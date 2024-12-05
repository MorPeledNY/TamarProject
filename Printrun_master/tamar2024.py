from openai import OpenAI
import base64
import requests
from pathlib import Path
import cv2
import time
import signal
import numpy as np
import random
import os
from playsound import playsound
import whisper
import pyaudio
import wave
import threading
import re
from printrun.printcore import printcore
from printrun import gcoder
import serial
from PIL import Image
import queue





is_pressed = False
upcamera = cv2.VideoCapture(1)
mullcamera = cv2.VideoCapture(0)

client = OpenAI(api_key='')
gcode_queue = queue.Queue()

# model = whisper.load_model("medium")
model = whisper.load_model("base")

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

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


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
        reply = reply.replace(drop_part, "")
        print(f"Gcode: {bracket}")
        return reply, bracket
    return reply, ""


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
     url1 = image_url
     response = requests.get(url1)
     with open("img.png", "wb") as f:
       f.write(response.content)

     time.sleep(0.2)

     print('finish creat image')

def convert_image_to_gcode3(image_path, output_gcode_path):
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
    first_100_elements = large_list[10:110]
    with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image_gcode', 'w') as file:
        for line in first_100_elements:
            file.write(line + '\n')

    print('G-code conversion completed.')



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
    first_100_elements = large_list[1000:2000]
    with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image_gcode', 'w') as file:
        for line in first_100_elements:
            file.write(line + '\n')

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

def dialog():
    print("התחל")
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    seconds = 0.5
    filename = "output3.wav"
    p1 = pyaudio.PyAudio()

    try:
        # חיפוש המכשיר לפי שם
        device_name = 'PnP'
        device_index = -1
        for i in range(p1.get_device_count()):
            info = p1.get_device_info_by_index(i)
            if device_name.lower() in info['name'].lower():
                device_index = i
                break
        if device_index == -1:
            raise Exception("could not find the 'PnP Microphone connected to the PC")

        print('Recording...')
        stream = p1.open(format=sample_format,
                         channels=channels,
                         rate=fs,
                         frames_per_buffer=chunk,
                         input=True,
                         input_device_index=device_index)

        frames = []
        # שמירת נתונים ב-chunks
        while is_pressed:
            print(is_pressed)
            for i in range(0, int(fs / chunk * seconds)):
                data = stream.read(chunk)
                frames.append(data)

        # עצירת ההקלטה
        stream.stop_stream()
        stream.close()
        p1.terminate()

        print('Finished recording.')

        # שמירת הקובץ כ-WAV
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p1.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        # תמלול ההקלטה
        with open(filename, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="json",
            )

        # קבלת התמלול
        sentence = transcription.text
        print(sentence)

        # בדיקה אם התשובה כוללת את המילה 'כן'
        sentence_lower = sentence.lower()
        if "כן" in sentence_lower:
            print("המילה 'כן' נמצאה במשפט, הפעלה מתבצעת...")

            speech_file_path = Path(__file__).parent / "speech.mp3"
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input="תחזיקי את העבודה מול המלצמה שלי שאוכל לראות מה את עושה"
            )

            with open(speech_file_path, "wb") as audio_file:
                audio_file.write(response.content)
            # השמעת קובץ ה-MP3
            playsound(str(speech_file_path))
            time.sleep(0.1)
            os.remove(speech_file_path)
            activate_action()
        else:
            print("המילה 'כן' לא נמצאה במשפט.")

    finally:
        # מחיקת הקובץ לאחר השימוש
        if os.path.exists(filename):
            os.remove(filename)
            speech_file_path = Path(__file__).parent / "speech.mp3"
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input= "בסדר גמור, בואי נמשיך בשיחה שלנו"
            )

            with open(speech_file_path, "wb") as audio_file:
                audio_file.write(response.content)

            # השמעת קובץ ה-MP3
            playsound(str(speech_file_path))
            time.sleep(0.1)
            os.remove(speech_file_path)

            print(f"הקובץ {filename} נמחק בהצלחה.")
        else:
            print(f"הקובץ {filename} לא נמצא ולא נמחק.")




