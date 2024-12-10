# test_gpt_manager.py
import unittest
from unittest.mock import AsyncMock, patch
from pathlib import Path
import aiofiles
import asyncio
import sys
from gpt_manager import GPTManager

class TestGPTManager(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.gpt_manager = GPTManager()
        self.prompt = "A futuristic cityscape with flying cars and neon lights."
        self.text = "Hello, how are you?"

    @patch('gpt_manager.AsyncOpenAI')
    @patch('aiohttp.ClientSession.get')
    async def test_create_dalle_image(self, mock_get, mock_openai):
        # Mock the OpenAI client
        mock_openai.return_value.images.generate = AsyncMock(return_value=AsyncMock(data=[{'url': 'http://example.com/image.png'}]))

        # Mock the aiohttp response
        mock_response = AsyncMock()
        mock_response.read.return_value = b'fake_image_data'
        mock_get.return_value.__aenter__.return_value = mock_response

        # Run the create_dalle_image function
        image_path = await self.gpt_manager.create_dalle_image(self.prompt)

        # Check if the image path is correct
        expected_path = Path(__file__).parent / "used_files" / "img.png"
        self.assertEqual(image_path, expected_path)

    @patch('gpt_manager.AsyncOpenAI')
    async def test_generate_response(self, mock_openai):
        # Mock the OpenAI client
        mock_openai.return_value.chat.completions.create = AsyncMock(return_value=AsyncMock(choices=[AsyncMock(message=AsyncMock(content="Mocked response"))], usage=AsyncMock(prompt_tokens=10, completion_tokens=20)))

        # Run the generate_response function
        response = await self.gpt_manager.generate_response([{'role': 'user', 'content': self.text}])

        # Check if the response is correct
        self.assertEqual(response, "Mocked response")

    @patch('gpt_manager.AsyncOpenAI')
    async def test_speak(self, mock_openai):
        # Mock the OpenAI client
        mock_openai.return_value.audio.speech.create = AsyncMock(return_value=AsyncMock(content=b'fake_audio_data'))

        # Run the speak function
        await self.gpt_manager.speak(self.text)

        # Check if the audio file was created
        speech_file_path = Path(__file__).parent / "used_files" / "speech.mp3"
        async with aiofiles.open(speech_file_path, "rb") as f:
            content = await f.read()
            self.assertEqual(content, b'fake_audio_data')

    @patch('gpt_manager.AsyncOpenAI')
    async def test_speech_to_text(self, mock_openai):
        # Mock the OpenAI client
        mock_openai.return_value.audio.transcriptions.create = AsyncMock(return_value=AsyncMock(text="Mocked transcription"))

        # Run the speech_to_text function
        transcription = await self.gpt_manager.speech_to_text("fake_audio_path")

        # Check if the transcription is correct
        self.assertEqual(transcription, "Mocked transcription")

if __name__ == '__main__':
    # Determine which tests to run based on command-line arguments
    test_api = sys.argv[1] if len(sys.argv) > 1 else None

    suite = unittest.TestSuite()

    if test_api == "dalle" or test_api is None:
        suite.addTest(TestGPTManager('test_create_dalle_image'))
    if test_api == "chat" or test_api is None:
        suite.addTest(TestGPTManager('test_generate_response'))
    if test_api == "tts" or test_api is None:
        suite.addTest(TestGPTManager('test_speak'))
    if test_api == "whisper" or test_api is None:
        suite.addTest(TestGPTManager('test_speech_to_text'))

    runner = unittest.TextTestRunner()
    runner.run(suite)