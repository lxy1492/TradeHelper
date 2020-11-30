import pyttsx3
try:
    import win32com.client as win
except:
    win = None

def testVoice():
    if win==None:
        return -1
    speak = win.Dispatch("SAPI.SpVoice")
    speak.Speak("come on")
    speak.Speak("你好")
    return 0

def voiceForText(message):
    if win==None:
        return -1
    speak = win.Dispatch("SAPI.SpVoice")
    if isinstance(message,str):
        speak.Speak(message)
    return 0


if __name__ == '__main__':
    voiceForText("试一下文字转语音")