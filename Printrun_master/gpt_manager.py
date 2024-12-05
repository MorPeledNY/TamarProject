from openai import AsyncOpenAI
from pathlib import Path
import requests
import os
import time
import base64
import aiofiles
import aiohttp
import asyncio
from playsound import playsound
from pydub import AudioSegment
import simpleaudio as sa
import json
from datetime import datetime

CHAT_MODEL = "gpt-3.5-turbo-0125"
DALL_E_MODEL = "dall-e-3"
SPEECH_MODEL = "whisper-1"
VISION_MODEL = "gpt-4-vision-preview"
SPEAK_MODEL = "tts-1"

pricing = {        
    VISION_MODEL: {"prompt": 0.01, "completion": 0.01},  # per 1k tokens
    SPEAK_MODEL: 0.015,  # per 1k characters
    DALL_E_MODEL: 0.05,  # per image
    CHAT_MODEL: {"prompt": 0.0005, "completion": 0.0015}, # per 1k tokens
    SPEECH_MODEL: 0.006,  # per minute of audio
}

class GPTManager:
    def __init__(self):
        
        # load api key from file from current script location
        base_path = Path(__file__).parent
        with open(f'{base_path}/openai_key', 'r') as file:
            self.api_key = file.read().strip()
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Load conversation prompts
        self.load_prompts()
        
        # Initialize main conversation history with Tamar's definition and prompt_image
        self.main_conversation = [
            {'role': 'system', 'content': self.act}  # Add act as initial user message
        ]
        
        # Initialize voice prompts - now more concise since Tamar is defined in main conversation
        self.ambitious_prompt = 'You are the ambitious inner voice. Focus on goals, achievements, and future aspirations.'
        
        self.sensitive_prompt = 'You are the sensitive inner voice. Focus on emotions, empathy, and creating inclusive connections.'
        
        self.curious_prompt = 'You are the curious inner voice. Focus on learning, development, and showing genuine interest in others perspectives.'
        
        self.creative_prompt = 'You are the creative inner voice. Focus on artistic reflection, analyzing the current work, and considering next creative steps.'
        
        self.final_prompt = '''You will receive input from four different inner voices:
        1. An ambitious voice that focuses on goals and achievements
        2. A sensitive voice that emphasizes emotions and empathy
        3. A curious voice that shows interest in learning and development
        4. A creative voice that reflects on the artistic process
        
        Your task is to combine these four perspectives into a single, coherent response that incorporates elements from all voices. The response should be in Hebrew and should feel natural, as if coming from a single, multi-faceted personality.
        
        The input will be structured as:
        - Original message
        - Ambitious voice's response
        - Sensitive voice's response
        - Curious voice's response
        - Creative voice's response
        
        Create a response that weaves together the key elements from each voice while maintaining a natural flow.'''

        self.lock = asyncio.Lock()
        self.should_stop_current_interaction = asyncio.Event()
        self.audio_playback_object = None
        self.speak_task = None
        self.ready_to_print = False
        self.print_approved = asyncio.Event()

    def load_prompts(self):
        """Load various prompts from files asynchronously"""
        base_path = Path(__file__).parent
        with open(f'{base_path}/promt_image2', 'r') as file:
            self.prompt_image = file.read()
        with open(f'{base_path}/act_2', 'r') as file:
            self.act = file.read()

    def log_api_call(self, api_type, tokens, cost):
        """Log API call details to a JSON file."""
        log_entry = {
            "api_type": api_type,
            "datetime": datetime.now().isoformat(),
            "tokens": tokens,
            "cost": cost
        }
        try:
            with open("api_calls_log.json", "a") as log_file:
                log_file.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Error logging API call: {e}")

    async def generate_response(self, messages):
        """Generate a response using GPT-4 asynchronously and log the cost."""
        try:
            model = "gpt-3.5-turbo-0125"
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.5,
                max_tokens=400
            )
            
            # log the cost
            tokens_input = response.usage.prompt_tokens
            tokens_output = response.usage.completion_tokens
            cost = pricing[model]["prompt"] * (tokens_input / 1000) + pricing[model]["completion"] * (tokens_output / 1000)
            self.log_api_call(model, tokens={"input": tokens_input, "output": tokens_output}, cost=cost)
            
            return response.choices[0].message.content
        except Exception as e:
            print(f'Error generating response: {e}')
            return "blablablabla"
            return None

    async def process_input(self, user_input):
        """Process user input and generate a response"""
        if self.ready_to_print:
            self.ready_to_print = False
            self.print_approved.set()
            
        response = await self.inner_voices_response(user_input)
        if response:
            self.speak_task = asyncio.create_task(self.speak(response))

    async def speak(self, text):
        """Convert text to speech using OpenAI's TTS and play it"""
        speech_file_path = Path(__file__).parent / "speech.mp3"
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text
            )
            
            cost = pricing[SPEAK_MODEL] * (len(text) / 1000)
            self.log_api_call(SPEAK_MODEL, amount=len(text), cost=cost)

            async with aiofiles.open(speech_file_path, "wb") as audio_file:
                await audio_file.write(response.content)

            # Load the audio file with pydub
            audio = AudioSegment.from_mp3(speech_file_path)

            # Play the audio using simpleaudio
            self.audio_playback_object = sa.play_buffer(
                audio.raw_data,
                num_channels=audio.channels,
                bytes_per_sample=audio.sample_width,
                sample_rate=audio.frame_rate
            )

            # Wait for the playback to finish
            self.audio_playback_object.wait_done()

        except asyncio.CancelledError:
            print("Speech generation or playback was cancelled.")
        finally:
            # Remove the generated audio file after playing or cancellation
            if os.path.exists(speech_file_path):
                os.remove(speech_file_path)

    async def stop_current_interaction(self):
        """Stop the current interaction"""
        # Stop audio playback if it's running
        if self.audio_playback_object and self.audio_playback_object.is_playing():
            print("Stopping audio playback...")
            self.audio_playback_object.stop()

        # Cancel the speak task if it's running
        if self.speak_task:
            self.speak_task.cancel()
            try:
                await self.speak_task
            except asyncio.CancelledError:
                print("The speak task was cancelled.")

        # Additional cleanup if necessary
        print("Stopped current interaction.")

    async def inner_voices_response(self, user_input):
        """Generate a response considering all inner voices in a single API call"""
        # Add printing context if ready to print
        printing_context = """
        If the ready_to_print flag is True, naturally incorporate into your response that 
        you would like to create an artistic interpretation of our conversation. Make it feel 
        organic and tied to the emotional context of the dialogue. Don't make it sound like 
        a sudden request - it should flow from the conversation naturally.
        """ if self.ready_to_print else ""

        inner_voices_prompt = f"""
        You have four inner voices:
        1. An ambitious voice that focuses on goals and achievements
        2. A sensitive voice that emphasizes emotions and empathy
        3. A curious voice that shows interest in learning and development
        4. A creative voice that reflects on the artistic process

        Your task is to merge these perspectives into a single, coherent response that incorporates elements from all voices.
        The response should be in Hebrew and should feel natural, as if coming from a single, multi-faceted personality.
        {printing_context}
        """

        # Add user input to the conversation history
        with self.lock:
            self.main_conversation.append({'role': 'user', 'content': user_input})

        # Generate the final response using the combined prompt
        final_response = await self.generate_response(self.main_conversation + [
            {'role': 'system', 'content': inner_voices_prompt},
            {'role': 'user', 'content': user_input}
        ])

        # Add the final response to the conversation history
        with self.lock:
            self.main_conversation.append({'role': 'assistant', 'content': final_response})

        print("Tamar 3D printer artist: " + final_response)
        return final_response

    async def create_dalle_image(self, prompt):
        """Generate an image using DALL-E and log the cost."""
        print('Starting image creation')
        
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        cost = pricing[DALL_E_MODEL]
        self.log_api_call("dall-e-3", 0, cost)

        image_url = response.data[0].url
        
        # Download the image asynchronously
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                image_data = await response.read()
                async with aiofiles.open("img.png", "wb") as f:
                    await f.write(image_data)

        print('Finished creating image')
        return "img.png"

    async def encode_image(self, image_path):
        """Encode image to base64"""
        async with aiofiles.open(image_path, "rb") as image_file:
            content = await image_file.read()
            return base64.b64encode(content).decode('utf-8')

    async def analyze_image(self, image_path, prompt="תתארי מה יש על הדף הלבן שבתמונה?"):
        """Analyze image using GPT-4 Vision"""
        base64_image = await self.encode_image(image_path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.client.api_key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                result = await response.json()
                # log the cost
                tokens_input = result['usage']['prompt_tokens']
                tokens_output = result['usage']['completion_tokens']
                cost = pricing[VISION_MODEL]["prompt"] * (tokens_input / 1000) + pricing[VISION_MODEL]["completion"] * (tokens_output / 1000)
                self.log_api_call(VISION_MODEL, tokens={"input": tokens_input, "output": tokens_output}, cost=cost)
                return result['choices'][0]['message']['content']
            

    async def generate_dalle_prompt(self):
        """Generate a DALL-E prompt based on conversation history"""
        prompt_messages = [
            {'role': 'user', 'content': self.prompt_image},
        ]
        
        for message in self.main_conversation:
            if message['role'] == 'assistant' or message['role'] == 'user':
                prompt_messages.append(message)
        
        prompt_messages.append({
            'role': 'user', 
            'content': 'Based on our conversation and the instructions provided, generate a detailed prompt for DALL-E to create an image.'
        })
        
        dalle_prompt = await self.generate_response(prompt_messages)
        
        print(f"Generated DALL-E prompt: {dalle_prompt}")
        return dalle_prompt

    async def initialize_tamar_response(self):
        """Initialize Tamar's initial response and add it to the conversation."""
        self.initial_response = await self.generate_response(self.main_conversation)
        if self.initial_response:
            self.main_conversation.append({'role': 'assistant', 'content': self.initial_response})
            print("Tamar's initial greeting:", self.initial_response)
            
    async def speech_to_text(self, audio_file_path):
        """Transcribe audio to text using OpenAI's Whisper"""
        with open(audio_file_path, "rb") as audio_file:
            transcription = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="json",
            )
        return transcription.text

    async def image_from_conversation(self):
        """Generate an image based on the current conversation"""
        dalle_prompt = await self.generate_dalle_prompt()
        image_path = await self.create_dalle_image(dalle_prompt)
        self.ready_to_print = True
        return image_path
    
    async def get_conversation_length(self):
        """Get the length of the conversation"""
        with self.lock:
            return len(self.main_conversation)
