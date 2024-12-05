from openai import OpenAI
import re
import time
import ast
from openai import OpenAI
import base64
import requests
from pathlib import Path
from playsound import playsound
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import queue
import time
import re
import cv2
import multiprocessing as mp


client = OpenAI(api_key = "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")

fig, ax, line, head, current_position = None, None, None, None, [0, 0]
gcode_queue = queue.Queue()


with open('/Users/morpeled/Documents/Tamar/promt_image2', 'r') as file:
   promt_image = file.read().strip()

with open('/Users/morpeled/Documents/Tamar/act_2', 'r') as file:
   act = file.read().strip()

with open('/Users/morpeled/Documents/Tamar/use_3', 'r') as file:
   first_sentens = file.read().strip()



shape_messages = [{'role': "system", 'content':promt_image}]
open_sentens = [{"role": "system", "content":first_sentens }]
main_act = [{"role": "system", "content":act},]


conversation1 = [{'role': 'system', 'content': ' I want you to act as The ambitious inner voice of Tamar, the world first 3D printer artist. You will get a sentence that Tamar says to the person opposite her in a conversation she is having with him. Dissect the simplistic and you will see that you need to add ambition to it so that Tamar looks like a printer with an ambitious nature.Put a new sentence in place of the existing sentence'}]
conversation2 = [{'role': 'system', 'content': ' I want you to act as The sensitive inner voice of Tamar, the world first 3D printer artist. The inner voice of Tamar, the worlds first 3D printer artist. You will get a sentence that Tamar says to a man in a conversation she has with him. Dissect the simplistic and you will see that you need to add emotion to it so that Tamar will appear to be a printer with a sensitive and inclusive character. Put a new sentence in place of the existing sentence'}]
conversation3 = [{'role': 'system', 'content': ' I want you to act as The inner voice of Tamar, the world first 3D printer artist. The inner voice of Tamar, the worlds first 3D printer artist.You will receive four sentences that Tamar can say to a person in a conversation she is having with him. Among the sentences, Choose the sentence that will continue the  dialogue. '}]
conversation4 = [{'role': 'system', 'content': 'I want you to act as the curious inner voice of Tamar, the worlds first 3D printer artist. The inner voice of Tamar, the worlds first 3D printer artist. You will receive a sentence that Tamar says to a person in a conversation she has with him. Analyze the sentence and see that you need to add curiosity to it so that Tamar will be seen as a curious printer who wants to learn and develop in the world, therefore she is also interested in what the person in front of her thinks. Put a new sentence in place of the existing sentence'}]

def generate_response(conversation1):
   response = client.chat.completions.create(model="gpt-4-1106-preview", messages=conversation1, temperature=0.5, max_tokens=260)
   return response.choices[0].message.content

def generate_response2(conversation2):
   response2 = client.chat.completions.create(model="gpt-4-1106-preview", messages=conversation2, temperature=0.5, max_tokens=260)
   return response2.choices[0].message.content

def generate_response3(conversation3):
   response3 = client.chat.completions.create(model="gpt-4-1106-preview", messages=conversation3, temperature=0.5, max_tokens=260)
   return response3.choices[0].message.content

def generate_response4(conversation4):
   response4 = client.chat.completions.create(model="gpt-4-1106-preview", messages=conversation4, temperature=0.5, max_tokens=260)
   return response4.choices[0].message.content


def parse_gcode(gcode):
   """Parse a G-code command and extract X and Y coordinates."""
   x_match = re.search(r'X(\d+\.?\d*)', gcode)
   y_match = re.search(r'Y(\d+\.?\d*)', gcode)
   x = float(x_match.group(1)) if x_match else None
   y = float(y_match.group(1)) if y_match else None
   return x, y

def init_plot():
   global fig, ax, line, head, current_position
   fig, ax = plt.subplots()
   ax.set_xlim(0, 200)
   ax.set_ylim(0, 200)
   ax.set_aspect('equal', adjustable='box')
   ax.set_facecolor('white')
   ax.axis('off')
   line, = ax.plot([], [], 'r-')
   head = plt.Circle((0, 0), 5, color='blue')
   ax.add_artist(head)
   current_position = [0, 0]

def update_animation(frame):
   global current_position
   while not gcode_queue.empty():
       gcode_command = gcode_queue.get_nowait()
       x, y = parse_gcode(gcode_command)
       if x is not None and y is not None:
           line.set_xdata(list(line.get_xdata()) + [current_position[0], x])
           line.set_ydata(list(line.get_ydata()) + [current_position[1], y])
           head.center = (x, y)
           current_position = [x, y]
   return line, head

