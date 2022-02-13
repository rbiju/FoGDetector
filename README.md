# FoGDetector
The FoGDetector is a system designed for the detection of Freezing of Gait in those with Parkinson's, designed to work as cheaply and dicreetly as possible so as to not interfere in the life of the user.

Data is collected via a waist-mounted IMU, collecting shank (z-axis) acceleration, which is then sent in chunks to the post processing algorithm. Then, frequency features are extracted via a spectrogram, which are then passed to an LSTM network for real time classification occuring every ~1 second.
An AUC of 0.93 under test conditions (normal day to day movement with simulated FoG) is competitive with state of the art approaches. Validation with real patients has not yet been perforned.

Contact me at raymondbiju@gmail.com with any questions!
