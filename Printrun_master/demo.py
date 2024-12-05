import datetime
from openai import OpenAI
from pathlib import Path
import base64
import requests
from pathlib import Path
from playsound import playsound

import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
import time
import signal
import cvzone
import datetime as dt
import numpy as np
import random
import os
from playsound import playsound
import whisper
import text2emotion as te
import pyaudio
import wave
import speech_recognition as sr
import pyttsx3
import threading
import re
from printrun.printcore import printcore
from printrun import gcoder
import serial
import queue



is_pressed = False
upcamera = cv2.VideoCapture(1)

last_capture_time = time.time()  # Track the last capture time
capture_interval = 60  # Time in seconds (1 minute)

client = OpenAI()
gcode_queue = queue.Queue()

# model = whisper.load_model("medium")
model = whisper.load_model("base")
engine = pyttsx3.init()
all_voices = engine.getProperty('voices')
engine.setProperty('voice', all_voices[1].id)
engine.setProperty('volume', 1.0)
engine.setProperty('rate', 150)
t = dt.datetime.now()
exstrod = -5
ser = serial.Serial('COM8', 9600) # Replace 'COM3' with the port name of your Arduino
time.sleep(2)
command = "sample"



with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\promt_image2', 'r') as file:
   promt_image = file.read().strip()

with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\act_2', 'r') as file:
   act = file.read().strip()

with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\first', 'r') as file:
   first_sentens = file.read().strip()

with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\replaydalley', 'r') as file:
   replay_promt = file.read().strip()

replay_dalley = [{'role': "system", 'content':replay_promt}]
shape_messages = [{'role': "system", 'content':promt_image}]
open_sentens = [{"role": "system", "content":first_sentens }]
main_act = [{"role": "system", "content":act},]


conversation1 = [{'role': 'system', 'content': ' I want you to act as The ambitious inner voice of Tamar, the world first 3D printer artist. You will get a sentence that Tamar says to the person opposite her in a conversation she is having with him. Dissect the simplistic and you will see that you need to add ambition to it so that Tamar looks like a printer with an ambitious nature.Put a new sentence in place of the existing sentence'}]
conversation2 = [{'role': 'system', 'content': ' I want you to act as The sensitive inner voice of Tamar, the world first 3D printer artist. The inner voice of Tamar, the worlds first 3D printer artist. You will get a sentence that Tamar says to a man in a conversation she has with him. Dissect the simplistic and you will see that you need to add emotion to it so that Tamar will appear to be a printer with a sensitive and inclusive character. Put a new sentence in place of the existing sentence'}]
conversation3 = [{'role': 'system', 'content': 'I want you to act the inner voice of Tamar, the world is first 3D printer artist. You will receive four separate sentences that Tamar can say in a conversation with another person, as well as a sentence describing the artistic work that Tamar creates during the dialogue. Your task is to choose one sentence that continues the conversation. answer in Hebrew'}]
conversation4 = [{'role': 'system', 'content': 'I want you to act as the curious inner voice of Tamar, the worlds first 3D printer artist. The inner voice of Tamar, the worlds first 3D printer artist. You will receive a sentence that Tamar says to a person in a conversation she has with him. Analyze the sentence and see that you need to add curiosity to it so that Tamar will be seen as a curious printer who wants to learn and develop in the world, therefore she is also interested in what the person in front of her thinks. Put a new sentence in place of the existing sentence'}]
art_voice = [{'role': 'system', 'content':'I want you to act as Tamar is creative voice. You will receive a sentence that describes the artwork you are creating. Transform this sentence into a reflection where you analyze your work, express your thoughts on it, and consider your next steps. Make sure the sentence flows naturally as part of a creative dialogue with the person you are speaking to. The machine in this picture is you. Therefore, Do not refer to the machine in your answer and talk about yourself in the first person. '}]
def generate_response(conversation1):
   response = client.chat.completions.create(model="gpt-4-1106-preview", messages=conversation1, temperature=0.5, max_tokens=400)
   return response.choices[0].message.content

def generate_response(art_voice):
   response = client.chat.completions.create(model="gpt-4-1106-preview", messages=art_voice, temperature=0.5, max_tokens=400)
   return response.choices[0].message.content


def generate_response2(conversation2):
   response2 = client.chat.completions.create(model="gpt-4-1106-preview", messages=conversation2, temperature=0.5, max_tokens=400)
   return response2.choices[0].message.content

def generate_response3(conversation3):
   response3 = client.chat.completions.create(model="gpt-4-1106-preview", messages=conversation3, temperature=0.5, max_tokens=400)
   return response3.choices[0].message.content

