#include <OneWire.h>
#include <DallasTemperature.h>

// #define ONE_WIRE_BUS 17 // Digital pin connected to the Data pin of the sensor

// OneWire oneWire(ONE_WIRE_BUS);
// DallasTemperature sensors(&oneWire);
int readTemp(int tempIn){
  OneWire oneWire(tempIn);
  DallasTemperature sensors(&oneWire);
  sensors.requestTemperatures();
  float temperatureC = sensors.getTempCByIndex(0);

  return temperatureC;
}

// Load below code to run standalone temperature sensor test
//
// void setup() {
//   Serial.begin(9600); // Initialize serial communication for debugging (optional)
//   sensors.begin();
// }

// void loop() {
//   sensors.requestTemperatures(); // Request temperature reading
//   float temperatureC = sensors.getTempCByIndex(0); // Get the temperature in Celsius

//   // Display the temperature on the Serial Monitor
//   Serial.print("Temperature: ");
//   Serial.print(temperatureC);
//   Serial.println(" °C");

//   delay(1000); // Delay for one second before taking another reading
// }
