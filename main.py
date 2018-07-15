from tap import mainTap
from rK import recordKey
from tap import ConvertToImage
from tap import ReadWavFile, ReadWavFile2
from continiousKeyRecord import startDataCollection
from audioToImage import generateImageFromFiles
import os

def main():

	#clear screen for windows
	os.system("cls")
	
	print "1. Train and Start"
	print "2. Record Surface"
	print "3. Record Keys"
	print "4. Conver to Image"
	print "5. Read Wav File"
	print "6. Generate PColormesh"
	print "7. Generate Spectrogram"
	print "8. Generate PColormesh and Spectrogram"
	print "9. Continious Key Record"
	print "0. Exit"


	while True:
		ch = input("Enter your option ")
		if(ch == 1):
			mainTap('A')
		elif(ch == 2):
			mainTap('B')
		elif(ch == 3):
			recordKey()
		if(ch == 4):
			ConvertToImage()
		elif(ch==5):
			ReadWavFile()
			ReadWavFile2()
		elif(ch==6):
			generateImageFromFiles(True, False)
		elif(ch==7):
			generateImageFromFiles(False, True)
		elif(ch==8):
			generateImageFromFiles(True, True)
		elif(ch==9):
			startDataCollection()
		elif(ch == 0):
			print "Goodbye!"
			break
		else:
			print "Invalid Input. Please Try Again. "

if __name__ == '__main__':
	main()