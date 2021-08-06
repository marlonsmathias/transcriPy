import vosk
import tkinter.filedialog
import tkinter as tk
import os
import subprocess
from math import floor

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

def process(filepath,modelFolder,sampleRate):

    # Get output file
    outName = filepath[:-4] + '-transcrito.txt'

    # Initialize model
    vosk.SetLogLevel(-1)
    model = vosk.Model(modelFolder)
    recognizer = vosk.KaldiRecognizer(model,sampleRate)

    # Read audio with ffmpeg
    ffmpegProcess = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i', filepath, '-ar', str(sampleRate) , '-ac', '1', '-f', 's16le', '-'], stdout=subprocess.PIPE)

    # Get terminal size
    width = os.get_terminal_size()[0]

    time = 0
    dt = 8*4000/(16*sampleRate)
    print(f'[{floor(time/60)}:{floor(time%60):02}]')

    # Process chunk
    while True:
        time += dt
        data = ffmpegProcess.stdout.read(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            t = recognizer.Result()
            t = t.split('"')[3]
            print(t)
            print(f'[{floor(time/60)}:{floor(time%60):02}]')
            with open(outName, "a") as outHandle:
                outHandle.write(f'{t}\n')
        else:
            t = recognizer.PartialResult()
            t = t.split('"')[3]
            print(t[-width:-1], end='\r')

# Main part
if __name__ == "__main__":
    # Aviso inicial
    initialMessage()

    # Get file name
    filepath = getFileName()
    if not filepath:
        exit()

    # Check ffmpeg
    checkffmpeg()

    # Process file
    process(filepath,modelFolder='modelo-portugues',sampleRate=16000)
