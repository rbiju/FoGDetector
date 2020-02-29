import time
import matplotlib
import serial
from scipy import signal
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import skimage
from skimage import io
from skimage.transform import resize
import numpy as np
from keras.models import load_model
from pysine import sine

MODEL_PATH = '/Users/ray/Documents/5th_Semester/BMED_2250/PHASE3/FoG_Classifier.h5'
ROOT_PATH = '/Users/ray/Documents/5th_Semester/BMED_2250/Spectrograms'
MACHINE_GUESS = 0

model = load_model(MODEL_PATH)
model.summary()

dataStart = False
dataEnd = False
port="/dev/tty.HC-06-DevB"
ser = serial.Serial(port, baudrate=57600)

time.sleep(0.1)
print("Connected")
ser.flushInput()
vals = []

picCounter = 0

fs = 475

def ifnFoG():
    sine(frequency=440.0, duration=0.05)

def ifFoG():
    sine(frequency=587.33, duration=0.05)

while True:
    try:
        ser_bytes = ser.readline()
        time.sleep(1/(1000000))
        try:
            decoded_bytes = ser_bytes.decode()
            dataFlag = (decoded_bytes[0:len(decoded_bytes)-2])

            if dataFlag == 'Start':
                dataEnd = False
                dataStart = True
            elif dataFlag == 'End':
                dataEnd = True
            else:
                if dataStart and not dataEnd: #if only start has been received
                    print("Appending data")
                    temp = decoded_bytes.split(",")
                    temp = temp[0:len(temp)-1]
                    vals = vals + temp #add data fragment to vals
                else: #bullshit in the beginning
                    dataEnd = False
                    continue

            if dataEnd and dataStart:  # if 'end' preceded by 'start' has been received, this is where spectro/ML stuff should go
                try:
                    vals = list(map(float, vals))
                    print(vals)
                    print(len(vals))

                    #spectrogram generation
                    x = np.array(vals)
                    f, t, Sxx = signal.spectrogram(x, fs, noverlap=20)
                    plt.pcolormesh(t, f, Sxx)
                    plt.ylabel('Frequency [Hz]')
                    plt.xlabel('Time [sec]')
                    plt.axis('off')
                    axes = plt.gca()
                    axes.set_position([0, 0, 1, 1])
                    axes.set_ylim([0, 30])

                    #spectrogram saving
                    directory = ROOT_PATH + "/" + str(picCounter) + ".png"
                    plt.savefig(directory)
                    print("Fig saved to " + directory)
                    picCounter += 1

                    vals = []  # clear vals for next burst
                    x = np.array(vals)
                    dataStart = False
                    dataEnd = False

                    #ML part
                    #pic collection and resizing/normalizing
                    temp_img = skimage.io.imread(directory, as_gray=True)
                    img = resize(temp_img,(28,28), anti_aliasing=True)
                    img = np.reshape(img, (1,28,28))
                    prediction = model.predict(img)
                    #MACHINE_GUESS = np.argmax(prediction)
                    MACHINE_GUESS = prediction[0][1]

                    print("Guessed")
                    if MACHINE_GUESS >= 0.416:
                        ifFoG()
                    else:
                        ifnFoG()

                except Exception as exc:
                    print(exc)
            time.sleep(1/10000000)
        except:
            print("Could not print to console")
            continue
    except Exception as inst:
        print(inst)
        break
