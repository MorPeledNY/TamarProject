import asyncio
from gpt_manager import GPTManager
from audio_input_manager import AudioInputManager
from button_interface import ButtonInterface, SocketButton, GPIOButton
from printer_manager import Printer, SimulatedPrinter, RealPrinter, ServerPrinter

async def is_ready_to_print(printer: Printer, gpt_manager: GPTManager):
    global last_conversation_length
    conversation_threshold = 1  # Number of exchanges before considering printing
    return not printer.print_in_progress and await gpt_manager.get_conversation_length() >= conversation_threshold * 2 + 1

async def main():
    # Initialize managers
    gpt_manager = GPTManager()
    await gpt_manager.initialize_tamar_response()
    audio_input_manager = AudioInputManager()
    printer = ServerPrinter()
    await printer.connect()
    print_approved = asyncio.Event()  # Create print_approved event
    
    # Keep track of the last conversation length
    global last_conversation_length
    last_conversation_length = 0
    
    tasks = [
        asyncio.create_task(audio_input_manager.run()),
        asyncio.create_task(handle_conversations(gpt_manager, audio_input_manager, printer, print_approved)),  # Pass print_approved
        asyncio.create_task(handle_printing(gpt_manager, printer, print_approved))  # Pass print_approved
    ]

    await asyncio.gather(*tasks)

async def handle_conversations(gpt_manager: GPTManager, audio_input_manager: AudioInputManager, printer: Printer, print_approved: asyncio.Event):
    while True:
        # Wait for recording to start and stop any ongoing GPT tasks
        await audio_input_manager.recording_started.wait()
        audio_input_manager.recording_started.clear()
        await gpt_manager.stop_current_interaction()

        # Wait for new input to be available
        await audio_input_manager.new_input_available.wait()
        audio_input_manager.new_input_available.clear()

        # Process the new user input
        user_input = await gpt_manager.speech_to_text(audio_input_manager.latest_user_input_path)
        await gpt_manager.create_input_task(user_input, await is_ready_to_print(printer, gpt_manager))

        # Emit print_approved event if printer is not busy
        if await is_ready_to_print(printer, gpt_manager):
            print_approved.set()

async def handle_printing(gpt_manager: GPTManager, printer: Printer, print_approved: asyncio.Event):
    """Handle the printing process based on conversation"""    
    while True:
        # Wait until the printer is ready to print
        if await is_ready_to_print(printer, gpt_manager):
            # Generate image from conversation
            image_path = await gpt_manager.image_from_conversation()
        else:
            await asyncio.sleep(0.5)
            continue
            
        # Wait approval for the print to start
        await print_approved.wait()
        print_approved.clear()
        
        # Start printing
        await printer.print_image(image_path)
        
        await asyncio.sleep(1)  # Check conditions every second

if __name__ == "__main__":
    asyncio.run(main()) 