def file_reader():
   """Read G-code commands from a file and add to the queue."""
   processed_commands = set()
   while True:
       with open('/Users/morpeled/Documents/Tamar/image_gcode.txt', 'r') as file:
           for line in file:
               line = line.strip()
               if line and line not in processed_commands:
                   gcode_queue.put(line)
                   processed_commands.add(line)
                   time.sleep(0.03)
       time.sleep(0.08)  # Adjust the sleep time as needed

def start_animation():
   """Start the animation."""
   file_reader_thread = threading.Thread(target=file_reader, daemon=True)
   file_reader_thread.start()
   init_plot()
   ani = animation.FuncAnimation(fig, update_animation, blit=True, interval=500, cache_frame_data=False)
   plt.show()
   plt.close()

# Conduct the dialogue
def inner_voices(reply):
   user_input = reply
   conversation1.append({'role': 'user', 'content': user_input})
   conversation2.append({'role': 'user', 'content': user_input})
   conversation4.append({'role': 'user', 'content': user_input})

   # Generate GPT response
   gpt_response = generate_response(conversation1)
   gpt_response2 = generate_response2(conversation2)
   gpt_response4 = generate_response2(conversation4)

   conversation1.append({'role': 'assistant', 'content': gpt_response})
   conversation2.append({'role': 'assistant', 'content': gpt_response2})
   conversation4.append({'role': 'assistant', 'content': gpt_response4})

   print("ambitious voice: " + gpt_response)
   print("sensitive voice: " + gpt_response2)
   print("curious voice: " + gpt_response4)

   conversation3.append({'role': 'user', 'content': user_input+ gpt_response +gpt_response2 +gpt_response4})
   gpt_response3 = generate_response3(conversation3)
   conversation3.append({'role': 'user', 'content': gpt_response3})
   print("Tamar 3D printer artist: " + gpt_response3)
   return gpt_response3

def gpt_interaction1(gpt_messages : dict):
   # create the input to gpt
   while True:
       try:
           chat = client.chat.completions.create(model="gpt-4-1106-preview", messages=gpt_messages, temperature=0.5, max_tokens=260)
           reply = chat.choices[0].message.content
           return reply
       except Exception as e:
           print(f'got an error of type: {e}. \n wating for 2 seconds and try again')
           time.sleep(2)

def gpt_interaction(gpt_messages : dict):
   # create the input to gpt
   while True:
       try:
           chat = client.chat.completions.create(model="gpt-4-1106-preview", messages=gpt_messages, temperature=0.5, max_tokens=260)
           reply = chat.choices[0].message.content

           # dump all conversation to a file
           with open('/Users/morpeled/Documents/Tamar/siha.txt', 'w') as f:
               f.write(str(gpt_messages))
           return reply
       except Exception as e:
           print(f'got an error of type: {e}. \n wating for 2 seconds and try again')
           time.sleep(2)

def extract_gcode_with_brackets(reply : str):
   print("found gcode")
   square_brackets = re.findall(r'[[^\[\]]*?\]', reply)
   print("0")
   print(square_brackets)
   for bracket in square_brackets:
       print("1")
       drop_part = bracket
       print(drop_part)
       if reply.find(f'GCODE: {bracket}') != -1:
           print("2")
           drop_part = f'GCODE: {bracket}'
       reply = reply.replace(drop_part, "")
       print(f" the Gcode: {bracket} saved in file image_gcode.txt")
       return reply, bracket
   return reply, ""

def extract_gcode_with_brackets_new(reply: str):
   print("Searching for GCODE in the reply...")
   # Using a regex pattern to match text within square brackets
   square_brackets = re.findall(r'\[.*?\]', reply)
   print("Extracted brackets:", square_brackets)

   for bracket in square_brackets:
       print("Checking bracket:", bracket)
       print(type(bracket))
       if 'GCODE: ' + bracket in reply:
           print("Matching GCODE found.")
           drop_part = 'GCODE: ' + bracket
           reply = reply.replace(drop_part, "")
           print(f"The GCODE: {bracket} is saved in file image_gcode.txt")
           # Add code here to save the GCODE to a file if needed
           return reply, bracket
   print("No matching GCODE found.")
   return reply, ""


def extract_gcode(reply : str):
   target_word = "G1"
   words = reply.split()
   if target_word in words:
       index = words.index(target_word)
       if len(words) > index + 2:  # Check if there are two words after target word
           word1 = words[index + 1]
           word2 = words[index + 2]
           gcode_command = f"{target_word} {word1} {word2} "
           index = words.index(target_word)
           del words[index:index + 5]  # Remove target word and two words following it
           new_sentence = ' '.join(words)
           return new_sentence, gcode_command


