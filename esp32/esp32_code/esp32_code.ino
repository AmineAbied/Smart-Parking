#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h>

// ==== LCD Setup ====
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ==== WiFi & Server ====
const char* ssid      = "EL FARABI SMART PARKING";
const char* password  = "wlan798027";
const char* serverURL = "http://192.168.1.4:5000/parking";

// ==== Pins ====
#define IR_ENTREE  19   // Capteur IR entrée
#define IR_SORTIE  2   // Capteur IR sortie
#define SERVO_ENTREE_PIN 4
#define SERVO_SORTIE_PIN 23

// ==== Servos ====
Servo servoEntree;
Servo servoSortie;

String spot = "";

// ==== Ouvre/Ferme barrière ====
void ouvrirBarriere(Servo &servo, String label) {
  servo.write(90);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(label);
  lcd.setCursor(0, 1);
  lcd.print("Barriere ouverte");
  delay(3000);         // reste ouvert 3 secondes
  servo.write(0);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(label);
  lcd.setCursor(0, 1);
  lcd.print("Barriere fermee");
}

void setup() {
  pinMode(2, OUTPUT);
  pinMode(IR_ENTREE, INPUT);
  pinMode(IR_SORTIE, INPUT);

  Serial.begin(300);
  delay(1000);

  // ==== LCD Init ====
  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Connexion WiFi..");

  // ==== Servos Init ====
  servoEntree.attach(SERVO_ENTREE_PIN);
  servoSortie.attach(SERVO_SORTIE_PIN);
  servoEntree.write(0);  // position fermée
  servoSortie.write(0);

  // ==== WiFi ====
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, password);
    delay(10000);
    Serial.print("WIFI status: ");
    Serial.println(WiFi.status());
  }

  Serial.println("\nWiFi connected");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WiFi connecte!");
  lcd.setCursor(0, 1);
  lcd.print(WiFi.localIP());
  delay(2000);
}

void loop() {

  // ==== Lecture capteurs IR ====
  bool detectionEntree = digitalRead(IR_ENTREE) == LOW;  // LOW = objet détecté
  bool detectionSortie = digitalRead(IR_SORTIE) == LOW;

  if (detectionEntree) {
    Serial.println("Voiture detectee a l'entree");
    if (spot != "No SPOTS") {
      ouvrirBarriere(servoEntree, "Entree");
    } else {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Entree bloquee");
      lcd.setCursor(0, 1);
      lcd.print("Parking plein!");
      Serial.println("Parking plein, entree refusee");
    }
  }

  if (detectionSortie) {
    Serial.println("Voiture detectee a la sortie");
    ouvrirBarriere(servoSortie, "Sortie");
  }

  // ==== Requête serveur ====
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    int httpCode = http.GET();

    if (httpCode == HTTP_CODE_OK) {
      spot = http.getString();
      spot.trim();
      Serial.print("Received from server: ");
      Serial.println(spot);

      // ==== Affichage LCD ====
      lcd.clear();
      if (spot == "No SPOTS") {
        lcd.setCursor(0, 0);
        lcd.print("Places libres:");
        lcd.setCursor(0, 1);
        lcd.print("Aucune place");
      } else {
        lcd.setCursor(0, 0);
        lcd.print("Place libre:");
        lcd.setCursor(0, 1);
        lcd.print("Spot " + spot);
      }

    } else {
      Serial.print("HTTP error: ");
      Serial.println(httpCode);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Erreur serveur");
      lcd.setCursor(0, 1);
      lcd.print("Code: " + String(httpCode));
    }

    http.end();

  } else {
    Serial.println("WiFi disconnected");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi deconnecte");
  }

  delay(500);

  if (spot == "1") {
    digitalWrite(2, HIGH);
  } else {
    digitalWrite(2, LOW);
  }
}
