from scipy.io import wavfile
from pydub import AudioSegment
from matplotlib import pyplot as plt
from scipy import signal
import numpy as np

from os import mkdir
from os import listdir
from os.path import isfile, join, exists




def WavToSpectroGram(input_file, gain, output_file):
    # To add gain
    audio_file = AudioSegment.from_wav(input_file)
    audio_file += gain
    samples = np.array(audio_file.get_array_of_samples().tolist())


    sample_rate, _ = wavfile.read(input_file)

    # Spectrogram
    fig,ax = plt.subplots(1)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis('off')

    pxx, freqs, bins, im = plt.specgram(x=samples, Fs=sample_rate, noverlap=384, NFFT=512)

    ax.axis('off')
    fig.savefig(output_file, frameon='false')

def WavToPcolormesh(input_file, gain, output_file):
    # To add gain
    audio_file = AudioSegment.from_wav(input_file)
    audio_file += gain
    samples = np.array(audio_file.get_array_of_samples().tolist())

    sample_rate, _ = wavfile.read(input_file)

    # Color Mesh
    fig, ax = plt.subplots(1)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis('off')

    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
    plt.pcolormesh(times, frequencies, spectrogram)

    plt.ylim(0, 8000)
    ax.axis('off')
    fig.savefig(output_file, dpi=50, frameon='false')




def generateImageFromFiles(output_colormesh, output_spectrogram):
    # Path declaration
    colormeshPath = '../../colorMesh/'
    spectrogramPath = '../../spectrograms/'



    # For PColorMesh
    if(output_colormesh == True):
        print "Starting PColorMesh Conversion"

        fileCounter = 0
        folderList = [f for f in listdir('.') if not isfile(join('.', f))]

        # Creating colormesh folder
        if not exists(colormeshPath):
            mkdir(colormeshPath)

        # Iterating through all the folders
        for folder in folderList:
            if not exists(colormeshPath + folder):
                mkdir(colormeshPath + folder)
            audioFileList = listdir(folder)

            # Iterating through all the files in the folder
            for audioFile in audioFileList:
                # If it is a .wav file
                if audioFile[-4:] == '.wav':
                    print "Converting " + folder + '/' + audioFile + " to PColorMesh."
                    audioFilePath = folder + '/' + audioFile
                    WavToPcolormesh(folder + '/' + audioFile, 0, colormeshPath + folder + '/' + audioFile + '.png')
                    fileCounter += 1

        print "PColorMesh conversion complete. \n" \
              "%d WAV files were successfully converted to PColorMesh." % (fileCounter)



    # For Spectrogram
    if (output_spectrogram == True):
        print "Starting Spectrogram Conversion"
        fileCounter = 0

        folderList = [f for f in listdir('.') if not isfile(join('.', f))]

        # Creating spectrogram folder
        if not exists(spectrogramPath):
            mkdir(spectrogramPath)

        # Iterating through all the folders
        for folder in folderList:
            if not exists(spectrogramPath + folder):
                mkdir(spectrogramPath + folder)
            audioFileList = listdir(folder)

            # Iterating through all the files in the folder
            for audioFile in audioFileList:
                # If it is a .wav file
                if audioFile[-4:] == '.wav':
                    print "Converting " + folder + '/' + audioFile + " to spectrogram."
                    audioFilePath = folder + '/' + audioFile
                    WavToSpectroGram(audioFilePath, 0, spectrogramPath + audioFilePath + '.png')
                    fileCounter += 1

    print "Spectrogram conversion complete! \n" \
          "%d WAV files were successfully converted to spectrograms." % (fileCounter)

    print "All Conversions Complete!"



