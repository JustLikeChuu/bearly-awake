// int buttonpin = 12; // define D0 Sensor Interface
int soundValue = 0;// define numeric variables val
int soundIn;

int readSound(int soundIn){
    soundValue = analogRead(soundIn); // Read the analog value from the Sound Sensor
    return soundValue;
}

// Load below code to run standalone sound sensor test
//
// void setup ()
// {
//   Serial.begin(9600);
// }
//
// void loop() {
//     int soundValue = analogRead(buttonpin); // Read the analog value from the Sound Sensor
  
//     // Display the sound sensor value on the Serial Monitor
//     // Serial.print("Sound Level: ");
//     Serial.println(soundValue);

//     delay(100);
// }
