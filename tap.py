# IMPORTS:
import sys
import pyaudio
import time
import random
import os
import wave
import thread
from pyAudioAnalysis import audioTrainTest as aT
import threading
import time
from pydub import AudioSegment
import numpy
import Queue
from os import listdir
from os.path import isfile, join
from pynput import keyboard

from scipy import signal
import matplotlib.pyplot as plt

# Thread Control
lo = threading.Lock()
onlyfiles = []


# On press
def on_press(key):
    global keyPressedFlag
    global keyPressed
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
    if key == keyboard.Key.esc:
        keyPressedFlag = True  # stop listener
        return False

    # if k in ['1', '2', 'left', 'right']: # keys interested
    # self.keys.append(k) # store it in global-like variable
    # print('Key pressed: ' + k)


# Thread Class to play Audio segment
class playThread(threading.Thread):
    def __init__(self, file):
        threading.Thread.__init__(self)
        self.file = file

    def run(self):
        CHUNK = 1024

        wf = wave.open(self.file, 'rb')

        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK)

        while data != '':
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()

        p.terminate()


# Thread Class to queue record stream
class recordQThread(threading.Thread):
    def __init__(self, frames=[]):
        threading.Thread.__init__(self)
        self.frames = frames

    def run(self):
        global q
        RATE = 44100
        audiofile = AudioSegment(data=b''.join(self.frames), sample_width=2, frame_rate=RATE, channels=2)
        data = numpy.fromstring(audiofile._data, numpy.int16)

        len(data)

        x = []
        for chn in xrange(audiofile.channels):
            x.append(data[chn::audiofile.channels])
        x = numpy.array(x).T
        # print "X: " + str(len(x))

        lo.acquire()
        # print "Q: " + str(q.qsize())
        q.put(x)
        lo.release()


# Thread Class to record Audio Segment
class recordThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global q
        global keyPressedFlag
        global keyPressed
        keyPressedFlag = False
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 5
        WAVE_OUTPUT_FILENAME = "output.wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        output=True,
                        frames_per_buffer=CHUNK)

        # print("* HIT!")
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        recordQThread(frames).start()

        while True:
            # print "Frames: " + str(len(frames))
            frames.remove(frames[0])
            data = stream.read(CHUNK)
            frames.append(data)

            recordQThread(frames).start()

            '''audiofile = AudioSegment(data=b''.join(frames),sample_width=2,frame_rate=RATE,channels=2)
            data = numpy.fromstring(audiofile._data, numpy.int16)
            x = []
            for chn in xrange(audiofile.channels):
                x.append(data[chn::audiofile.channels])
            x = numpy.array(x).T

            lo.acquire()
            q.put(x)
            lo.release()'''

            if keyPressedFlag:
                break
        # print "Exiting " + self.name


def ConvertToImage():
    # Recording parameters
    CHUNK = 2048
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 22050
    RECORD_SECONDS = 0.5

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=CHUNK)

    frames = []
    for i in range(0, int(RATE * RECORD_SECONDS) / CHUNK):
        data = stream.read(CHUNK)
        frames.append(data)


    audiofile = AudioSegment(data=b''.join(frames), sample_width=2, frame_rate=RATE, channels=2)
    print "audiofile!!!"

    print audiofile.get_array_of_samples()

    # data = numpy.fromstring(audiofile._data, numpy.int16)

    import pylab
    data = pylab.fromstring(audiofile._data, 'int16')

    print data


    f, t, Sxx = signal.spectrogram(data, 22050)
    plt.pcolormesh(t, f, Sxx)
    plt.ylim(0, 8000)
    plt.axis('off')
    plt.axis()
    plt.tight_layout(0,0,0)
    plt.savefig("test.png")
    plt.show()


def ReadWavFile():
    from scipy.io import wavfile

    # To add gain
    ''' audioFile = AudioSegment.from_wav('q/7548.123441052.wav')
        audioFile += 20
        samples = numpy.array(audioFile.get_array_of_samples().tolist())
        samples_rate = 441000 '''

    sample_rate, samples = wavfile.read('q/7548.123441052.wav')

    # Spectrogram
    fig,ax = plt.subplots(1)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis('off')

    pxx, freqs, bins, im = plt.specgram(x=samples, Fs=sample_rate, noverlap=384, NFFT=512)

    ax.axis('off')
    fig.savefig('sp_xyz.png', frameon='false')

    # Color Mesh
    fig, ax = plt.subplots(1)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis('off')

    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
    plt.pcolormesh(times, frequencies, spectrogram)

    plt.ylim(0, 8000)
    # plt.xlim(0, 0.5)
    ax.axis('off')
    fig.savefig('test1.png', dpi = 100, frameon='false')

