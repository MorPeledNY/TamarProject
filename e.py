import text2emotion as te
import nltk
text = 'i feel amazing'
print(te.get_emotion(text))

emoshion_d = te.get_emotion(text)
print(emoshion_d)

namber_max_value = max(emoshion_d.values())
print(namber_max_value)

if namber_max_value != 0:

    max_valeu= max(emoshion_d, key=emoshion_d.get)
    print(max_valeu)

    if max_valeu == 'Happy':
        print(1)
    else:
        print(0)

else:
    print('natural')




