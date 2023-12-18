import mido
import time
from functions import soundBoardRecording as ar

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

groupsOfMessages = [
    [mido.Message('note_on', channel=0, note=103, velocity=63), mido.Message('note_on', channel=0, note=103, velocity=0)], # UNMUTE LR MASTER
    [mido.Message('control_change', channel=0, control=99, value=103), mido.Message('control_change', channel=0, control=98, value=23), mido.Message('control_change', channel=0, control=6, value=98), mido.Message('control_change', channel=0, control=38, value=7)], # SET LR MASTER FADER TO 0
    [mido.Message('note_on', channel=0, note=32, velocity=63), mido.Message('note_on', channel=0, note=32, velocity=0)], # UNMUTE CHANNEL 1
    [mido.Message('control_change', channel=0, control=99, value=32), mido.Message('control_change', channel=0, control=98, value=23), mido.Message('control_change', channel=0, control=6, value=98), mido.Message('control_change', channel=0, control=38, value=7)] # SET CHANNEL 1 FADER TO 0dB
    ]

def readInput():
    with mido.open_input('QU-24 MIDI Out') as inport:
        for message in inport:
            print(f"{message}")

def sendOutput():
    with mido.open_output('QU-24 MIDI In') as outport:
        for group in groupsOfMessages:
            for message in group:
                #time.sleep(userMinimumTimeBetweenCues)
                outport.send(message)
            #time.sleep(1)

def unMuteChannel(channel) -> mido.Message:
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
    return [mido.Message('note_on', channel=0, note=channel, velocity=63), mido.Message('note_on', channel=0, note=channel, velocity=0)]

def setVolume(volume):
    pass
readInput()
#ar.listAudioDevices()
#ar.recordAudio()
#sendOutput()

'''
Try to use multithreading to allow simultaneous read/write but might not be needed so :/
Can write messages to txt file and then reread them in using mido.parse_string()
can convert messages to hex with message.hex()
'''