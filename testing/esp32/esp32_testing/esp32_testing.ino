#include <WiFi.h>
#include <HTTPClient.h>

// 🔧 CHANGE THESE
const char* ssid = "Murphy";
const char* password = "HjeAZziBkBIpCgH";
const char* serverURL = "http://192.168.1.12:5000/parking"; // CHANGE IP
String spot = "";

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    pinMode(2, OUTPUT);
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

    if (httpCode == HTTP_CODE_OK) {  // 200
      spot = http.getString();
      spot.trim(); // remove \n or spaces

      Serial.print("Received from server: ");
      Serial.println(spot);  // should print "a1"
    } else {
      Serial.print("HTTP error: ");
      Serial.println(httpCode);
    }

    http.end();
  } else {
    Serial.println("WiFi disconnected");
  }

  delay(5000);  // request every 5 seconds

  if (spot == "a1") {
    digitalWrite(2, HIGH);
  } else {
    digitalWrite(2, LOW);
      
  }
}
