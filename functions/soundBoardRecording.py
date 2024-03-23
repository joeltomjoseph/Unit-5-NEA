import pyaudio
import wave
import datetime

from .generalFunctions import resourcePath

def findDeviceIndex(pyaudioInterface: pyaudio.PyAudio, searchTerm: str):
    ''' Function to find the index of the QU-24 in the list of audio devices to check if it exists before recording. If the QU-24 is not found, then return None. '''
    found = None

    for i in range(pyaudioInterface.get_device_count()):
        device = pyaudioInterface.get_device_info_by_index(i)
        name = device['name'].encode('utf-8')
        #print(f"Index: {i} - {name}, Input CHs: {device['maxInputChannels']}, Output CHs: {device['maxOutputChannels']}")

        if name.lower().find(searchTerm) >= 0 and device['maxInputChannels'] > 0:
            found = i
            break
    return found

def listAudioDevices(pyaudioInterface: pyaudio.PyAudio):
    ''' Function to list all the audio devices along with the number of input and output channels. For Debugging Purposes. '''
    info = pyaudioInterface.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (pyaudioInterface.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print(f"Input Device id {i} - {pyaudioInterface.get_device_info_by_host_api_device_index(0, i).get('name')}, Channels: {pyaudioInterface.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')}")

def recordAudio():
    ''' Function to record audio from the QU-24 which is stored in a .WAV file. The audio is recorded in chunks of 1024 samples and the data is filtered to remove the extra empty bytes. The recording is stopped when the `stopFlag` is set to True or the length of frames is greater than the max recording length. '''
    p = pyaudio.PyAudio()  # Create an interface to PyAudio

    deviceIndex = findDeviceIndex(p, b'qu-24')
    if deviceIndex == None:
        print('QU-24 is not Connected!')
    else:
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt24  # 24 bits per sample, as per the QU-24
        channels = 32 # 32 channels of audio, as per the QU-24      #p.get_device_info_by_index(deviceIndex)['maxInputChannels']
        fs = 48000  # Record at 48000 samples per second, as per the QU-24
        maxSeconds = 1000 # Max recording time in seconds
        global stopFlag; stopFlag = False # Global Flag to control continuous recording, controllable outside the function
        filename = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".wav" # Filename for the recorded audio is the current date and time
        filePath = resourcePath(f"Contents/Recordings/{filename}") # Filepath for the recorded audio

        with wave.open(filePath, 'wb') as fileObject:
            stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True, input_device_index=deviceIndex)

            frames = []  # Initialize array to store frames
            print('RECORDING STARTED')
            
            while True:
                data = stream.read(chunk).hex() # Read the data and convert it to hex
                filteredData = b''.join([bytes.fromhex(data[i:i+12]) for i in range(0, len(data), 192)]) # Filter the data to remove the extra empty bytes
                frames.append(filteredData) # Append the filtered data to the frames array
                
                if stopFlag or len(frames) > int(fs / chunk * maxSeconds): # if the stopFlag is True or the length of frames is greater than max recording length, stop recording
                    break
            
            # for i in range(0, int(fs / chunk * seconds)):
            #     data = stream.read(chunk).hex()
            #     filteredData = b''.join([bytes.fromhex(data[i:i+12]) for i in range(0, len(data), 192)])
            #     frames.append(filteredData)

            # Stop and close the stream 
            stream.stop_stream()
            stream.close()
            # Terminate the PortAudio interface
            p.terminate()
            print('FINISHED RECORDING')
            # Set up the wave file and write the data
            fileObject.setnchannels(2)
            fileObject.setsampwidth(p.get_sample_size(sample_format))
            fileObject.setframerate(fs)
            fileObject.writeframes(b''.join(frames))
            fileObject.close()