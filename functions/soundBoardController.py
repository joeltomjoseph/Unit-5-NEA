import mido
import time
from collections import deque

from functions import soundBoardRecording as audioRecording

'''
inport = mido.get_input_names()
outport = mido.get_output_names()
print(inport) # ['QU-24 MIDI Out', 'MIDI Control 1']
print(outport) # ['MIDI Control 1', 'QU-24 MIDI In']
'''
#ioport = mido.open_ioport(port)
#print(ioport.name)

''' ALL VALUES ARE IN HEX, MIDO RETURNS IN DECIMAL CONVERT LIL BRO
N is MIDI Channel (0 based, always 0, unless using Custom layer with MIDI option)
CH is Input Channel (0 based, ch1 = 0)
VA is Main Variable to change (volume, on/off, pan direction)
VX is Secondary Variable

The MSB (most significant byte) selects the mixer channel (CH) 
LSB (least significant byte) selects the parameter number (ID). 
The data entry MSB sets the parameter value (VA)
LSB sets the index value for its range (VX) where needed. 

CHANNEL 1 = 20 (32)
ChANNEL 2 = 21 (33)
CHANNEL 24 = 37 (55)
CHANNEL ST3 = 42 (66)
LR MASTER = 67 (103)

VOLUME LEVELS for FADERS (dBu)
+10     7F
+5      72
0       62
-5      4F
-10     3F
-15     36
-20     2F
-25     27
-30     1F
-35     17
-40     10
-45     0C
-inf    00

MUTE/UNMUTE CHANNEL - type: note_on
MUTE ON     9N, CH, 7F,     9N, CH, 00 (velocity >= 40) [mido.Message('note_on', channel=, note=, velocity=127), mido.Message('note_on', channel=, note=, velocity=0)]
MUTE OFF    9N, CH, 3F,    9N, CH, 00 (velocity < 40) [mido.Message('note_on', channel=, note=, velocity=63), mido.Message('note_on', channel=, note=, velocity=0)]

FADER MESSAGE (Change volume of a fader - remember to unmute first to hear) - type: control_change
BN, 63, CH,     BN, 62, 17,     BN, 06, VA      BN, 26, 07
'''

messageQueue = deque() # create this when a connection is made to the QU-24

def checkIfConnected(searchTerm: str):
    ''' Function to check if the QU-24 is connected. '''
    pyaudioInterface = audioRecording.pyaudio.PyAudio()

    for i in range(pyaudioInterface.get_device_count()):
        device = pyaudioInterface.get_device_info_by_index(i)
        name = device['name'].encode('utf-8')
        #print(f"Index: {i} - {name}, Input CHs: {device['maxInputChannels']}, Output CHs: {device['maxOutputChannels']}")

        if name.lower().find(searchTerm) >= 0 and device['maxInputChannels'] > 0:
            pyaudioInterface.terminate()
            return True
    pyaudioInterface.terminate()
    # return True # For testing purposes, return True
    return False

def readInput():
    ''' Function to read input from the QU-24 and print it to the console. For debugging purposes. Can also be used for readouts from the QU-24. '''
    with mido.open_input('QU-24 MIDI Out') as inport:
        for message in inport:
            print(f"{message}")

def sendOutput(message: list[mido.Message]):
    ''' Function to send output to the QU-24. '''
    with mido.open_output('QU-24 MIDI In') as outport:
        for midi in message:
            outport.send(midi)
            #time.sleep(1)

def controlMuteChannel(channel, mute: bool = False) -> list[mido.Message]:
    ''' Function to control the mute of a channel. If mute is True, then mute the channel. '''
    extraChannelLookup = {
        'ST1':64,
        'ST2':65,
        'ST3':66,
        'LR':103,
        'MTX1-2':108
    }

    if channel in range(1, 25):
        channel += 31
    elif channel in extraChannelLookup:
        channel = extraChannelLookup[channel]
    else:
        return None
    
    if mute:
        return [mido.Message('note_on', channel=0, note=channel, velocity=127), mido.Message('note_on', channel=0, note=channel, velocity=0)]
    else:
        return [mido.Message('note_on', channel=0, note=channel, velocity=63), mido.Message('note_on', channel=0, note=channel, velocity=0)]

def setVolume(channel, volume: int) -> list[mido.Message]:
    ''' Function to set the volume of a channel. 
    VOLUME LEVELS for FADERS (dBu)
    +10 = 127, +5 = 114, 0 = 98, -5 = 79, -10 = 63, -15 = 54, -20 = 47, -25 = 39, -30 = 31, -35 = 23, -40 = 16, -45 = 12, -inf = 0
    '''
    extraChannelLookup = {
        'ST1':64,
        'ST2':65,
        'ST3':66,
        'LR':103,
        'MTX1-2':108
    }

    if channel in range(1, 25):
        channel += 31
    elif channel in extraChannelLookup:
        channel = extraChannelLookup[channel]
    else:
        return None
    
    if not(volume >= 0 and volume <= 127):
        return None

    return [mido.Message('control_change', channel=0, control=99, value=channel), mido.Message('control_change', channel=0, control=98, value=23), mido.Message('control_change', channel=0, control=6, value=volume), mido.Message('control_change', channel=0, control=38, value=7)]

#readInput()
#ar.listAudioDevices()
#ar.recordAudio()
#sendOutput()
# print(checkIfConnected(b'qu-24'))

'''
Try to use multithreading to allow simultaneous read/write but might not be needed so :/
Can write messages to txt file and then reread them in using mido.parse_string()
can convert messages to hex with message.hex()
'''