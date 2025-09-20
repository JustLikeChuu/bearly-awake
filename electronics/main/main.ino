// Arduino dependencies 
#include <Arduino.h>
#include <Wire.h>

// Time dependencies
#include <WiFi.h>
#include "time.h"

// Sensor libraries
#include "digital_temperature_sensor/digital_temperature_sensor.ino"
#include "shock_sensor/shock_sensor.ino"
#include "sound_sensor/sound_sensor.ino"

// Json Library for logging + json setup
#include <ArduinoJson.h>
#include <fstream>
#include <SPIFFS.h>

// if (!SPIFFS.begin(true)) {
//     Serial.println("An Error has occurred while mounting SPIFFS");
//     return;
//   }
// Serial

// // Open JSON file
// File logs = SPIFFS.open("/log.json", "r");
// if (!logs) {
//     Serial.println("Failed to open file for reading");
//     return;
// }
// Serial.println("Successfully opened log file");

// DeserializationError error = deserializeJson(doc, logs);
// if (error) {
//     Serial.println("Failed to read file, using default configuration");
// };
// logs.close();


// Pin definitions
#define temperature_sensor_pin 16
#define shock_sensor_pin 4
#define sound_sensor_pin 20

// Time setup
const char* ssid = "pixel_9a";
const char* password = "qazwsxedc";

const char* ntpServer = "pool.ntp.org";     // NTP server to get gmt time
const long gmtOffset_sec = 28800;           // + 8 hours

void setup() {
    // Initialise serial communication
    Serial.begin(9600);

    // Connect to Wi-Fi
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected.");

    // Init time
    configTime(gmtOffset_sec, 0, ntpServer);
    printLocalTime();
}

void printLocalTime(){
    struct tm timeinfo;
    if(!getLocalTime(&timeinfo)){
        Serial.println("Failed to obtain time");
        return;
  }
}

void loop() {
    // Read heartbeat sensor
    bool shock = readShock(shock_sensor_pin);

    // Read temperature sensor
    float temperature = readTemp(temperature_sensor_pin);

    // Read sound sensor
    int sound = readSound();

    // Create JSON object for logging
    JsonDocument doc;
    JsonDocument data;
    data["shock"] = shock;
    data["temperature"] = temperature;
    data["sound"] = sound;
    doc[getLocalTime(&timeinfo)] = data;

    std::ofstream o("log.json");
    delay(5000);
}