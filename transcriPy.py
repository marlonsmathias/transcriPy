import speech_recognition as sr
from audioread import audio_open
import tkinter.filedialog
import tkinter as tk
from os import remove, system
from math import ceil

# TODO: Add other speech recognition servers
# TODO: Add language selector
# TODO: Add checker for ffmpeg and maybe autodownloader

def getFileName():
    root = tk.Tk()
    root.withdraw()
    fileName = tk.filedialog.askopenfilename()
    print('Abrindo arquivo: ' + fileName)
    return fileName

def process(filepath):

    with audio_open(filepath) as f:
        audioLength = f.duration

    # Get output file
    outName = filepath[:-4] + '-transcrito.txt'

    # Compute number of chunks
    nChunks = ceil(audioLength/60)
    print(f"{audioLength} segundos: Dividindo em {nChunks} blocos de 1 minuto cada")


    recognizer = sr.Recognizer()
    
    # Now process each chunk
    for index in range(0,nChunks):
        print(f"Processando bloco {index+1} de {nChunks}")
        
        # Split chunk with ffmpeg
        system(f"ffmpeg -hide_banner -loglevel error -y -ss {60*index} -i \"{filepath}\" -t 60 temp.wav")

        # Load chunk
        with sr.AudioFile('./temp.wav') as source:
            audio = recognizer.record(source)

        # Use Google's speech recognition
        transcript = recognizer.recognize_google(audio, language="pt-BR") # Change language here
        print(transcript)

        # Write output to file
        with open(outName, "a") as outHandle:
            outHandle.write(f'{index}\n')
            outHandle.write(f'{transcript}\n')

    # Clean up temporary file
    remove('./temp.wav')

# Main part

# Get file name
filepath = getFileName()

# Process file
process(filepath)