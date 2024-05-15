import sys
sys.path.append('/Users/joeljoseph/Documents/Projects/Coding Projects/Unit-5-NEA/')
from functions import soundBoardController
import pyaudio
import wave
from collections import deque
import threading
import time

def sendMessages():
    messages = [
        soundBoardController.controlMuteChannel(1, False),
        soundBoardController.controlMuteChannel('LR', False),
        soundBoardController.setVolume('LR', 98),
        soundBoardController.setVolume(1, 98),
        *[soundBoardController.setVolume(i, 98) for i in range(2, 25)],
    ]
    for message in messages:
        time.sleep(0.05)
        soundBoardController.sendOutput(message)

def resetBoard():
    messages = [
        *[soundBoardController.setVolume(i, 0) for i in range(1, 25)],
    ]
    for message in messages:
        time.sleep(0.05)
        soundBoardController.sendOutput(message)

def recordAudio():
    ''' Function to record audio from the QU-24 which is stored in a .WAV file. The audio is recorded in chunks of 1024 samples and the data is filtered to remove the extra empty bytes. The recording is stopped when the `stopFlag` is set to True or the length of frames is greater than the max recording length. '''
    p = pyaudio.PyAudio()  # Create an interface to PyAudio

    deviceIndex = soundBoardController.audioRecording.findDeviceIndex(p, b'qu-24')
    if deviceIndex == None:
        print('QU-24 is not Connected!')
        p.terminate()
    else:
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt24  # 24 bits per sample, as per the QU-24
        channels = 32 # 32 channels of audio, as per the QU-24      #p.get_device_info_by_index(deviceIndex)['maxInputChannels']
        fs = 48000  # Record at 48000 samples per second, as per the QU-24 
        seconds = 10 # Max recording time in seconds

        with wave.open('Contents/test.wav', 'wb') as fileObject:
            stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True, input_device_index=deviceIndex)

            # Set up the wave file
            fileObject.setnchannels(2) # Set the number of channels to 2 (Stereo)
            fileObject.setsampwidth(p.get_sample_size(sample_format)) # Set the sample width to the sample format (24 bits per sample)
            fileObject.setframerate(fs) # Set the frame rate to the sample rate (48000 samples per second)

            frames = []  # Initialize array to store frames
            print('RECORDING STARTED')
            
            for i in range(0, int(fs / chunk * seconds)): #Might have to change to while loop for continuous recording until exception
                data = stream.read(chunk).hex() # Read the data and convert it to hex

                filteredData = b''.join([bytes.fromhex(data[i:i+12]) for i in range(0, len(data), 192)]) # Filter the data to remove the extra empty bytes

                frames.append(filteredData) # Append the filtered data to the frames array

            # Stop and close the stream 
            stream.stop_stream()
            stream.close()
            # Terminate the PortAudio interface
            p.terminate()
            print('FINISHED RECORDING')
            # Write the frames to the file
            fileObject.writeframes(b''.join(frames))
            fileObject.close()

#sendMessages()
# resetBoard()
recordAudio()