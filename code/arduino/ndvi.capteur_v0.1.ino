#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <RTClib.h>
#include <Adafruit_BME280.h>
#include <SparkFun_AS7265X.h>
#include <EEPROM.h>

/************ Réglages ************/
#define SD_CS_PIN 10
#define BME280_ADDR 0x76
#define LED_PIN 8
#define SAMPLE_DELAY 60000UL // 1 minute

RTC_DS3231 rtc;
Adafruit_BME280 bme;
AS7265X as7265x;
File logFile;

/************ Config ************/
void setup() {
  Serial.begin(115200);
  Wire.begin();

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Initialisation RTC
  if (!rtc.begin()) {
    Serial.println(F("RTC non détectée !"));
  } else if (rtc.lostPower()) {
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  // Initialisation SD
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println(F("Erreur carte SD !"));
  } else {
    Serial.println(F("SD OK"));
  }

  // Initialisation BME280
  if (!bme.begin(BME280_ADDR)) {
    Serial.println(F("BME280 non détecté !"));
  } else {
    Serial.println(F("BME280 OK"));
  }

  // Initialisation AS7265x
  if (!as7265x.begin()) {
    Serial.println(F("AS7265x non détecté !"));
  } else {
    Serial.println(F("AS7265x OK"));
    as7265x.setGain(AS7265X_GAIN_16X);
    as7265x.setIntegrationCycles(50); // correct pour ta version
    as7265x.disableIndicator();
  }

  Serial.println(F("Démarrage NDVI Logger prêt."));
}

/************ Boucle ************/
void loop() {
  digitalWrite(LED_PIN, HIGH);

  DateTime now = rtc.now();
  char dateStr[11], timeStr[9];
  snprintf(dateStr, sizeof(dateStr), "%04u-%02u-%02u", now.year(), now.month(), now.day());
  snprintf(timeStr, sizeof(timeStr), "%02u:%02u:%02u", now.hour(), now.minute(), now.second());

  // Lecture BME280
  bme.takeForcedMeasurement();
  float t = bme.readTemperature();
  float rh = bme.readHumidity();
  float p = bme.readPressure() / 100.0f;

  // Lecture AS7265x
  as7265x.takeMeasurements();
  // selon la lib SparkFun : canaux A-F, G-L, R-W
  float red = as7265x.getCalibratedR(); // 680 nm
  float nir = as7265x.getCalibratedK(); // ~800–810 nm

  // Calcul NDVI
  float ndvi = (nir - red) / (nir + red);

  // Fichier CSV du jour
  char filename[20];
  snprintf(filename, sizeof(filename), "%04u%02u%02u.csv", now.year(), now.month(), now.day());
  File logFile = SD.open(filename, FILE_WRITE);

  if (logFile) {
    if (logFile.size() == 0) {
      logFile.println(F("date,time,red_680,nir_810,ndvi,temp,hum,press"));
    }
    logFile.print(dateStr); logFile.print(',');
    logFile.print(timeStr); logFile.print(',');
    logFile.print(red, 4); logFile.print(',');
    logFile.print(nir, 4); logFile.print(',');
    logFile.print(ndvi, 4); logFile.print(',');
    logFile.print(t, 2); logFile.print(',');
    logFile.print(rh, 2); logFile.print(',');
    logFile.println(p, 2);
    logFile.close();
  } else {
    Serial.println(F("Erreur ouverture fichier SD !"));
  }

  // Affichage série
  Serial.print(dateStr); Serial.print(" ");
  Serial.print(timeStr);
  Serial.print(F(" | NDVI=")); Serial.println(ndvi, 3);

  digitalWrite(LED_PIN, LOW);
  delay(SAMPLE_DELAY);
}
