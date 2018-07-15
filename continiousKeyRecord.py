import pyaudio
import random
import time
import os
import wave
import threading
from pynput import keyboard
import numpy as np
from pydub import AudioSegment



# Function to start data collection
def startDataCollection():
    global keyPressed
    global keyPressedFlag
    global keyTimeStampList
    global keyList
    global endOfRecording

    endOfRecording = False

    keyTimeStampList = []
    keyList = []

    keyPressed = keyboard.Key.tab
    keyPressedFlag = True

    time.sleep(0.1)

    list = keyboard.Listener(on_press=on_press)
    list2 = keyboard.Listener(on_release=on_release)

    recThread = startRecording()
    recThread.start()
    #list.start()
    list2.start()
    #list.join()
    list2.join()





def on_press(key):
    global keyPressedFlag
    global keyPressed
    global endOfRecording


    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
    print('Key pressed: ' + k)
    keyPressed = k
    keyPressedFlag = True
    if key == keyboard.Key.ctrl:
        return False  # stop listener
    elif recordStartTime != None:
        timeStamp = time.time() - recordStartTime
        keyTimeStampList.append(str(timeStamp) + "," + k)


def on_release(key):
    global keyPressedFlag
    global keyPressed
    global recordStartTime
    global keyTimeStampList
    global keyList
    global endOfRecording

    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys

    if k != None:
        try:
            k = str(k).lower()
            print('Key pressed: ' + str(k))
            keyPressed = k
            keyPressedFlag = True
            if key == keyboard.Key.esc or endOfRecording:
                return False  # stop listener
            elif recordStartTime != None:
                timeStamp = time.time() - recordStartTime
                keyTimeStampList.append(str(timeStamp))
                if k == ',':
                    keyList.append("comma")
                else:
                    keyList.append(k)

        except:
            print str(key) + "was pressed, and recorded as cmd combo."
            timeStamp = time.time() - recordStartTime
            keyTimeStampList.append(str(timeStamp))
            keyList.append("cmd combo")




class startRecording(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        # Initializing global variables
        global keyPressedFlag
        global keyPressed
        global recordStartTime
        global keyTimeStampList
        global keyList
        global endOfRecording


        # Setting audio recording parameters

        CHUNK = 512
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 8100
        RECORD_SECONDS = 1
        CSV_CHUNK = 512

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        output=True,
                        frames_per_buffer=CHUNK)

        frames = []

        print "Starting recording."

        recordStartTime = time.time()

        print "Calculations"
        print int(RATE * RECORD_SECONDS / CHUNK)

        while keyPressed != 'esc':
        # for i in range(0, int(RATE * RECORD_SECONDS / CHUNK)):
            try:
                data = stream.read(CHUNK)
                frames.append(data)
            except:
                print "Exception Occurred. Possible Overflow."
                break

        endOfRecording = True
        print "Stopped recording."

        print "Frames Length:"
        print len(frames)
        audiofile = AudioSegment(data=b''.join(frames), sample_width=2, frame_rate=RATE, channels=1)
        data = np.fromstring(audiofile._data, np.int16)


        print "Data length:"
        print len(data)
        print data


        stream.stop_stream()
        stream.close()
        p.terminate()

        # Generating random filename
        randomFileName = str((random.random() * 100) * (random.random() * 100))
        WAVE_OUTPUT_FILENAME = randomFileName + ".wav"
        LABALED_CHUNK_FILENAME = randomFileName + ".csv"
        TIME_STAMP_FILENAME = randomFileName + ".txt"

        # Writing data file
        writeDataKeyList(data, LABALED_CHUNK_FILENAME, CHUNK=CSV_CHUNK, insertHeader=True)
        writeTimeStampKeyList(TIME_STAMP_FILENAME)
        writeOnlyKeyList(randomFileName + "keys.txt")

        # Writing wav file
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()


        print "WAV file saved as " + WAVE_OUTPUT_FILENAME
        print "Data file saved as " + TIME_STAMP_FILENAME
        print "Labeled Chunk saved as " + LABALED_CHUNK_FILENAME

        DATA_FILE_FOLDER = "data"

        if not os.path.exists(DATA_FILE_FOLDER):
            os.mkdir(str(DATA_FILE_FOLDER))

        # os.rename(WAVE_OUTPUT_FILENAME, "keys/" + surfacePointName + "/" +  WAVE_OUTPUT_FILENAME)
        os.rename(WAVE_OUTPUT_FILENAME, DATA_FILE_FOLDER + "/" + WAVE_OUTPUT_FILENAME)
        os.rename(TIME_STAMP_FILENAME, DATA_FILE_FOLDER + "/" + TIME_STAMP_FILENAME)
        os.rename(LABALED_CHUNK_FILENAME, DATA_FILE_FOLDER + "/" + LABALED_CHUNK_FILENAME)

        return




def writeDataKeyList(data, filename, RATE = 8100,  CHUNK = 32, insertHeader = False):
    global keyTimeStampList
    global keyList

    outData = []
    chunkVal = None


    # Generating CSV header
    if insertHeader:
        header = ""
        for i in range(0, CHUNK):
            header += '"var' + str(i) + '",'
        header += '"input"\n'

        outData.append(header)
    


    # Formatting data into size of CHUNKS
    i = 0

    for x in data:
        if i > CHUNK - 1:
            outData.append(chunkVal)
            i = 0
            chunkVal = None
        if not chunkVal:
            chunkVal = str(x) + ","
        else:
            chunkVal = chunkVal + str(x) + ","
        i += 1

    # Handling the last chunk
    outData.append(chunkVal)

    prevDataIndex = -1
    # Inserting key values into right chunks
    for i in range(0, len(keyTimeStampList) - 1):
        timeStamp = float(keyTimeStampList[i])
        key = keyList[i]
        dataIndex = int(RATE * timeStamp / CHUNK)
        if dataIndex !=prevDataIndex:
            print "Data Index"
            print dataIndex
            # If the key was input before recording ended
            if dataIndex < len(outData) - 1:
                outData[dataIndex] = outData[dataIndex] + '"' + str(key) + '"\n'
        else:
            print "Keys were probably pressed too fast. Same data index detected."
        prevDataIndex = dataIndex

    # Filling with "NONE" for empty chunks
    i = 0
    for x in outData:
        if x[-1:] == ",":
            outData[i] = outData[i] + '"NONE"\n'
        i += 1

    dataFile = open(filename, "w")
    dataFile.writelines(outData)
    dataFile.close()


def writeTimeStampKeyList(filename):
    global keyTimeStampList
    global keyList

    outData = []

    # Combining keyTImeStampList and keyList to string list of outData
    for i in range(0, len(keyTimeStampList) - 1):
        timeStamp = float(keyTimeStampList[i])
        key = keyList[i]
        # If the key was input before recording ended
        outData.append(str(timeStamp) + " " + key + "\n")

    dataFile = open(filename, "w")
    dataFile.writelines(outData)
    dataFile.close()

def writeOnlyKeyList(filename):

    global keyList
    outputStr = ""
    keysss = set(keyList)
    for x in keysss:
        outputStr += "'" + x + "', "
    outputStr += "'NONE'"

    dataFile = open(filename, "w")
    dataFile.writelines(outputStr)
    dataFile.close()















