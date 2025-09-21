// Arduino dependencies 
#include <Arduino.h>
#include <Wire.h>

// Temperature dependencies
#include <OneWire.h>
#include <DallasTemperature.h>

// Time dependencies
#include <WiFi.h>
#include "time.h"

const char* ntpServer = "pool.ntp.org";     // NTP server to get gmt time
const long gmtOffset_sec = 28800;           // + 8 hours
const int daylightOffset_sec = 0;           // No daylight saving time

// Sensor libraries
#include "digital_temperature_sensor/digital_temperature_sensor.cpp"
#include "shock_sensor/shock_sensor.cpp"
#include "sound_sensor/sound_sensor.cpp"
bool readShock(int);
int readTemp(int);
int readSound(int);

// Json Library for logging + json setup
#include <ArduinoJson.h>
#include <fstream>
#include <SPIFFS.h>

// Pin definitions
#define temperature_sensor_pin 9
#define shock_sensor_pin 17
#define sound_sensor_pin 20

OneWire oneWire(temperature_sensor_pin);
DallasTemperature sensors(&oneWire);

// Time setup
const char* ssid = "pixel_9a";
const char* password = "qazwsxedc";

void setup() {
    // Initialise serial communication
    Serial.begin(115200);

    // Pin initialization
    sensors.begin();
    pinMode (shock_sensor_pin, INPUT);

    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println("An error occurred while mounting SPIFFS");
        return;
    }
    Serial.println("SPIFFS mounted successfully");

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
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    printLocalTime();
}

String printLocalTime(){
    struct tm timeinfo;
    if(!getLocalTime(&timeinfo)){
        String msg = "Failed to obtain time";
        return msg;
    }
    
    else{
        char timeDate[64];
        strftime(timeDate, sizeof(timeDate), "%Y-%m-%d %H:%M:%S", &timeinfo);
        return String(timeDate);
    }
}

void loop() {
    // Read heartbeat sensor
    bool shock = readShock(shock_sensor_pin);

    // Read temperature sensor
    float temperature = readTemp(temperature_sensor_pin);

    // Read sound sensor
    int sound = readSound(sound_sensor_pin);

    // Create JSON object for logging
    JsonDocument doc;
    doc["shock"] = shock;
    doc["temperature"] = temperature;
    doc["sound"] = sound;
    
    String timeDate = { printLocalTime() };

    Serial.print("'date':");
    Serial.print(timeDate);
    Serial.print(",");
    Serial.print("'temperature':");
    Serial.print(temperature);
    Serial.print(",");
    Serial.print("'shock':");
    Serial.print(shock);
    Serial.print(",");
    Serial.print("'sound':");
    Serial.print(sound);
    Serial.println("");

    doc["timestamp"] = timeDate;

    // Append to SPIFFS file
    File file = SPIFFS.open("/log.json", FILE_APPEND);
    if (file) {
        serializeJson(doc, file);
        file.println(); // Add newline for each entry
        file.close();
    } else {
        Serial.println("Failed to open file for writing");
    }

    // std::ofstream o("log.json");
    delay(5000);
}

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