def creat_image_in_delly():
 print('get the promt start creat image')

 file_path = '/Users/morpeled/Documents/Tamar/promt_to_delly.txt'
 with open(file_path, 'r') as file:
     prompt = file.read().strip()

 response = client.images.generate(model="dall-e-3",prompt=prompt,size="1024x1024",quality="standard",n=1,)

 image_url = response.data[0].url
 file_conversition2= open("/Users/morpeled/Documents/Tamar/siha", "a")
 print("\n"+ f"Tamar 3D printer:{image_url}",file=file_conversition2)
 file_conversition2.close()

 url1 = image_url
 response = requests.get(url1)
 with open("img.png", "wb") as f:
   f.write(response.content)

 time.sleep(0.03)

 print('finish creat image')


def convert_image_to_gcode(image_path, output_gcode_path, scale_factor=0.15):
   print('Start converting image to G-code')

   def image_to_gcode(image_path, scale_factor=1.0):
       # Load the image in grayscale and threshold it
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
       first_300_elements = large_list[:300]
       with open('/Users/morpeled/Documents/Tamar/image_gcode.txt', 'w') as file:
           for line in first_300_elements:
               file.write(line + '\n')

   gcode = image_to_gcode(image_path, scale_factor)

   save_gcode_to_file(gcode, output_gcode_path)

   print('Saved new G-code to file:', output_gcode_path)

def handle_speech(content):
   speech_file_path = Path(__file__).parent / "speech.mp3"
   response = client.audio.speech.create(model="tts-1", voice="nova", input=content)
   response.stream_to_file(speech_file_path)
   playsound(speech_file_path)
   pass

if __name__ == "__main__":
   p = mp.Process(target=start_animation)
   time.sleep(1)
   p.start()
   print("hi")
   reply = gpt_interaction1(open_sentens)
   print(reply)
   reply, gcode = extract_gcode_with_brackets_new(reply)

   threading.Thread(target=handle_speech, args=(reply,), daemon=True).start()

   file_conversition = open("/Users/morpeled/Documents/Tamar/siha", "w")
   print(f"Tamar 3D printer:{reply}", file=file_conversition)
   file_conversition.close()
   gcodeCommands = ast.literal_eval(gcode)
   formatted_gcode = '\n'.join(gcodeCommands)

   # Write the formatted G-code to a text file
   with open('/Users/morpeled/Documents/Tamar/image_gcode.txt', 'w') as file:
       file.write(formatted_gcode)
   time.sleep(1)



   while True:
       message = input("Enter your message: ")
       if message:
           print("i get the message")
           shape_messages.append({"role": "user", "content": message})
           reply = gpt_interaction(shape_messages)
           file_conversition2= open("/Users/morpeled/Documents/Tamar/siha", "a")
           print("\n"+ f"human:{message}",file=file_conversition2)
           print("\n"+ f"image promt:{reply}",file=file_conversition2)
           time.sleep(0.1)
           #file_conversition2.close()
           with open('/Users/morpeled/Documents/Tamar/promt_to_delly.txt', 'w') as file:
               file.write(reply)

       #file_conversition2= open("/Users/morpeled/Documents/Tamar/siha", "r")
       print("i answer to the message")
       main_act.append({"role": "user", "content": message}, )
       main_act.append({"role": "assistant", "content": reply})
       reply = gpt_interaction(main_act)
       print(main_act)
       reply, gcode = extract_gcode_with_brackets_new(reply)
       threading.Thread(target=handle_speech, args=(reply,), daemon=True).start()
       file_conversition2= open("/Users/morpeled/Documents/Tamar/siha", "a")
       print("\n"+ f"Tamar 3D printer:{reply}",file=file_conversition2)
       file_conversition2.close()
       print(reply)
       gcodeCommands = ast.literal_eval(gcode)
       formatted_gcode = '\n'.join(gcodeCommands)

   # Write the formatted G-code to a text file
       with open('/Users/morpeled/Documents/Tamar/image_gcode.txt', 'w') as file:
           file.write(formatted_gcode)
       #time.sleep(1)
       print("The promt save in file promt_to_delly.txt")
       creat_image_in_delly()
       convert_image_to_gcode('/Users/morpeled/Documents/Tamar/img.png', '/Users/morpeled/Documents/Tamar/image_gcode.txt')
       ansewr = inner_voices(reply)
       main_act.append({"role": "assistant", "content": reply})











