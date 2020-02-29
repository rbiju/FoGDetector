#include "MPU9250.h"
#include "SoftwareSerial.h"
#include "Queue.h" //by Einar Arnason
#include "MemoryUsage.h"

//Y AXIS

// pin 9 - Serial clock out (SCLK)
// pin 8 - Serial data out (DIN)
// pin 4 - RX from Bluetooth
// pin 5 - TX to Bluetooth

#define AHRS true         // Set to false for basic data read
#define SerialDebug true // Set to true to get Serial output for debugging


// Pin definitions
int intPin = 12;  // These can be changed, 2 and 3 are the Arduinos ext int pins
int myLed  = 13;  // Set up pin 13 led for toggling
int dQlength = 600;  //Spec needs 500 points at least
int bQlength = 500; //Want this to be approx 0.50s
int numPieces = 3; //needs to divide dQlength evenly, its not pretty but its 3am and I want to fucking die and I'm not editing the fucking source code to increase the fucking buffer size
int counter = 0;
unsigned long time_start; //for use in generating time values to send with accel data

#define I2Cclock 400000
#define I2Cport Wire
#define MPU9250_ADDRESS MPU9250_ADDRESS_AD0   // Use either this line or the next to select which I2C address your device is using
//#define MPU9250_ADDRESS MPU9250_ADDRESS_AD1


MPU9250 myIMU(MPU9250_ADDRESS, I2Cport, I2Cclock);
DataQueue<float> dataQueue(dQlength);
DataQueue<float> tempQueue(dQlength);


void setup()
{
  Wire.begin();
  // TWBR = 12;  // 400 kbit/sec I2C speed
  Serial.begin(57600);
  Serial1.begin(57600);
  Serial1.println("Ready!!");

  // Set up the interrupt pin, its set as active high, push-pull
  pinMode(intPin, INPUT);
  digitalWrite(intPin, LOW);
  pinMode(myLed, OUTPUT);
  digitalWrite(myLed, HIGH);

  // Read the WHO_AM_I register, this is a good test of communication
  byte c = myIMU.readByte(MPU9250_ADDRESS, WHO_AM_I_MPU9250);
  Serial.print(F("MPU9250 I AM 0x"));
  Serial.print(c, HEX);
  Serial.print(F(" I should be 0x"));
  Serial.println(0x71, HEX);

  if (c == 0x71) // WHO_AM_I should always be 0x71
  {
    Serial.println(F("MPU9250 is online..."));

    // Start by performing self test and reporting values
    myIMU.MPU9250SelfTest(myIMU.selfTest);
    Serial.print(F("x-axis self test: acceleration trim within : "));
    Serial.print(myIMU.selfTest[0], 1); Serial.println("% of factory value");
    Serial.print(F("y-axis self test: acceleration trim within : "));
    Serial.print(myIMU.selfTest[1], 1); Serial.println("% of factory value");
    Serial.print(F("z-axis self test: acceleration trim within : "));
    Serial.print(myIMU.selfTest[2], 1); Serial.println("% of factory value");
    Serial.print(F("x-axis self test: gyration trim within : "));
    Serial.print(myIMU.selfTest[3], 1); Serial.println("% of factory value");
    Serial.print(F("y-axis self test: gyration trim within : "));
    Serial.print(myIMU.selfTest[4], 1); Serial.println("% of factory value");
    Serial.print(F("z-axis self test: gyration trim within : "));
    Serial.print(myIMU.selfTest[5], 1); Serial.println("% of factory value");
    FREERAM_PRINT;

    // Calibrate gyro and accelerometers, load biases in bias registers
    myIMU.calibrateMPU9250(myIMU.gyroBias, myIMU.accelBias);

    myIMU.initMPU9250();
    Serial.println("MPU9250 initialized for active data mode....");
    myIMU.getAres();
    myIMU.getGres();
    myIMU.getMres();

  } // if (c == 0x71)
  else
  {
    Serial.print("Could not connect to MPU9250: 0x");
    Serial.println(c, HEX);

    // Communication failed, stop here
    Serial.println(F("Communication failed, abort!"));
    Serial.flush();
    abort();
  }
  time_start = millis();
}

//MY Functions


//prints queue to BT as comma separated string

void printQueue() {
  Serial1.println("Start");
  Serial.println("Start");
  for(int i = 0; i < numPieces; i++){
    int counter1 = 0;
    String BTmessage = "";
    boolean flag = true;
    while (flag) {
      float temp = dataQueue.dequeue();
      BTmessage.concat(temp);
      BTmessage.concat(",");
      dataQueue.enqueue(temp);
      counter1++;
      if (counter1 == dQlength / numPieces) {
        flag = false;
      }
    }
  Serial1.println(BTmessage);
  //Serial.println(BTmessage);
  }
  Serial1.println("End");
  Serial.println("End");
}

void loop()
{
  if (myIMU.readByte(MPU9250_ADDRESS, INT_STATUS) & 0x01)
  {
    myIMU.readAccelData(myIMU.accelCount);  // Read the x/y/z adc values
    myIMU.ax = (float)myIMU.accelCount[0] * myIMU.aRes; // - myIMU.accelBias[0];
    myIMU.ay = (float)myIMU.accelCount[1] * myIMU.aRes; // - myIMU.accelBias[1];
    myIMU.az = (float)myIMU.accelCount[2] * myIMU.aRes; // - myIMU.accelBias[2];
  } // if (readByte(MPU9250_ADDRESS, INT_STATUS) & 0x01)

  if (!AHRS)
  {
    Serial.println("Switch AHRS");
  } // if (!AHRS)

  else
  {
    // Serial print and/or display at 0.5 s rate independent of data rates
    myIMU.delt_t = millis() - myIMU.count;
    // collect data once per 10ms independent of read rate
    if (myIMU.delt_t > 1)
    {
      if (SerialDebug)
      {
        // MAIN SHIT

        if (dataQueue.item_count() == dQlength) {
          if (counter == bQlength) {
            tempQueue = dataQueue;
            printQueue();
            counter = 0;
            Serial.println("");
          }
          else {
            float junk = dataQueue.dequeue();
            dataQueue.enqueue(1000 * myIMU.az);
            counter++;
          }
        }
        else {
          dataQueue.enqueue(1000 * myIMU.az);
          Serial.println(1000 * myIMU.az);
        }
      }
      myIMU.count = millis();
      myIMU.sumCount = 0;
      myIMU.sum = 0;

    } // if (myIMU.delt_t > 500)
  } // if (AHRS)
}
