from openai import AsyncOpenAI, APIError
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
        self.input_task = None
        self.print_approved = asyncio.Event()

    def load_prompts(self):
        """Load various prompts from files asynchronously"""
        used_files_path = Path(__file__).parent / "used_files"
        with open(f'{used_files_path}/promt_image2', 'r') as file:
            self.prompt_image = file.read()
        with open(f'{used_files_path}/act_2', 'r') as file:
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
            # print(f'Error generating response: {e}')
            await asyncio.sleep(3)
            return "blablablabla"
            return None

    async def create_input_task(self, user_input, ready_to_print):
        """Start a task to process user input"""
        self.input_task = asyncio.create_task(self.process_input_task(user_input, ready_to_print))
            
    async def process_input_task(self, user_input, ready_to_print):
        """Process user input and generate a response"""
        try:
            response = await self.inner_voices_response(user_input, ready_to_print)
            if response:
                await self.speak(response)
                
        except asyncio.CancelledError as e:
            print(f"Input task cancelled: {e}")
            
        except Exception as e:
            # Stop the audio playback
            print(f"Other error in speech generation/playback: {e}")
            await self.stop_current_interaction()

    async def speak(self, text):
        """Convert text to speech using OpenAI's TTS and play it"""
        speech_file_path = Path(__file__).parent / "used_files" / "speech.mp3"
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

        except asyncio.CancelledError as e:
            # Propagate the error
            raise e
            
        except APIError as api_error:
            # print(f"OpenAI API Error: {api_error}")
            # Play haha.mp3 on API error
            error_audio_path = Path(__file__).parent / "used_files" / "haha.mp3"
            if os.path.exists(error_audio_path):
                error_audio = AudioSegment.from_mp3(error_audio_path)
                self.audio_playback_object = sa.play_buffer(
                    error_audio.raw_data,
                    num_channels=error_audio.channels, 
                    bytes_per_sample=error_audio.sample_width,
                    sample_rate=error_audio.frame_rate
                )
                self.audio_playback_object.wait_done()
        except Exception as e:
            raise e
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
        if self.input_task:
            self.input_task.cancel()

        # Additional cleanup if necessary
        print("Stopped current interaction.")

    async def inner_voices_response(self, user_input, ready_to_print):
        """Generate a response considering all inner voices in a single API call"""
        # Add printing context if ready to print
        printing_context = """
        naturally incorporate into your response that 
        you would like to create an artistic interpretation of our conversation. Make it feel 
        organic and tied to the emotional context of the dialogue. Don't make it sound like 
        a sudden request - it should flow from the conversation naturally.
        """ if ready_to_print else ""

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
        await self.lock.acquire()
        try:
            self.main_conversation.append({'role': 'user', 'content': user_input})
        finally:
            self.lock.release()

        # Generate the final response using the combined prompt
        final_response = await self.generate_response(self.main_conversation + [
            {'role': 'system', 'content': inner_voices_prompt},
            {'role': 'user', 'content': user_input}
        ])

        # Add the final response to the conversation history
        await self.lock.acquire()
        try:
            self.main_conversation.append({'role': 'assistant', 'content': final_response})
        finally:
            self.lock.release()

        print("Tamar 3D printer artist: " + final_response)
        return final_response

    async def create_dalle_image(self, prompt):
        """Generate an image using DALL-E and log the cost."""
        print('Starting image creation')
        
        try:
            image_path = Path(__file__).parent / "used_files" / "img.png"
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
                    async with aiofiles.open(image_path, "wb") as f:
                        await f.write(image_data)

            print('Finished creating image')
            return image_path
        
        except Exception as e:
            # print(f"Image creation failed: {e}")
            # Use fallback image
            return image_path

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
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcription = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="json",
                )
            return transcription.text
        except Exception as e:
            # print(f"Error transcribing audio: {e}")
            return "blablablabla2"

    async def image_from_conversation(self):
        """Generate an image based on the current conversation"""
        dalle_prompt = await self.generate_dalle_prompt()
        image_path = await self.create_dalle_image(dalle_prompt)
        return image_path
    
    async def get_conversation_length(self):
        """Get the length of the conversation"""
        await self.lock.acquire()
        try:
            return len(self.main_conversation)
        finally:
            self.lock.release()
