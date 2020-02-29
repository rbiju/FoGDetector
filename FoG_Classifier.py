import keras
from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential
from keras.callbacks import TensorBoard
import sklearn
from sklearn.metrics import roc_curve,auc
import numpy as np
from numpy import savetxt
import skimage
from skimage import io
from skimage.transform import resize
from matplotlib import pyplot as plt
import os

ROOT_PATH = '/Users/ray/Documents/5th_Semester/BMED_2250/Data20191128/Spectrograms'
train_data_directory = os.path.join(ROOT_PATH, 'Training')
test_data_directory = os.path.join(ROOT_PATH, 'Testing')


#takes in data from directory and contstructs parallel image and label arrays
def load_data(data_directory):
    directories = [d for d in os.listdir(data_directory)
                   if os.path.isdir(os.path.join(data_directory,d))]
    labels = []
    images = []

    for d in directories:
        curr_folder = os.path.join(data_directory, d)
        spec_names = os.listdir(os.path.join(curr_folder))
        #filters out weird files
        spec_names = [s for s in spec_names
                      if not('_' in s)]

        temp = [x.split('.')[0] for x in spec_names]
        temp_labels = [int(x.split('-')[0]) for x in temp]
        nums = [int(x.split('-')[1]) for x in temp]

        zipped = zip(nums, temp_labels, spec_names)
        zipped = sorted(zipped)
        zipped.pop(0)
        fnames = [x[2] for x in zipped]

        temp_labels = np.array([x[1] for x in zipped])
        temp_labels = [n-1 for n in temp_labels]
        temp_images = np.array([skimage.io.imread(os.path.join(curr_folder,f), as_gray=True) for f in fnames])
        temp_images = [resize(i,(28,28), anti_aliasing=True) for i in temp_images]

        labels.extend(temp_labels)
        images.extend(temp_images)

    return np.array(labels), np.array(images)


train_labels, train_images = load_data(train_data_directory)
test_labels, test_images = load_data(test_data_directory)

print(train_labels.shape)
print(train_images.shape)

print("Modeling!")

"""neural network:
2 LSTM layers for RNN functionality
2 output neurons"""

#tensorboard callback for visualization
tensorboard = TensorBoard(log_dir='./logs', histogram_freq=1,
                          write_graph=False, write_images=False)

model = Sequential()
model.add(LSTM(72, input_shape = (28,28), activation = 'relu', return_sequences=True))
model.add(Dropout(0.1))

model.add(LSTM(72, activation = 'relu'))
model.add(Dropout(0.1))

model.add(Dense(32, activation = 'relu'))
model.add(Dropout(0.1))

model.add(Dense(32, activation = 'relu'))
model.add(Dropout(0.1))

model.add(Dense(2, activation = 'softmax'))

opt = keras.optimizers.Adam(lr=1e-3, decay=1e-5)

model.compile(loss='sparse_categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

#model.fit(train_images, train_labels, epochs=3, validation_data=(test_images, test_labels), callbacks=[tensorboard])
model.fit(train_images, train_labels, epochs=4, callbacks=[tensorboard])
model.save('FoG_Classifier.h5')

#getting confidence values for positive node to feed to ROC
predictions = model.predict(test_images)
predictions = predictions[:,1]
data = np.vstack((predictions, test_labels))

savetxt('ROCdata.csv', data, delimiter=',')
fpr_keras, tpr_keras, thresholds_keras = roc_curve(test_labels, predictions)
auc_keras = auc(fpr_keras, tpr_keras)

#launch tensorboard
#tensorboard --logdir /Users/ray/Documents/5th_Semester/BMED_2250/PHASE3/logs

plt.figure(1)
plt.plot([0, 1], [0, 1], 'k--')
plt.plot(fpr_keras, tpr_keras, label='Keras (area = {:.3f})'.format(auc_keras))
plt.title('FoG Classifier ROC')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.savefig('ROC.png')
plt.show()

