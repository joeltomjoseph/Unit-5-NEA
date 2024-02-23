import sys
sys.path.append('/Users/joeljoseph/Documents/Projects/Coding Projects/Unit-5-NEA/')
from functions import soundBoardController
import mido
from collections import deque
import threading
import time

# with mido.open_output('QU-24 MIDI In') as outport:
messages = [soundBoardController.controlMuteChannel(1, True), soundBoardController.controlMuteChannel('LR', True), soundBoardController.controlMuteChannel(1, False), soundBoardController.controlMuteChannel('LR', False), soundBoardController.setVolume('LR', 98), soundBoardController.setVolume(1, 30)]

def sendMessages(messageQueue: deque):
    while True:
        try:
            print(messageQueue.pop())
        # outport.send(messageQueue.pop())
        except IndexError:
            pass

messageQueue = deque()
sendMessageThread = threading.Thread(target=sendMessages, args=(messageQueue,))
sendMessageThread.start()

messageQueue.extendleft(soundBoardController.controlMuteChannel(1, True)[::-1])
messageQueue.extendleft(soundBoardController.controlMuteChannel('LR', True)[::-1])
time.sleep(1)
messageQueue.extendleft(soundBoardController.controlMuteChannel(1, False)[::-1])
messageQueue.extendleft(soundBoardController.controlMuteChannel('LR', False)[::-1])
messageQueue.extendleft(soundBoardController.setVolume('LR', 98)[::-1])
messageQueue.extendleft(soundBoardController.setVolume(1, 30)[::-1])
# print(messageQueue)