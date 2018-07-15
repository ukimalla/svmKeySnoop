from pyAudioAnalysis import audioSegmentation as aS
[flagsInd, classesAll, acc, CM] = aS.mtFileClassification("keys.wav", "svmTaps", "svm", True)