def ReadWavFile2():
    from scipy.io import wavfile

    audioFile = AudioSegment.from_wav('q/7548.12344105.wav')
    audioFile += 0
    samples = numpy.array(audioFile.get_array_of_samples().tolist())

    sample_rate, _ = wavfile.read('q/7548.12344105.wav')

    # Spectrogram
    fig,ax = plt.subplots(1)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis('off')

    pxx, freqs, bins, im = plt.specgram(x=samples, Fs=sample_rate, noverlap=384, NFFT=512)

    ax.axis('off')
    fig.savefig('sp_xyz.png', frameon='false')

    # Color Mesh
    fig, ax = plt.subplots(1)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis('off')

    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
    plt.pcolormesh(times, frequencies, spectrogram)

    plt.ylim(0, 8000)
    # plt.xlim(0, 0.5)
    ax.axis('off')
    fig.savefig('test2.png', dpi=100, frameon='false')



# Thread Class to Analyse Audio Segment
class analyseThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global q
        global keyPressedFlag
        global keyPressed
        keyPressedFlag = False
        flagStart = False

        while True:
            lo.acquire()

            while not q.empty():
                f = q.get()
                x = aT.fileClassification(f, "svmTaps", "svm")
                q.task_done()
                flagStart = True
                if flagStart:
                    flagStart = False

                    onlyObj = [f for f in
                    listdir('.') if not isfile(join('.', f))]
                    # onlyObj.remove("drums")
                    onlyObj.remove("pyAudioAnalysis")
                    onlyObj.remove("images")
                    counter = len(onlyObj)

                    for i in range(0, counter):
                        if (float(x[1][i]) > 0.5) and (float(x[1][i]) < 0.99):
                            Sens = x[2][i]
                        else:
                            Sens = "NOISE"
                        if (Sens != "NOISE"):
                            print Sens
                            print x[1]
                if keyPressedFlag: break
            lo.release()


##############
##############
# MAIN FUNCTION:

def mainTap(ch):
    recordKey().start()
    onlyfiles = [f for f in listdir('.') if not isfile(join('.', f))]
    # onlyfiles.remove("drums")
    onlyfiles.remove("pyAudioAnalysis")
    onlyfiles.remove("images")

    global q
    global keyPressedFlag
    keyPressedFlag = False
    q = Queue.Queue(0)

    # ch = A (start Thread for drums) | B (Record new Data) | C (Start Thread for LaunchPad)
    if (str(ch) == 'A'):

        aT.featureAndTrain(onlyfiles, 1.0, 1.0, aT.shortTermWindow, aT.shortTermStep, "svm", "svmTaps", False)
        startMode = True

    elif (str(ch) == 'B'):
        ch = 'x'
        surfaceName = raw_input("Surface Name: ")
        while (surfaceName != 'x'):
            numberOfInputs = raw_input("Number of Data Points: ")
            for i in range(0, int(numberOfInputs)):
                print "Input " + str(i + 1)
                addSurfacePoint(surfaceName)
            surfaceName = raw_input("Surface Name: ")

    if (startMode):
        recordThread().start()
        analyseThread().start()
        analyseThread().start()
        while not keyPressedFlag:
            time.sleep(0.1)


def addSurfacePoint(surfacePointName):
    print "Starting Record"
    recordSurfacePoint(surfacePointName)


def recordSurfacePoint(surfacePointName):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 0.9
    randomFileName = str((random.random() * 100) * (random.random() * 100))
    WAVE_OUTPUT_FILENAME = randomFileName + ".wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=CHUNK)

    print("* Recording in ")
    print (".. 2")
    time.sleep(0.2)
    print (".. 1")
    time.sleep(0.2)
    print ("Tap!")
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    if not os.path.exists(surfacePointName):
        os.mkdir(str(surfacePointName))

    os.rename(WAVE_OUTPUT_FILENAME, surfacePointName + "/" + WAVE_OUTPUT_FILENAME)


class recordKey(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        lis = keyboard.Listener(on_press=on_press)
        lis.start()  # start to listen on a separate thread
        lis.join()  # no this if main thread is polling self.keys
