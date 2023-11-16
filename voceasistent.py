import speech_recognition as sr
import pyttsx3
from playsound import playsound
import text2emotion as te


listener = sr.Recognizer()

def talk(text):
    engine.setProperty('volume', 1.0)
    engine.setProperty('rate', 100)
    engine.say(text)
    engine.runAndWait()


def take_commands():
    try:
        with sr.Microphone() as source:
            print('listening..')

            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
    except:
        command = ""
        pass
    return command

def run_alexa():
    command = take_commands()
    print(command)
    if 'print' in command:
        song = command.replace('print', '')
        talk('printing' + song)
        print(song)
    else:
        talk('Please say again.')

if __name__ in "__main__":
    listener.dynamic_energy_threshold = False
    listener.pause_threshold = 15
    listener.non_speaking_duration = 10
    listener.phrase_threshold = 0.5
    with sr.Microphone() as source:
        listener.adjust_for_ambient_noise(source, 1.0)
    engine = pyttsx3.init()

    # playsound('welcom.mp3')
    all_voices = engine.getProperty('voices')
    engine.setProperty('voice', all_voices[1].id)
    engine.setProperty('volume', 1.0)
    engine.setProperty('rate', 100)
    engine.say('Welcome Mor  ... how you feels today?')
    engine.runAndWait()

    spoken_pharse = ""
    while "alexa" not in spoken_pharse:
        spoken_pharse = take_commands()
    text = spoken_pharse
    print(te.get_emotion(text))

    emoshion_d = te.get_emotion(text)
    print(emoshion_d)

    namber_max_value = max(emoshion_d.values())
    print(namber_max_value)

    if namber_max_value != 0:

        max_valeu = max(emoshion_d, key=emoshion_d.get)
        print(max_valeu)

        if max_valeu == 'Happy':
            print(1)
        else:
            print(0)

    else:
        print('natural')

    # send file to printer

    engine.say("oh Yeahhh! I like to print cute little bears...A file of a small bear with a loop for a necklace, thirty by sixteen millimeters has been sent for printing. The printing time is six minutes.")
    spoken_pharse = ""
    while "yes" not in spoken_pharse:
        spoken_pharse = take_commands()

    #open camera