def activate_action():
    print("הפעולה הופעלה! פתיחת המצלמה הקדמית...")
    mullcamera = cv2.VideoCapture(0)
    time.sleep(2)

    if not mullcamera.isOpened():
        print("לא ניתן לפתוח את המצלמה הקדמית.")
        return

    ret_camera, frame = mullcamera.read()

    if not ret_camera:
        print("לא ניתן לקרוא מהמצלמה.")
    else:
        # שמירת התמונה בקובץ
        cv2.imwrite("captured_image2.png", frame)
        print("תמונה נשמרה כ-captured_image2.png")

        time.sleep(0.2)
        image_path = "captured_image2.png"
        base64_image = encode_image(image_path)

        api_key = "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"

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
                            "text": "מולך תמונה. תתארי מה את רואה בה?"

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
        time.sleep(0.2)

        x = random.randint(10, 80)
        y = random.randint(10, 80)
        send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])
        time.sleep(0.2)

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_dict = response.json()
        content2 = response_dict['choices'][0]['message']['content']
        image_discrip = str(content2)
        print(image_discrip)

        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=image_discrip +"הענה לך באופן חזותי"
        )

        with open(speech_file_path, "wb") as audio_file:
            audio_file.write(response.content)

        # השמעת קובץ ה-MP3
        playsound(str(speech_file_path))
        time.sleep(0.1)
        os.remove(speech_file_path)
        replay_dalley.append({"role": "user", "content": image_discrip})
        image_discrip = gpt_interaction(replay_dalley)

        with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\promt_to_delly', 'w', encoding='utf-8') as file:
            file.write(image_discrip)


        print("The promt save in file promt_to_delly.txt")
        creat_image_in_delly()
        time.sleep(1)
        convert_image_to_gcode3('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\img.png',
                                    '\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image_gcode.txt')
        time.sleep(1)
        send_commands([i.strip() for i in open('image_gcode')])
        time.sleep(2)


        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input="מה דעתך?"
        )

        with open(speech_file_path, "wb") as audio_file:
            audio_file.write(response.content)

        # השמעת קובץ ה-MP3
        playsound(str(speech_file_path))
        time.sleep(0.1)
        os.remove(speech_file_path)


    # שחרור המצלמה וסגירת החלון
    cv2.destroyAllWindows()


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
    gcode_str = gcode
    gcode_list_str = gcode_str.replace("Gcode: [", "").replace("]", "")
    gcode_list = gcode_list_str.split("', '")
    #with open("\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\image_gcode", 'w') as file:
    #   for item in gcode_list:
    #        file.write(f"{item}+\n")
    time.sleep(0.1)

    x = random.randint(10, 80)
    y = random.randint(10, 80)
    send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])

    time.sleep(0.2)

    try:
        send_commands([i.strip() for i in open('image_gcode')])
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

    count=0

    while True:

        if command == 'sample':
            # wait for button to be pressed
            if not is_pressed:
                time.sleep(0.01)
                continue
            print("pressed")
        message = listen()


        send_commands(['M106 S0'], False)


        if message:

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
                filename = f"image4.png"

                x_start = 100  # התחלה בציר ה-X
                y_start = 30  # התחלה בציר ה-Y
                crop_width = 250  # רוחב החיתוך
                crop_height = 500  # גובה החיתוך
                cropped_frame = crop_image(frame, x_start, y_start, crop_width, crop_height)
                cv2.imwrite(filename, cropped_frame)
                print(f"Image saved successfully as {filename}.")

                x = random.randint(10, 80)
                y = random.randint(10, 80)
                send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])
                time.sleep(0.1)

                client = OpenAI(api_key="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")
                response = client.images.edit(
                    model="dall-e-2",
                    image=open("image4.png", "rb"),
                    mask=open("mask.png", "rb"),
                    prompt="Paint the parts of the mask white ",
                    n=1,
                    size="1024x1024"
                )

                image_url = response.data[0].url
                image_data = requests.get(image_url).content
                with open("edited_image.png", "wb") as f:
                    f.write(image_data)

                image = cv2.imread("edited_image.png")
                print("Image saved successfully!")

                x = random.randint(10, 80)
                y = random.randint(10, 80)
                send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])

                time.sleep(0.2)

                x = random.randint(10, 80)
                y = random.randint(10, 80)
                send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])

                time.sleep(0.2)
                image_path = "edited_image.png"
                base64_image = encode_image(image_path)

                api_key = "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"

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
                                    "text": "התמונה לא באיכות טובה. היא בעצם ציור בטושים על דף לבן. תארי מה את רואה בדף הלבן?"

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

            else:
                print("Error: Could not read frame from camera")

            cv2.destroyAllWindows()

            shape_messages.append({"role": "user", "content": message + text_content})
            reply = gpt_interaction(shape_messages)

            reply, listenGcode = extract_gcode_with_brackets(reply)

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
                file.write(f"{item}+\n")
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

        with open('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\promt_to_delly', 'w', encoding='utf-8') as file:
            file.write(reply)

        try:
            print("The promt save in file promt_to_delly.txt")
            creat_image_in_delly()
            time.sleep(0.2)
            convert_image_to_gcode3('\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\img.png',
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

        main_act.append({"role": "assistant", "content": reply})
        file_conversition2 = open("C:\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\siha2", "a",encoding='utf-8')
        print("\n" + f"Tamar 3d printer:{clean_reply}", file=file_conversition2)
        #print("\n" + f"descrip image:{text_content}", file=file_conversition2)
        time.sleep(0.1)
        file_conversition2.close()
        time.sleep(0.1)

        count += 1
        if count % 2 == 0:
            speech_file_path = Path(__file__).parent / "speech.mp3"
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input="האם את עובדת יחד איתי?"
            )

            with open(speech_file_path, "wb") as audio_file:
                audio_file.write(response.content)

            # השמעת קובץ ה-MP3
            playsound(str(speech_file_path))
            time.sleep(0.1)
            os.remove(speech_file_path)
            if command == 'sample':
                print("ממתין ללחיצת כפתור...")
                while not is_pressed:
                    time.sleep(0.01)  # מחכה 0.01 שניות ואז בודק שוב את הכפתור
                print("כפתור נלחץ! ממשיכים...")
                na = dialog()
            time.sleep(0.2)

            x = random.randint(10, 80)
            y = random.randint(10, 80)
            send_commands([f" G1 X{x} Y{y}", f" G1 X{y} Y{x}"])

            time.sleep(0.2)


    my_thread.join()