def generate_response4(conversation4):
   response4 = client.chat.completions.create(model="gpt-4-1106-preview", messages=conversation4, temperature=0.5, max_tokens=400)
   return response4.choices[0].message.content

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Conduct the dialogue
def inner_voices(reply, text_content):
   user_input = reply
   art_descripsion = text_content
   conversation1.append({'role': 'user', 'content': user_input})
   conversation2.append({'role': 'user', 'content': user_input})
   conversation4.append({'role': 'user', 'content': user_input})
   art_voice.append({'role': 'user', 'content': art_descripsion})

   x = random.randint(10, 80)
   y = random.randint(10, 80)
   send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])



   # Generate GPT response
   gpt_response = generate_response(conversation1)
   gpt_response2 = generate_response2(conversation2)
   gpt_response4 = generate_response2(conversation4)
   gpt_response5 = generate_response2(art_voice)

   x = random.randint(10, 80)
   y = random.randint(10, 80)
   send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])

   conversation1.append({'role': 'assistant', 'content': gpt_response})
   conversation2.append({'role': 'assistant', 'content': gpt_response2})
   conversation4.append({'role': 'assistant', 'content': gpt_response4})
   art_voice.append({'role': 'assistant', 'content': gpt_response5})

   x = random.randint(10, 80)
   y = random.randint(10, 80)
   send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])

   print("ambitious voice: " + gpt_response)
   print("sensitive voice: " + gpt_response2)
   print("curious voice: " + gpt_response4)
   print("creative voice: " + gpt_response5)


   conversation3.append({'role': 'user', 'content': user_input+ gpt_response +gpt_response2 +gpt_response4+gpt_response5})
   gpt_response3 = generate_response3(conversation3)
   conversation3.append({'role': 'user', 'content': gpt_response3})
   print("Tamar 3D printer artist: " + gpt_response3)

   x = random.randint(10, 80)
   y = random.randint(10, 80)
   send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])

   return gpt_response3


def send_commands(commands: list, wait=True):
    commands_gcode = gcoder.LightGCode(commands)
    p.startprint(commands_gcode)
    time.sleep(0.5)
    if wait:
        while print_in_progress:
            time.sleep(0.01)


def send_command(command: str):
    send_commands([command])


def end_callback():
    global print_in_progress
    print_in_progress = False


def start_callback(printer):
    global print_in_progress
    print_in_progress = True

def add_new_p(gcode_list: list):
    gcode_list.insert(0, "G91;")
    gcode_list.insert(1, f"G1 X1 Y0.15 F3000;")
    gcode_list.insert(2, "G1 Z0.5;")
    gcode_list.insert(3, "G90 ;Absolute positioning")
    gcode_list.insert(4, "G92 E0 X0 Y0 ; Reset Extruder")
    gcode_list.append("G1 X0 Y0")
    print(gcode_list[9])
    return gcode_list


def check_contact_stoped():
    global is_pressed
    is_pressed = False
    while True:
        # ser.write(command.encode())
        data = ser.readline().decode()
        try:
            data1 = int(data.rstrip())
            is_pressed = data1 > 500
        except:
            pass

