import asyncio
from TamarInteraction.printer_manager import ServerPrinter

async def main():
    # Initialize the ServerPrinter with default hostname and port
    printer = ServerPrinter()

    # Connect to the server
    await printer.connect()

    # Print the image from the specified path
    image_path = '/used_files/img.png'
    await printer.print_image(image_path)

if __name__ == '__main__':
    asyncio.run(main()) 