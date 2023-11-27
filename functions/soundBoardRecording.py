import pyaudio
import wave
import time

p = pyaudio.PyAudio()  # Create an interface to PyAudio

def findDeviceIndex(searchTerm: str):
    found = -1

    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        name = device['name'].encode('utf-8')
        print(f"Index: {i} - {name}, Input CHs: {device['maxInputChannels']}, Output CHs: {device['maxOutputChannels']}")

        if name.lower().find(searchTerm) >= 0 and device['maxInputChannels'] > 0:
            found = i
            break
    return found

def listAudioDevices():
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print(f"Input Device id {i} - {p.get_device_info_by_host_api_device_index(0, i).get('name')}, Channels: {p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')}")

def recordAudio():
    deviceIndex = findDeviceIndex(b'qu-24')
    if deviceIndex < 0:
        print('QU-24 is not Connected!')
    else:
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt24  # 24 bits per sample
        channels = 32 #p.get_device_info_by_index(deviceIndex)['maxInputChannels']
        fs = 48000  # Record at 48000 samples per second
        seconds = 10
        filename = "test3.wav"

        with wave.open(filename, 'wb') as fileObject:
            stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True, input_device_index=deviceIndex)

            frames = []  # Initialize array to store frames
            print('RECORDING LIL BRO')
            # Store data in chunks for X seconds
            '''
            t = time.time()
            while time.time() < t + 5:
                data = stream.read(chunk)
                frames.append(data)
            '''
            for i in range(0, int(fs / chunk * seconds)): #Might have to change to while loop for continuous recording until exception
                data = stream.read(chunk).hex()
                #frames.append(data)
                #stream.write(data) #send the data back to the stream to output through speakers

                filteredData = b''.join([bytes.fromhex(data[i:i+12]) for i in range(0, len(data), 192)])

                frames.append(filteredData)

            # Stop and close the stream 
            stream.stop_stream()
            stream.close()
            # Terminate the PortAudio interface
            p.terminate()
            print('FINISHED LIL BRO')
            fileObject.setnchannels(2)
            fileObject.setsampwidth(p.get_sample_size(sample_format))
            fileObject.setframerate(fs)
            fileObject.writeframes(b''.join(frames))