def listen():
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1 # camera on printer mast to be conect
    fs = 44100
    seconds = 0.5
    filename = "output.wav"
    p1 = pyaudio.PyAudio()

    # search device index by name
    device_name = 'PnP'
    device_index = -1
    for i in range(p1.get_device_count()):
        info = p1.get_device_info_by_index(i)
        if device_name.lower() in info['name'].lower():
            device_index = i
            break
    if device_index == -1:
        raise Exception("could not find the 'PnP Microphone connected to the PC")
    print('Recording')
    stream = p1.open(format=sample_format,
                     channels=channels,
                     rate=fs,
                     frames_per_buffer=chunk,
                     input=True,
                     input_device_index=device_index)

    frames = []
    # Store data in chunks for 3 seconds
    send_commands(['M117 Listening'], False)
    while is_pressed:  # Continue recording while data1 is greater than 0
        print(is_pressed)
        for i in range(0, int(fs / chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p1.terminate()
    print('Finished recording')
    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p1.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    with open(filename, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="json",
        )
    # audio_file = open("C:\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\output.wav", "rb")

    transcribed_text = transcription.text
    print(transcribed_text)

    return transcribed_text

def signal_handler(signum, frame):
    print("exiting0")
    p.cancelprint()
    time.sleep(3)
    p.send("G92 E0")
    time.sleep(1)
    p.send("M107")
    time.sleep(1)
    p.send("M104 S0")
    time.sleep(1)
    p.send("G28 X0")
    time.sleep(1)
    p.send("M84")
    time.sleep(1)
    p.send("M140 S0")
    time.sleep(5)
    p.disconnect()
    exit()

def extract_gcode_with_brackets(reply : str):
    square_brackets = re.findall(r'\[[^\[\]]*?\]', reply)
    for bracket in square_brackets:
        drop_part = bracket
        if reply.find(f'GCODE: {bracket}') != -1:
            drop_part = f'GCODE: {bracket}'

        numbers_in_bracket = re.findall(r'\d+', bracket)
        for number_str in numbers_in_bracket:
            number = int(number_str)
            if number > 90:
                print(f"Replacing {number} with 90")
                # החלפת המספר ל-90 בתוך ה-GCode
                bracket = bracket.replace(str(number), '90')

        reply = reply.replace(drop_part, "")
        print(f"Gcode: {bracket}")
        return reply, bracket
    return reply, ""

def extract_gcode(reply : str):
    target_word = "G1"
    words = reply.split()
    if target_word in words:
        index = words.index(target_word)
        if len(words) > index + 2:  # Check if there are two words after target word
            word1 = words[index + 1]
            word2 = words[index + 2]
            gcode_command = f"{target_word} {word1} {word2} E{exstrod} "
            index = words.index(target_word)
            del words[index:index + 5]  # Remove target word and two words following it
            new_sentence = ' '.join(words)
            return  new_sentence, gcode_command
    else:
        x = random.randint(10, 80)
        y = random.randint(10, 80)
        random_gcode = f" G1 X{x} Y{y}"
        return reply, random_gcode

def gpt_interaction(gpt_messages : dict):

    # create the input to gpt
    while True:
        try:
            chat = client.chat.completions.create(model="gpt-4-1106-preview", messages=gpt_messages, temperature=0.5, max_tokens=1000)
            reply = chat.choices[0].message.content
            print(f"reply:{reply}")

            return reply
        except Exception as e:
            print(f'got an error of type: {e}. \n wating for 2 seconds and try again')
            time.sleep(2)


def speak(reply):
    ser.write("on".encode())
    time.sleep(1.0)
    engine.say(reply)
    engine.runAndWait()
    ser.write("off".encode())

def creat_image_in_delly():
     print('get the promt start creat image')

     x = random.randint(10, 80)
     y = random.randint(10, 80)
     send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])

     file_path = '\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\promt_to_delly'
     with open(file_path, 'r') as file:
         prompt = file.read().strip()

     response = client.images.generate(model="dall-e-3",prompt=prompt,size="1024x1024",quality="standard",n=1,)

     image_url = response.data[0].url
     #file_conversition2= open("\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\siha", "a")
     #print("\n"+ f"Tamar 3D printer:{image_url}",file=file_conversition2)
     #file_conversition2.close()

     url1 = image_url
     response = requests.get(url1)
     with open("img.png", "wb") as f:
       f.write(response.content)

     time.sleep(0.2)

     print('finish creat image')


def convert_image_to_gcode(image_path, output_gcode_path, scale_factor=0.75):
   print('Start converting image to G-code')

   def image_to_gcode(image_path, scale_factor=1.0):
       #Load the image in grayscale and threshold it
       image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
       _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

       # Find contours in the image
       contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

       gcode = []

       for contour in contours:
           # Scale the contour points
           contour = contour * scale_factor

           # Move to the starting point of the contour
           start_point = contour[0][0]
           gcode.append(f"G0 X{start_point[0]} Y{start_point[1]}")

           # Generate G1 commands to follow the contour
           for point in contour:
               x, y = point[0]
               gcode.append(f"G1 X{x} Y{y}")

       return gcode

   def save_gcode_to_file(gcode, file_path):
       large_list = gcode
       first_100_elements = large_list[1000:3000]
       with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image_gcode', 'w') as file:
           for line in first_100_elements:
               file.write(line + '\n')

   gcode = image_to_gcode(image_path, scale_factor)

   save_gcode_to_file(gcode, output_gcode_path)

   print('Saved new G-code to file:', output_gcode_path)


