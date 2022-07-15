import speech_recognition as sr
import subprocess
import tempfile
import os
# filename = "src/audio/vietnamese/wav/wave_3.wav"

def add_silence(file_name):
    # print(file_name)
    temp_file = os.path.join(next(tempfile._get_candidate_names())+'temp.wav')
    subprocess.run('sox ./sl.wav '+file_name+' ./sl.wav '+file_name.split('/')[-1].replace('.wav','1.wav'),shell=True, check=True,executable='/bin/bash')

def asr_gg(filepath):
    r = sr.Recognizer()
    # open the file
    with sr.AudioFile(filepath) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        text = str(r.recognize_google(audio_data,language='vi-VN').lower())
        return text
        
    except sr.UnknownValueError:
        print(filepath +" Google Speech Recognition could not understand audio")

# print(asr_gg(filename))