import re
import sys
import time
import getpass
import argparse
from collections import namedtuple

import pyaudio
import sounddevice
import numpy as np

VERSION = '0.1.0'
CODEBY = 'wise0n'

ColorFactory = namedtuple('ColorFactory', 'RED END')
Color = ColorFactory('\033[91m', '\033[0m')

class MorseCode():
    def __init__(self, string):
        self.string = string
        self.key = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
                    'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
                    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
                    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
                    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
                    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
                    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---',
                    '3': '...--', '4': '....-', '5': '.....', '6': '-....',
                    '7': '--...', '8': '---..', '9': '----.', '0': '-----',
                    '.': '.-.-.-', '\'': '.----.', '(': '-.--.', ':': '---...',
                    '+': '.-.-.', '"': '.-..-.', ',': '--..--', '!': '-.-.--',
                    ')': '-.--.-', ';': '-.-.-.', '-': '-....-', '$': '...-..-',
                    '?': '..--..', '/': '-..-.', '&': '.-...', '=': '-...-',
                    '_': '..--.-', '@': '.--.-.', ' ': '/ '}

    def encode(self) -> int | None:
        string_encoded = ''

        character_upper = [x.upper() for x in self.string]

        for character in character_upper:
            try:
                if self.key[character] != '/ ':
                    string_encoded += self.key[character] + ' '
                else:
                    string_encoded += self.key[character]
            except KeyError:
                print(f'{Color.RED}[failed] Cannot encode character: {character}{Color.END}')
                return 1

        print(f'[encoded] {string_encoded}')

        return None

    def decode(self) -> int | None:
        string_decoded = ''

        character_grouped = re.findall(r'\S+', self.string)

        for group in character_grouped:
            try:
                if group != '/':
                    string_decoded += dict((v, k) for k, v in self.key.items())[group]
                else:
                    string_decoded +=  dict((v, k) for k, v in self.key.items())[f'{group} ']
            except KeyError:
                print(f'{Color.RED}[failed] Cannot decode character(s): {group}{Color.END}')
                return 1

        print(f'[decoded] {string_decoded.lower()}')

        return None

    def dit_dah(self) -> int | None:
        chunk = 1024
        samplerate = 44100
        frequency = 800
        duration = 0.16

        for character in self.string:
            if character not in ['.', '-', ' ', '/']:
                print(f'{Color.RED}[failed] Cannot play character: {character}{Color.END}')
                return 1

        dit = (np.sin(2 * np.pi * np.arange(samplerate * duration) * frequency / samplerate)).astype(np.float32)
        dah = (np.sin(2 * np.pi * np.arange(samplerate * duration * 2) * frequency / samplerate)).astype(np.float32)

        p_audio = pyaudio.PyAudio()

        print('[playing] ', end='')

        for character in self.string:
            if character == '.':
                dit_dah_sound = dit

                stream = p_audio.open(format=pyaudio.paFloat32,
                                      channels=1,
                                      rate=samplerate,
                                      output=True,
                                      input=True,
                                      frames_per_buffer=chunk)

                stream.write(dit_dah_sound.tobytes())

                stream.stop_stream()
                stream.close()
                time.sleep(0.15)
            elif character == '-':
                dit_dah_sound = dah

                stream = p_audio.open(format=pyaudio.paFloat32,
                                      channels=1,
                                      rate=samplerate,
                                      output=True,
                                      input=True,
                                      frames_per_buffer=chunk)

                stream.write(dit_dah_sound.tobytes())

                stream.stop_stream()
                stream.close()
                time.sleep(0.15)
            elif character == ' ':
                time.sleep(0.15)

            print(character, end='')
            sys.stdout.flush()

        print('')

        p_audio.terminate()

        return None

def main():
    parser = argparse.ArgumentParser(
            prog='pymorsecode',
            description='''
+-+-+-+-+-+-+-+-+-+-+-+
|p|y|m|o|r|s|e|c|o|d|e|
+-+-+-+-+-+-+-+-+-+-+-+

Morse code encoder/decoder''',
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v',
                        '--version',
                        help='returns pymorsecode\'s version',
                        action='store_true')
    parser.add_argument('-e',
                        '--encode',
                        help='select encode string (python3 pymorsecode.py -e)',
                        action='store_true')
    parser.add_argument('-d',
                        '--decode',
                        help='select decode string (python3 pymorsecode.py -d)',
                        action='store_true')
    parser.add_argument('-c',
                        '--conceal',
                        help='when selected encoding/decoding conceal input given by not echoing to console (python3 pymorsecode.py -e/d -c)',
                        action='store_true')
    parser.add_argument('-x',
                        '--txt',
                        help='pass a text file containg the string to encode/decode (python3 pymorsecode.py -e/d -x xxxxx/xxxxx)',
                        type=str)
    parser.add_argument('-p',
                        '--play',
                        help='plays the encoded morse code dits and dahs (python3 pymorsecode.py -p)',
                        action='store_true')
    args = parser.parse_args()

    if args.version:
        print(f'[version]: {VERSION}')

    if args.encode:
        if args.txt:
            string_file = [line.strip() for line in open(args.txt, 'r', encoding='utf-8')]
            string_res =  ''.join(x if x != '' else ' ' for x in string_file)
        elif args.conceal:
            string_input = getpass.getpass(prompt='[encode] string to encode: ')
            string_res = string_input
        else:
            string_input = input('[encode] string to encode: ')
            string_res = string_input

        MorseCode(string_res).encode()

    if args.decode:
        if args.txt:
            string_file = [line.strip() for line in open(args.txt, 'r', encoding='utf-8')]
            string_res =  ''.join(x for x in string_file)
        elif args.conceal:
            string_input =  getpass.getpass(prompt='[decode] string to decode: ')
            string_res = string_input
        else:
            string_input = input('[decode] string to decode: ')
            string_res = string_input

        MorseCode(string_res).decode()

    if args.play:
        string_input = input('[play] string to play: ')
        string_res = string_input

        MorseCode(string_res).dit_dah()

if __name__ == '__main__':
    main()
