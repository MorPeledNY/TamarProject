import asyncio
from gpt_manager import GPTManager
from audio_input_manager import AudioInputManager
from printer_manager import RealPrinter

async def main():
    # Initialize managers
    print("Initializing managers...")
    gpt_manager = GPTManager()
    audio_input_manager = AudioInputManager()
    printer = RealPrinter()
    
    # Initialize Tamar and start printer
    # await gpt_manager.initialize_tamar_response()
    await asyncio.sleep(1)
    await printer.start()
    print("All managers initialized")

    # Start parallel tasks
    tasks = [
        asyncio.create_task(audio_input_manager.run()),
        asyncio.create_task(gpt_interaction(gpt_manager, audio_input_manager, printer))
    ]

    await asyncio.gather(*tasks)

async def gpt_interaction(gpt_manager: GPTManager, audio_input_manager: AudioInputManager, printer: RealPrinter):
    while True:
        # Wait for recording to start
        await audio_input_manager.recording_started.wait()
        audio_input_manager.recording_started.clear()

        # Stop all background tasks and tell printer to stop
        await gpt_manager.stop_current_interaction()
        await printer.stop_all(keep_heat=True)  # Keep printer heated

        # Wait for recording to finish
        await audio_input_manager.new_input_available.wait()
        audio_input_manager.new_input_available.clear()

        # Tell printer to start "thinking" movement
        thinking_task = asyncio.create_task(printer.start_thinking())

        # Convert speech to text with error handling
        try:
            user_input = await asyncio.wait_for(
                gpt_manager.speech_to_text(audio_input_manager.latest_user_input_path),
                timeout=30  # timeout after 30 seconds
            )
        except asyncio.TimeoutError:
            print("Speech to text conversion timed out")
            await printer.stop_all(keep_heat=True)
            continue
        except Exception as e:
            print(f"Error in speech to text conversion: {e}")
            await printer.stop_all(keep_heat=True)
            continue

        # Start parallel processing tasks
        image_task = asyncio.create_task(handle_image_generation(gpt_manager, printer))
        text_task = asyncio.create_task(gpt_manager.create_input_task(user_input, False))
        
        # Wait for all tasks to complete
        await asyncio.gather(image_task, text_task, thinking_task)

async def handle_image_generation(gpt_manager: GPTManager, printer: RealPrinter):
    try:
        # Generate image from conversation
        image_path = await gpt_manager.image_from_conversation()
        if image_path:  # Only if image was successfully generated
            # Stop thinking movement but keep printer heated
            await printer.stop_all(keep_heat=True)
            # Start printing the generated image
            await printer.print_image(image_path)
    except Exception as e:
        print(f"Error in image generation/printing: {e}")

if __name__ == "__main__":
    print("Starting TamarInteraction...")
    asyncio.run(main())