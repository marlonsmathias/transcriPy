import speech_recognition as sr
import tkinter.filedialog
import tkinter as tk
import os
import re
from math import floor,ceil
import traceback

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
            s = f.readline().replace("\n","").split()
            apiKey = s[0]
            if len(s) > 1:
                api = s[1]
            else:
                api = 'wit'
        return api, apiKey
    except:
        print(f"Nenhuma chave de API foi encontrada no arquivo {filePath}.\nA chave para o wit.ai pode ser gerada em <https://wit.ai/>. É necessário fazer login.")
        print('O serviço do Google será usado com chave padrão, que deve ser usada apenas para fins de teste e uso pessoal.\nO programa funcionará normalmente.')
        return 'google', None

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


def getBlocks(filepath,minLength=0.3,maxLength=10):
    os.system(f"ffmpeg -i \"{filepath}\" -af silencedetect=noise=-30dB:d=0.5 -f null - 2> temp.txt")
    starts = [0]
    durations = []

    with open('temp.txt', encoding='utf-8') as f:
        for line in f:
            if 'silence_duration:' in line:
                numbers = re.findall("[-+]?\d*\.\d+|\d+",line)
                silenceEnd = float(numbers[-2])
                silenceDuration = float(numbers[-1])
                durations.append(silenceEnd-silenceDuration-starts[-1])
                starts.append(silenceEnd)
            if 'time=' in line:
                for chunk in line.split():
                    if 'time=' in chunk:
                        numbers = re.findall("[-+]?\d*\.\d+|\d+",line)
                        end = 3600*int(numbers[0]) + 60*int(numbers[1]) + float(numbers[2])

    os.remove('./temp.txt')

    durations.append(end-starts[-1])

    blocks = []
    for i in range(0,len(starts)):
        s = starts[i]
        d = durations[i]
        if d>minLength and d<=maxLength:
            blocks.append([s, d])
        if d>maxLength:
            n = ceil(d/maxLength)
            for j in range(0,n):
                blocks.append([s+j*d/n, d/n])

    return blocks

def process(filepath,blocks,api='wit',apiKey=None):

    # Get output file
    outName = filepath[:-4] + '-transcrito.txt'

    recognizer = sr.Recognizer()
    
    nBlocks = len(blocks)

    # Now process each chunk
    for i in range(0,nBlocks):

        s = blocks[i][0]
        d = blocks[i][1]
        tStr = f"{floor(s/3600)}:{floor(s/60):02}:{s%60:04.1f}"

        print(f"Processando bloco {i+1} de {nBlocks} ({tStr})")
        
        # Split chunk with ffmpeg
        os.system(f"ffmpeg -hide_banner -loglevel error -y -ss {s} -i \"{filepath}\" -t {d} temp.wav")

        # Load chunk
        with sr.AudioFile('./temp.wav') as source:
            audio = recognizer.record(source)
        try:
            if api=='wit':
                transcript = recognizer.recognize_wit(audio, key=apiKey)
            else:
                transcript = recognizer.recognize_google(audio, key=apiKey, language='pt-BR')
        except:
            print("Erro no bloco:")
            traceback.print_exc()
            transcript = ''

        print(transcript)

        # Write output to file
        with open(outName, "a") as outHandle:
            outHandle.write(f'{tStr}\n')
            outHandle.write(f'{transcript}\n')

    # Clean up temporary file
    os.remove('./temp.wav')

# Main part
if __name__ == "__main__":
    # Aviso inicial
    initialMessage()

    # Get wit.ai API key
    api,apiKey = getKey()

    # Get file name
    filepath = getFileName()
    if not filepath:
        exit()

    # Check ffmpeg
    checkffmpeg()

    # Get audio blocks
    blocks = getBlocks(filepath,maxLength=10)

    # Process file
    process(filepath,blocks,api=api,apiKey=apiKey)
