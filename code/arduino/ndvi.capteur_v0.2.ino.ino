#include <Wire.h>
#include <Adafruit_BME280.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_AS726x.h>

#define TCA_ADDR 0x70  
#define CH_BME280  4  
#define CH_MPU6050 7  
#define CH_AS_SUN  0  
#define CH_AS_VINE 3  

Adafruit_BME280  bme;          
Adafruit_MPU6050 mpu;          
Adafruit_AS726x  as726x;

void tcaSelect(uint8_t ch) {
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << ch);
  Wire.endTransmission();
  delay(10);
}

void setup() {
  Serial.begin(115200);
  while (!Serial);
  Wire.begin();

  Serial.println("--- SYSTEME DE SURVEILLANCE VIGNE ---");
 
  tcaSelect(CH_BME280);  bme.begin(0x76);
  tcaSelect(CH_MPU6050); mpu.begin();
  tcaSelect(CH_AS_SUN);  as726x.begin();
  tcaSelect(CH_AS_VINE); as726x.begin();
 
  Serial.println("Initialisation terminee.");
  Serial.println("========================================");
}

void loop() {
  // --- 1. LECTURE DES CAPTEURS ---
 
  // MPU6050 (Accéléromètre)
  tcaSelect(CH_MPU6050);
  sensors_event_t a, g, temp_mpu;
  mpu.getEvent(&a, &g, &temp_mpu);

  // BME280 (Environnement)
  tcaSelect(CH_BME280);
  float T = bme.readTemperature();
  float H = bme.readHumidity();
  float P = bme.readPressure() / 100.0f;

  // AS726x (Spectre)
  uint16_t sun[6], vine[6];
  tcaSelect(CH_AS_SUN);
  as726x.startMeasurement();
  while (!as726x.dataReady());
  as726x.readRawValues(sun);

  tcaSelect(CH_AS_VINE);
  as726x.startMeasurement();
  while (!as726x.dataReady());
  as726x.readRawValues(vine);

  // --- 2. CALCULS ---
  // NDVI : (NIR - RED) / (NIR + RED)
  // On utilise ORANGE comme approximation NIR si capteur visible AS7262
  float red = (float)vine[AS726x_RED];
  float nir = (float)vine[AS726x_ORANGE];
  float ndvi = (nir - red) / (nir + red);

  // --- 3. AFFICHAGE STYLISÉ ---

  Serial.print("\n[ RELEVÉ : "); Serial.print(millis() / 1000); Serial.println(" s ]");
 
  // Section NDVI
  Serial.print("SANTÉ FEUILLE (NDVI) : ");
  Serial.print(ndvi, 3);
  if(ndvi > 0.5) Serial.println(" -> [ SAINE ]");
  else if(ndvi > 0.2) Serial.println(" -> [ STRESSÉE ]");
  else Serial.println(" -> [ ALERTE / SÈCHE ]");

  // Section Accéléromètre
  Serial.println("----------------------------------------");
  Serial.print("ACCÉLÉRATION (m/s²)");
  Serial.print("  X: "); Serial.print(a.acceleration.x, 2);
  Serial.print(" | Y: "); Serial.print(a.acceleration.y, 2);
  Serial.print(" | Z: "); Serial.println(a.acceleration.z, 2);

  // Section Environnement
  Serial.println("----------------------------------------");
  Serial.print("MÉTÉO  | ");
  Serial.print(T, 1); Serial.print("°C  | ");
  Serial.print(H, 1); Serial.print("% Hum  | ");
  Serial.print(P, 0); Serial.println(" hPa");

  // Section Spectrale brute
  Serial.print("SPECTRE| Soleil(R): "); Serial.print(sun[AS726x_RED]);
  Serial.print(" | Vigne(R): "); Serial.println(vine[AS726x_RED]);

  Serial.println("========================================");

  delay(10000); // Mise à jour toutes les 10 secondes
}