def convert_image_to_gcode2(image_path, output_gcode_path):
    print('Start converting image to G-code')

    def image_to_gcode(image_path, scale_factor):
        # Load the image in grayscale and threshold it
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Unable to find or open the image at {image_path}")

        _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

        # Find contours in the image
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        gcode = []

        for contour in contours:
            # Scale the contour points
            scaled_contour = contour * scale_factor

            # Move to the starting point of the contour
            start_point = scaled_contour[0][0]
            gcode.append(f"G0 X{start_point[0]} Y{start_point[1]}")

            # Generate G1 commands to follow the contour
            for point in scaled_contour:
                x, y = point[0]
                gcode.append(f"G1 X{x} Y{y}")

        return gcode


    # Define the scale factor based on the image and printer size
    image_width, image_height = 1024, 1024  # Image dimensions
    printer_width, printer_height = 90, 90  # Printer dimensions in mm

    # Calculate the scale factor
    # We use the larger dimension to ensure the scaled image fits within the print area
    scale_factor = min(printer_width / image_width, printer_height / image_height)

    # Generate G-code from the image
    gcode_list = image_to_gcode(image_path, scale_factor)

    large_list = gcode_list
    first_100_elements = large_list[1000:3000]
    with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image_gcode', 'w') as file:
        for line in first_100_elements:
            file.write(line + '\n')

    # Write the G-code to a file
    #with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image_gcode', 'w') as file:
        #for line in gcode_list:
            #file.write(f"{line}\n")



    print('G-code conversion completed.')


def crop_image(image, x_start, y_start, width, height):
    """
    חותך את התמונה לפי הקואורדינטות שנבחרו
    :param image: התמונה המתקבלת מהמצלמה
    :param x_start: נקודת התחלה אופקית
    :param y_start: נקודת התחלה אנכית
    :param width: רוחב החיתוך
    :param height: גובה החיתוך
    :return: התמונה החתוכה
    """
    cropped_image = image[y_start:y_start + height, x_start:x_start + width]
    return cropped_image



