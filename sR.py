from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import audioSegmentation as aS
[Fs, x] = aIO.readAudioFile("keys.wav")
segments = aS.silenceRemoval(x, Fs, 0.010, 0.020, smoothWindow = 0.02, Weight = 0.3, plot = True)