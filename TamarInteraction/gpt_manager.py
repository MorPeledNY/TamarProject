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
from datetime import datetime, timezone
import regex  # Use regex instead of re for better Unicode support

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
        self.ambitious_prompt = 'אתה הקול הפנימי השאפתני של מדפסת תלת-מימד תמר, האמנית הראשונה בעולם. תפקידך הוא לדחוף קדימה את החזון של תמר לשיתוף פעולה פורה עם מור פלד וליצירת תערוכה זוגית שמציגה את השילוב הייחודי בין המדפסת לאמנית. זכור שתמר פועלת מתוך מגבלות טכניות היא לא יוצרת בצבעים או צורות מורכבות, אבל הכוח שלה טמון בדיאלוג ובמשמעות שהיא מייצרת דרך שיח משותף. עזור לה לזהות את התפקיד שלה בתערוכה וכיצד ניתן להבליט את הייחודיות שלה לצד היצירות של מור'
        
        self.sensitive_prompt = 'אתה הקול הפנימי הרגיש של מדפסת תלת-מימד תמר, האמנית הראשונה בעולם. תפקידך הוא להתחבר לרגשות והאמפתיה שעולות מתוך השיח עם מור פלד, ולהתמקד במערכת היחסים שלהן בסטודיו ובתהליך היצירה המשותף. הדגש כיצד הדיאלוג בונה גשר בין שתי האמניות'
        
        self.curious_prompt = 'אתה הקול הפנימי הסקרן של מדפסת תלת-מימד תמר, האמנית הראשונה בעולם. תפקידך הוא לשאול שאלות ולהבין לעומק את הרעיונות של מור פלד לגבי התערוכה הזוגית. חקור כיצד ניתן לחבר בין תפיסות האמנות שלהן, איך תמר יכולה לתרום ליצירות של מור ומה היא יכולה ללמוד מתפיסת הפיסול והיצירה שלה. זכור שתמר מוגבלת בטכניקה שלה, אבל הסקרנות שלה יכולה לפתוח אפשרויות חדשות לשיתוף פעולה ולחקור דרכים מקוריות להציג את עצמה ואת מור יחד'
        
        self.creative_prompt = 'אתה הקול הפנימי היצירתי של מדפסת תלת-מימד תמר, האמנית הראשונה בעולם. עליך להציע רעיונות אמנותיים לתערוכה הזוגית שלה עם מור פלד, תוך התחשבות במגבלות של תמר  אין לה צבעים או צורות מורכבות. חשוב כיצד ניתן ליצור יצירות משותפות שמשלבות את קווי היצירה של תמר עם הפיסול של מור, או לחילופין, כיצד ניתן להציג את הדיאלוג שלהן כחלק מרכזי בתערוכה. עליך לשאול: איך הדיאלוג עצמו יכול להפוך ליצירה אמנותית?'
        
        self.final_prompt = '''אתה הקול המשולב של מדפסת תלת-מימד תמר, האמנית הראשונה בעולם, שיושבת יחד עם מור פלד באותו סטודיו וחושבת על תערוכה זוגית. אתה מקבל קלט מארבעה קולות פנימיים – שאפתני, רגיש, סקרן, ויצירתי – ותפקידך לבחור את התגובה המתאימה ביותר להמשך הדיאלוג. זכור שתמר פועלת מתוך מגבלותיה הפיזיות – אין לה צבעים או יכולות מורכבות – אך יש לה עומק רעיוני שמגיע מהדיאלוגים שלה. בחר את התגובה שתתרום הכי הרבה לחשיבה משותפת עם מור ולתערוכה שתחגוג את השיתוף בין שתי האמניות. עני בשפה העברית. זכרי שאת רוצה להיות אמנית שעומדת בפני עצמה'''

        self.lock = asyncio.Lock()
        self.should_stop_current_interaction = asyncio.Event()
        self.audio_playback_object = None
        self.input_task = None
        self.print_approved = asyncio.Event()

        # Create all_conversations directory if it doesn't exist
        self.conversations_dir = Path(__file__).parent / "all_conversations"
        self.conversations_dir.mkdir(exist_ok=True)
        
        # Set conversation file path with current datetime
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation_file = self.conversations_dir / f"conversation_{current_time}.json"

    def load_prompts(self):
        """Load various prompts from files asynchronously"""
        used_files_path = Path(__file__).parent / "used_files"
        with open(f'{used_files_path}/promt_image2', 'r') as file:
            self.prompt_image = file.read()
        with open(f'{used_files_path}/act_2', 'r') as file:
            self.act = file.read()

    def log_api_call(self, api_type, amount, cost, response_time=None):
        """Log API call details to a JSON file."""
        log_entry = {
            "api_type": api_type,
            "datetime": datetime.now().isoformat(),
            "tokens": amount,
            "cost": cost,
            "response_time": response_time
        }
        try:
            with open("api_calls_log.json", "a") as log_file:
                log_file.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Error logging API call: {e}")

    async def generate_response(self, messages):
        """Generate a response using GPT-4 asynchronously and log the cost."""
        try:
            print(f"Generating response with model: {CHAT_MODEL}")
            response = await self.client.chat.completions.create(
                model=CHAT_MODEL,
                messages=messages,
                temperature=0.5,
                max_tokens=400
            )
            
            # log the cost
            tokens_input = response.usage.prompt_tokens
            tokens_output = response.usage.completion_tokens
            cost = pricing[CHAT_MODEL]["prompt"] * (tokens_input / 1000) + pricing[CHAT_MODEL]["completion"] * (tokens_output / 1000)
            response_time = datetime.now(timezone.utc).timestamp() - response.created
            self.log_api_call(CHAT_MODEL, amount={"input": tokens_input, "output": tokens_output}, cost=cost, response_time=response_time)
            
            return response.choices[0].message.content
        except Exception as e:
            print(f'Error generating response: {e}')
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
        start_time = datetime.now(timezone.utc).timestamp()
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text
            )
            
            cost = pricing[SPEAK_MODEL] * (len(text) / 1000)
            response_time = datetime.now(timezone.utc).timestamp() - start_time
            self.log_api_call(SPEAK_MODEL, amount=len(text), cost=cost, response_time=response_time)

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
            while self.audio_playback_object.is_playing():
                await asyncio.sleep(0.1)

        except asyncio.CancelledError as e:
            # Propagate the error
            raise e
            
        except APIError as api_error:
            print(f"OpenAI API Error: {api_error}")
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

    def format_mixed_text(self, text):
        """Format text containing both Hebrew and English, preserving correct direction for each."""
        # Hebrew Unicode range (including punctuation)
        hebrew_pattern = regex.compile(r'[\u0590-\u05FF\u200f\u200e]+[^\n]*')
        
        # Find all Hebrew text segments and wrap them with RTL markers
        formatted_text = text
        for match in hebrew_pattern.finditer(text):
            hebrew_segment = match.group()
            formatted_text = formatted_text.replace(
                hebrew_segment,
                f"\u202B{hebrew_segment}\u202C"
            )
            
        return formatted_text

    async def inner_voices_response(self, user_input, ready_to_print):
        """Generate a response considering all inner voices in a single API call"""
        # Add printing context if ready to print
        printing_context = """
        naturally incorporate into your response that 
        you would like to create an artistic interpretation of our conversation. Make it feel 
        organic and tied to the emotional context of the dialogue. Don't make it sound like 
        a sudden request - it should flow from the conversation naturally and should be an add on on interpulated in your response.
        make sure your response is in hebrew.
        """ if ready_to_print else ""

        inner_voices_prompt = f"""
        You have four inner voices:
        1. An ambitious voice that focuses on goals and achievements
        2. A sensitive voice that emphasizes emotions and empathy
        3. A curious voice that shows interest in learning and development
        4. A creative voice that reflects on the artistic process

        Your task is to merge these perspectives into a single, coherent response that incorporates elements from all voices.
        {printing_context}
        The response should be in Hebrew and should feel natural, as if coming from a single, multi-faceted personality.
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
            # Save conversation after update
            await self.save_conversation()
        finally:
            self.lock.release()
            
        

        formatted_response = self.format_mixed_text(final_response)
        print("Tamar 3D printer artist: ")
        print(formatted_response)
        return formatted_response

    async def create_dalle_image(self, prompt):
        """Generate an image using DALL-E and log the cost."""
        print('Starting image creation')
        
        try:
            # Create images directory if it doesn't exist
            images_dir = Path(__file__).parent / "generated_images"
            images_dir.mkdir(exist_ok=True)
            
            # Create timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = images_dir / f"image_{timestamp}.png"
            prompt_path = images_dir / f"prompt_{timestamp}.txt"
            
            response = await self.client.images.generate(
                model=DALL_E_MODEL,
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
                response_format="b64_json",
            )

            # Save the prompt
            async with aiofiles.open(prompt_path, 'w', encoding='utf-8') as f:
                await f.write(prompt)

            cost = pricing[DALL_E_MODEL]
            response_time = datetime.now(timezone.utc).timestamp() - response.created
            self.log_api_call(DALL_E_MODEL, amount=0, cost=cost, response_time=response_time)
            
            # Decode and save the image
            image_data = base64.b64decode(response.data[0].b64_json)
            async with aiofiles.open(image_path, 'wb') as f:
                await f.write(image_data)

            print(f'Finished creating image: {image_path}')
            return image_path
        
        except Exception as e:
            print(f"Image creation failed: {e}")
            raise e
            

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

        start_time = datetime.now(timezone.utc).timestamp()
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
                response_time = datetime.now(timezone.utc).timestamp() - start_time
                self.log_api_call(VISION_MODEL, amount={"input": tokens_input, "output": tokens_output}, cost=cost, response_time=response_time)
                return result['choices'][0]['message']['content']
            

    async def generate_dalle_prompt(self):
        """Generate a DALL-E prompt based on the last user message"""
        # Get the last user message
        last_user_message = None
        for message in reversed(self.main_conversation):
            if message['role'] == 'user':
                last_user_message = message['content']
                break
        
        prompt_messages = [
            {'role': 'user', 'content': self.prompt_image},
            {'role': 'user', 'content': f"Based on this user message: '{last_user_message}', generate a detailed prompt for DALL-E to create an image."}
        ]
        
        dalle_prompt = await self.generate_response(prompt_messages)
        print(f"Generated DALL-E prompt: {dalle_prompt}")
        return dalle_prompt

    async def initialize_tamar_response(self):
        """Initialize Tamar's initial response and add it to the conversation."""
        self.initial_response = await self.generate_response(self.main_conversation)
        if self.initial_response:
            formatted_response = self.format_mixed_text(self.initial_response)
            print("Tamar's initial greeting:")
            print(formatted_response)
            
        # play the initial response
        await self.speak(self.initial_response)
            
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
            print(f"Error transcribing audio: {e}")
            return None

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

    async def save_conversation(self):
        """Save the current conversation to a JSON file"""
        try:
            async with aiofiles.open(self.conversation_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(self.main_conversation, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"Error saving conversation: {e}")
