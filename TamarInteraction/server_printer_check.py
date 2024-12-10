import asyncio
from printer_manager import ServerPrinter
from pathlib import Path
async def main():
    # Initialize the ServerPrinter with default hostname and port
    printer = ServerPrinter()

    # Connect to the server
    await printer.connect()

    # Print the image from the specified path
    used_files_path = Path(__file__).parent / "used_files"
    image_path = used_files_path / "img.png"
    await printer.print_image(image_path)

if __name__ == '__main__':
    asyncio.run(main()) 