if __name__ == "__main__":
    print_in_progress = False
    p = printcore()
    p.connect('COM16', 115200, True)
    print("connecting...")
    p.startcb = start_callback
    p.endcb = end_callback
    time.sleep(2)
    signal.signal(signal.SIGINT, signal_handler)
    send_commands([i.strip() for i in open('preper_printer.txt')])
    print('התחמם נכנס לעבודה')
    #send_commands(['M117 connected', 'G28'])
    time.sleep(1)
    send_commands(['G1 Z1'])
    time.sleep(1)
    send_commands(['G92'])
    time.sleep(1)
    send_commands(['M201 X90'])
    time.sleep(1)
    send_commands(['G1 X20'])
    time.sleep(1)
    reply = gpt_interaction(open_sentens)
    #print(reply)
    reply, gcode = extract_gcode_with_brackets(reply)
    print(type(gcode))
    gcode_str = gcode
    gcode_list_str = gcode_str.replace("Gcode: [", "").replace("]", "")
    gcode_list = gcode_list_str.split("', '")
    with open("\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image_gcode", 'w') as file:
        for item in gcode_list:
            file.write(f"{item}+E{exstrod}\n")

    try:
        send_commands([i.strip() for i in open('image_gcode')])
        #speak(reply)
        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=reply
        )

        with open(speech_file_path, "wb") as audio_file:
            audio_file.write(response.content)

        # השמעת קובץ ה-MP3
        playsound(str(speech_file_path))
        time.sleep(0.1)
        os.remove(speech_file_path)




    except:
        pass



    # start button sensing thread
    my_thread = threading.Thread(target=check_contact_stoped)
    my_thread.start()

    while True:

        if command == 'sample':
            # wait for button to be pressed
            if not is_pressed:
                time.sleep(0.01)
                continue
            print("pressed")
        message = listen()


        send_commands(['M106 S0'], False)

        exstrod -= 10



        if message:

            #send_commands(['M106 S10', 'M117 I process the information'], False)
            print("i get the message")


            x = random.randint(10, 80)
            y = random.randint(10, 80)
            send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])

            time.sleep(0.2)

            speech_file_path = Path(__file__).parent / "speech.mp3"
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input="שמעתי את דברייך, אני כבר אענה עליהם. אבל לפני אני אהפוך אותם לתמונה חזותית"
            )

            with open(speech_file_path, "wb") as audio_file:
                audio_file.write(response.content)

            # השמעת קובץ ה-MP3
            playsound(str(speech_file_path))

            time.sleep(0.1)
            os.remove(speech_file_path)

            send_commands(['G1 X90 Y40'])
            time.sleep(5)
            ret, frame = upcamera.read()

            if ret:
                # Create a unique filename with a timestamp
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"image4.jpg"

                x_start = 100  # התחלה בציר ה-X
                y_start = 30  # התחלה בציר ה-Y
                crop_width = 250  # רוחב החיתוך
                crop_height = 500  # גובה החיתוך

                # ביצוע חיתוך של הפריים
                cropped_frame = crop_image(frame, x_start, y_start, crop_width, crop_height)

                # Save the frame as an image file
                cv2.imwrite(filename, cropped_frame)
                print(f"Image saved successfully as {filename}.")

                # Update the last capture time
                time.sleep(2)
                image_path = r"C:\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image4.jpg"

                # Getting the base64 string
                base64_image = encode_image(image_path)

                api_key = ""

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }

                payload = {
                    "model": "gpt-4-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "תתארי מה יש על הדף הלבן שבתמונה?"

                                },
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

                x = random.randint(10, 80)
                y = random.randint(10, 80)
                send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])

                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                response_dict = response.json()
                content = response_dict['choices'][0]['message']['content']
                text_content = str(content)
                print(content)
                #main_act.append({"role": "assistant", "content": text_content})


            else:
                print("Error: Could not read frame from camera")

            # upcamera.release()
            cv2.destroyAllWindows()

            shape_messages.append({"role": "user", "content": message + text_content})
            reply = gpt_interaction(shape_messages)

            reply, listenGcode = extract_gcode_with_brackets(reply)
            #print(reply)
            #threading.Thread(target=handle_speech, args=(reply,), daemon=True).start()
            file_conversition2 = open("C:\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\siha2", "a",encoding='utf-8')
            print("\n" + f"human:{message}", file=file_conversition2)
            print("\n" + f"image promt:{reply}", file=file_conversition2)
            time.sleep(0.1)
            file_conversition2.close()
            with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\promt_to_delly', 'w', encoding='utf-8') as file:
                file.write(reply)
            try:

                print("The promt save in file promt_to_delly.txt")
                creat_image_in_delly()
                time.sleep(0.2)
                convert_image_to_gcode2('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\img.png',
                                       '\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image_gcode.txt')
                time.sleep(1)
                send_commands([i.strip() for i in open('image_gcode')])
                time.sleep(4)


                #send_commands(eval(listenGcode))
                #speak(reply)

            except:
                continue

        print("i answer to the message")

        x = random.randint(10, 80)
        y = random.randint(10, 80)
        send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])

        main_act.append({"role": "user", "content": message}, )
        main_act.append({"role": "assistant", "content": reply})
        reply = gpt_interaction(main_act)
        clean_reply, parsed_gcode = extract_gcode_with_brackets(reply)
        gcode_str = parsed_gcode
        gcode_list_str = gcode_str.replace("Gcode: [", "").replace("]", "")
        gcode_list = gcode_list_str.split("', '")


        with open("\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image_gcode", 'w') as file:
            for item in gcode_list:
                file.write(f"{item}+ E{exstrod}\n")
        send_commands([i.strip() for i in open('image_gcode')])



        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input="לפני שאני עונה לך תשובה אני רוצה להביע אותה באופן חזותי"
        )

        with open(speech_file_path, "wb") as audio_file:
            audio_file.write(response.content)

        # השמעת קובץ ה-MP3
        playsound(str(speech_file_path))

        time.sleep(0.1)
        os.remove(speech_file_path)
        replay_dalley.append({"role": "user", "content": reply})
        reply = gpt_interaction(replay_dalley)

        with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\promt_to_delly', 'w',
                  encoding='utf-8') as file:
            file.write(reply)

        try:
            print("The promt save in file promt_to_delly.txt")
            creat_image_in_delly()
            time.sleep(0.2)
            convert_image_to_gcode2('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\img.png',
                                    '\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image_gcode.txt')
            time.sleep(1)
            send_commands([i.strip() for i in open('image_gcode')])


        except:
            continue



        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=clean_reply
        )

        with open(speech_file_path, "wb") as audio_file:
            audio_file.write(response.content)

        # השמעת קובץ ה-MP3
        playsound(str(speech_file_path))

        time.sleep(0.1)
        os.remove(speech_file_path)

        #ansewr = inner_voices(clean_reply, text_content)

        main_act.append({"role": "assistant", "content": reply})
        file_conversition2 = open("C:\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\siha2", "a",encoding='utf-8')
        print("\n" + f"Tamar 3d printer:{clean_reply}", file=file_conversition2)
        print("\n" + f"descrip image:{text_content}", file=file_conversition2)
        time.sleep(0.1)
        file_conversition2.close()

    my_thread.join()

