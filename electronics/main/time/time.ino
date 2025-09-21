#include <WiFi.h>
#include "time.h"

const char* ssid     = "pixel_9a";
const char* password = "qazwsxedc";

const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 28800;
const int   daylightOffset_sec = 0;

void setup(){
  Serial.begin(115200);

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
  
  // Init and get the time
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  printLocalTime();

  //disconnect WiFi as it's no longer needed
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
}

void loop(){
  delay(1000);
  printLocalTime();
}

void printLocalTime(){
  struct tm timeinfo;
  if(!getLocalTime(&timeinfo)){
    Serial.println("Failed to obtain time");
    return;
  }
  // Serial.print(&timeinfo, "%H:");
  // Serial.print(&timeinfo, "%M:");
  // Serial.print(&timeinfo, "%S");

  char timeDate[21];
  strftime(timeDate, sizeof(timeDate), "%y-%m-%d %H:%M:%S", &timeinfo);
  Serial.print(timeDate);
  Serial.println();
}