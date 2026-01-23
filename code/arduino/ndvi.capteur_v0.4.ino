#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <Adafruit_BME280.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_AS726x.h>

// --- ADRESSES I2C ---
#define TCA_ADDR 0x70  
#define CH_BME280  4  
#define CH_MPU6050 7  
#define CH_AS_SUN  0  
#define CH_AS_VINE 3  

// Pin de sélection de la carte SD (généralement 10 sur Nano 33 IoT / Uno)
const int chipSelect = 10; 

Adafruit_BME280  bme;          
Adafruit_MPU6050 mpu;          
Adafruit_AS726x  as726x;

// Fonction pour changer le canal du Multiplexeur
void tcaSelect(uint8_t ch) {
  if (ch > 7) return;
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << ch);
  Wire.endTransmission();
  delay(10);
}

void setup() {
  Serial.begin(115200);
  while (!Serial); // Attend que le PC soit connecté (utile pour le débogage)
  Wire.begin();

  Serial.println("--- SYSTEME DE SURVEILLANCE VIGNE ---");

  // --- 1. INITIALISATION CARTE SD ---
  Serial.print("Init Carte SD... ");
  if (!SD.begin(chipSelect)) {
    Serial.println("ERREUR ! (Verifiez que la carte est bien inseree)");
  } else {
    Serial.println("OK.");
    
    // Création du fichier CSV avec l'en-tête (une seule fois)
    File dataFile = SD.open("donnees.csv", FILE_WRITE);
    if (dataFile) {
      // Si le fichier est vide (taille 0), on met les titres
      if (dataFile.size() == 0) {
        dataFile.println("Temps(s);Temperature;Humidite;Pression;NDVI;AccelX;AccelY;AccelZ");
      }
      dataFile.close();
    }
  }
  
  // --- 2. INITIALISATION CAPTEURS ---
  tcaSelect(CH_BME280);  
  if(!bme.begin(0x76)) Serial.println("Erreur BME280");
  
  tcaSelect(CH_MPU6050); 
  if(!mpu.begin()) Serial.println("Erreur MPU6050");
  
  tcaSelect(CH_AS_SUN);  
  if(as726x.begin()) {
     // as726x.setGain(2); // Optionnel : Gain 16X
  } else {
     Serial.println("Erreur AS726x SUN");
  }

  tcaSelect(CH_AS_VINE); 
  if(as726x.begin()) {
     // as726x.setGain(2); // Optionnel
  } else {
     Serial.println("Erreur AS726x VINE");
  }
  
  Serial.println("Initialisation terminee.");
  Serial.println("========================================");
}

void loop() {
  // --- 1. LECTURE DES CAPTEURS ---
  
  // Accéléromètre
  tcaSelect(CH_MPU6050);
  sensors_event_t a, g, temp_mpu;
  mpu.getEvent(&a, &g, &temp_mpu);

  // Météo
  tcaSelect(CH_BME280);
  float T = bme.readTemperature();
  float H = bme.readHumidity();
  float P = bme.readPressure() / 100.0f;

  // Spectre (Soleil & Vigne)
  uint16_t sun[6], vine[6];
  
  tcaSelect(CH_AS_SUN);
  as726x.startMeasurement();
  while (!as726x.dataReady());
  as726x.readRawValues(sun);

  tcaSelect(CH_AS_VINE);
  as726x.startMeasurement();
  while (!as726x.dataReady());
  as726x.readRawValues(vine);

  // --- 2. CALCUL NDVI ---
  // On utilise les canaux spécifiques pour le calcul
  float red = (float)vine[AS726x_RED];
  float nir = (float)vine[AS726x_ORANGE];
  
  float ndvi = 0.0;
  if ((nir + red) != 0) {
      ndvi = (nir - red) / (nir + red);
  }

  // --- 3. SAUVEGARDE SUR CARTE SD ---
  // On ouvre, on écrit, on ferme (sécurité maximale)
  File dataFile = SD.open("donnees.csv", FILE_WRITE);
  if (dataFile) {
    dataFile.print(millis() / 1000); dataFile.print(";");
    dataFile.print(T); dataFile.print(";");
    dataFile.print(H); dataFile.print(";");
    dataFile.print(P); dataFile.print(";");
    dataFile.print(ndvi); dataFile.print(";");
    dataFile.print(a.acceleration.x); dataFile.print(";");
    dataFile.print(a.acceleration.y); dataFile.print(";");
    dataFile.println(a.acceleration.z);
    dataFile.close();
  } else {
    // Si la carte est retirée, on l'affiche juste dans le moniteur série
    Serial.println("Erreur d'ecriture SD (Carte absente ?)");
  }

  // --- 4. AFFICHAGE SERIE (Ton format) ---
  Serial.print("\n[ RELEVÉ : "); Serial.print(millis() / 1000); Serial.println(" s ]");
  
  Serial.print("SANTÉ FEUILLE (NDVI) : ");
  Serial.print(ndvi, 3);
  if(ndvi > 0.5) Serial.println(" -> [ SAINE ]");
  else if(ndvi > 0.2) Serial.println(" -> [ STRESSÉE ]");
  else Serial.println(" -> [ ALERTE / SÈCHE ]");

  Serial.println("----------------------------------------");
  Serial.print("ACCÉLÉRATION (m/s²)");
  Serial.print("  X: "); Serial.print(a.acceleration.x, 2);
  Serial.print(" | Y: "); Serial.print(a.acceleration.y, 2);
  Serial.print(" | Z: "); Serial.println(a.acceleration.z, 2);

  Serial.println("----------------------------------------");
  Serial.print("MÉTÉO  | ");
  Serial.print(T, 1); Serial.print("°C  | ");
  Serial.print(H, 1); Serial.print("% Hum  | ");
  Serial.print(P, 0); Serial.println(" hPa");

  Serial.print("SPECTRE| Soleil(R): "); Serial.print(sun[AS726x_RED]);
  Serial.print(" | Vigne(R): "); Serial.println(vine[AS726x_RED]);

  Serial.println("========================================");

  delay(10000); // Pause de 10 secondes
}