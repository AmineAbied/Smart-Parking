#include <WiFi.h>
#include <HTTPClient.h>


// CHANGE THESE
const char* ssid = "Murphy";
const char* password = "HjeAZziBkBIpCgH";
const char* serverURL = "http://192.168.1.10:5000/parking";
String spot = "";

void setup() {
  pinMode(2, OUTPUT);
  Serial.begin(300);
  delay(1000);

  Serial.println("Connecting to WiFi...");
  //WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, password);
    delay(10000);
    Serial.print("WIFI status: ");
    Serial.println(WiFi.status());
  }

  Serial.println("\nWiFi connected");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;
    http.begin(serverURL);

    int httpCode = http.GET();

    if (httpCode == HTTP_CODE_OK) { 
      spot = http.getString();
      spot.trim();

      Serial.print("Received from server: ");
      Serial.println(spot);
    } else {
      Serial.print("HTTP error: ");
      Serial.println(httpCode);
    }

    http.end();
  } else {
    Serial.println("WiFi disconnected");
  }

  delay(5000);

  if (spot == "1") {
    digitalWrite(2, HIGH);
  } else {
    digitalWrite(2, LOW);
      
  }

  
}
