import os
import pyttsx3
try:
    import win32com.client as win
except:
    win=None

def voiceBroad(text):
    if win==None:
        return -1
    if isinstance(text, str):
        speak = win.Dispatch("SAPI.SpVoice")
        speak.Speak(text)
    elif isinstance(text, list):
        speak = win.Dispatch("SAPI.SpVoice")
        if len(text) > 0:
            for each in text:
                if each != "":
                    speak.Speak(each)
    return 0

if __name__ == '__main__':
    voiceBroad("测试一下能发出声音吗")