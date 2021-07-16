import speech_recognition as sr
from audioread import audio_open
import tkinter.filedialog
import tkinter as tk
import os
from math import ceil

# TODO: Add other speech recognition servers
# TODO: Add language selector
# TODO: Add support for video files

def initialMessage():
    print('transcriPy')
    print('')
    print('Código fonte disponível em <https://github.com/marlonsmathias/transcriPy>')
    print('')
    print('Licença: GPL 3.0 (em inglês):')
    print('This program is free software: you can redistribute it and/or modify')
    print('it under the terms of the GNU General Public License as published by')
    print('the Free Software Foundation, either version 3 of the License, or')
    print('(at your option) any later version.')
    print('')
    print('This program is distributed in the hope that it will be useful,')
    print('but WITHOUT ANY WARRANTY; without even the implied warranty of')
    print('MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the')
    print('GNU General Public License for more details.')
    print('')
    print('You should have received a copy of the GNU General Public License')
    print('along with this program.  If not, see <https://www.gnu.org/licenses/>')
    print('')

def getKey(filePath = './key.txt'):
    try:
        with open(filePath, "r") as f:
            return f.readline().replace("\n","")
    except:
        print(f"A chave para o wit.ai API não foi encontrada no arquivo {filePath}.\nA chave pode ser gerada em <https://wit.ai/>. É necessário fazer login.")
        input('Aperte Enter para sair')
        exit()
        return None

def getFileName():
    root = tk.Tk()
    root.withdraw()
    fileName = tk.filedialog.askopenfilename()
    print('Abrindo arquivo: ' + fileName)
    return fileName

def checkffmpeg():
    if os.name == 'nt':
        f = os.system('where ffmpeg > NUL 2>&1')
        if f != 0:
            print('')
            print('O programa ffmpeg não foi encontrado neste computador e deverá ser baixado para o transcriPy funcionar.')
            print('Este processo é necessário apenas uma vez.')
            print('Siga os seguintes passos:')
            print('1 - Baixe o arquivo do link: <https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip>')
            print('2 - Extraia a pasta')
            print('3 - Copie o arquivo ffmpeg.exe, que está em ffmpeg-x.x-essentials_build/bin da pasta extraida')
            print('4 - Cole este arquivo na mesma pasta do programa de transcrição')
            input('Aperte Enter para sair')
            exit()


    else:
        f = os.system('which ffmpeg > /dev/null 2>&1')
        if f != 0:
            print('O programa ffmpeg não foi encontrado neste computador,')
            print('em algumas distribuições Linux, ele pode ser instalado com o comando:')
            print('sudo apt install ffmpeg')
            input('Aperte Enter para sair')
            exit()


def process(filepath,apiKey=None):

    blockLength = 10

    with audio_open(filepath) as f:
        audioLength = f.duration

    # Get output file
    outName = filepath[:-4] + '-transcrito.txt'

    # Compute number of chunks
    nChunks = ceil(audioLength/blockLength)
    print(f"{audioLength} segundos: Dividindo em {nChunks} blocos de {blockLength} segundos cada")


    recognizer = sr.Recognizer()
    
    # Now process each chunk
    for index in range(0,nChunks):
        print(f"Processando bloco {index+1} de {nChunks}")
        
        # Split chunk with ffmpeg
        os.system(f"ffmpeg -hide_banner -loglevel error -y -ss {blockLength*index} -i \"{filepath}\" -t {blockLength} temp.wav")

        # Load chunk
        with sr.AudioFile('./temp.wav') as source:
            audio = recognizer.record(source)

        transcript = recognizer.recognize_wit(audio, key=apiKey)
            
        print(transcript)

        # Write output to file
        with open(outName, "a") as outHandle:
            outHandle.write(f'{index}\n')
            outHandle.write(f'{transcript}\n')

    # Clean up temporary file
    os.remove('./temp.wav')

# Main part
if __name__ == "__main__":
    # Aviso inicial
    initialMessage()

    # Get Google Cloud Speech API key
    apiKey = getKey()

    # Get file name
    filepath = getFileName()
    if not filepath:
        exit()

    # Check ffmpeg
    checkffmpeg()

    # Process file
    process(filepath,apiKey=apiKey)
