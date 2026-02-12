#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <Adafruit_BME280.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_AS726x.h>
#include <math.h> 

// --- REGLAGES ---
#define NB_MESURES 10 // Rafale de 10 mesures pour l'incertitude

// --- ADRESSES ---
#define TCA_ADDR 0x70   
#define CH_BME280  4   
#define CH_MPU6050 7   
#define CH_AS_VINE 3   

const int chipSelect = 10; 

Adafruit_BME280  bme;           
Adafruit_MPU6050 mpu;           
Adafruit_AS726x  as726x; 

void tcaSelect(uint8_t ch) {
  if (ch > 7) return;
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << ch);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  while (!Serial); 
  Wire.begin();
  Wire.setClock(100000); 

  Serial.println("--- SYSTEME VIGNE (METROLOGIE & UNITES) ---");

  // --- 1. CARTE SD ---
  Serial.print("Init SD... ");
  if (!SD.begin(chipSelect)) {
    Serial.println("ERREUR !");
    while(1);
  } 
  Serial.println("OK.");

  // --- 2. FICHIERS (Avec Unités) ---
  
  // MESURES.CSV (Moyennes)
  File f1 = SD.open("MESURES.CSV", FILE_WRITE);
  if (f1) {
    if (f1.size() == 0) {
      // AJOUT DES UNITÉS ICI
      f1.println("Temps(s);Temp(C);Hum(%);Pres(hPa);NDVI;AccelX(m/s2);AccelY(m/s2);AccelZ(m/s2)");
    }
    f1.close();
  }

  // METROLO.CSV (Incertitudes)
  File f2 = SD.open("METROLO.CSV", FILE_WRITE);
  if (f2) {
    if (f2.size() == 0) {
      f2.print("Temps(s);");
      f2.print("u_Temp(C);u_Hum(%);u_Pres(hPa);"); 
      f2.print("u_Rouge;u_NIR;u_NDVI;"); 
      f2.println("u_Ax(m/s2);u_Ay(m/s2);u_Az(m/s2)");      
    }
    f2.close();
  }
  
  // --- 3. CAPTEURS ---
  Serial.println("Init Capteurs...");

  tcaSelect(CH_BME280);   
  if (!bme.begin(0x76)) Serial.println("Err BME");
  
  tcaSelect(CH_MPU6050);  
  if (!mpu.begin()) Serial.println("Err MPU");

  tcaSelect(CH_AS_VINE);  
  if (!as726x.begin()) {
    Serial.println("Err Vigne");
  } else {
    // REGLAGE SENSIBILITE (Pour éviter NDVI=1)
    as726x.setGain(2); // Gain 16x (Moyen)
    as726x.setIntegrationTime(50); // 50ms x 16 = bonne sensibilité
    as726x.indicateLED(false); // Pas de lumière parasite
    as726x.drvOff();
  }
  
  Serial.println("--- PRET ---");
}

void loop() {
  unsigned long currentMillis = millis();
  float timeSec = currentMillis / 1000.0;
  
  // Variables statistiques
  double s_T=0, sq_T=0; 
  double s_H=0, sq_H=0; 
  double s_P=0, sq_P=0;
  double s_R=0, sq_R=0; 
  double s_N=0, sq_N=0; 
  double s_NDVI=0, sq_NDVI=0;
  double s_ax=0, sq_ax=0; 
  double s_ay=0, sq_ay=0; 
  double s_az=0, sq_az=0;

  // --- RAFALE DE 10 MESURES ---
  for(int i=0; i<NB_MESURES; i++) {
    
    // MPU
    tcaSelect(CH_MPU6050);
    sensors_event_t a, g, temp_mpu;
    mpu.getEvent(&a, &g, &temp_mpu);
    float ax = a.acceleration.x;
    float ay = a.acceleration.y;
    float az = a.acceleration.z;

    // BME
    tcaSelect(CH_BME280);
    float t = bme.readTemperature();
    float h = bme.readHumidity();
    float p = bme.readPressure() / 100.0f;

    // VIGNE
    tcaSelect(CH_AS_VINE);
    as726x.startMeasurement();
    while(!as726x.dataReady());
    // On lit en calibré (float) pour la précision
    float red = as726x.readCalibratedValue(AS726x_RED);
    float nir = as726x.readCalibratedValue(AS726x_ORANGE);
    
    float ndvi = 0.0;
    // Protection division par zéro renforcée
    if((nir + red) > 0.1) ndvi = (nir - red) / (nir + red);

    // Accumulation
    s_T+=t; sq_T+=t*t;
    s_H+=h; sq_H+=h*h;
    s_P+=p; sq_P+=p*p;

    s_R+=red; sq_R+=red*red;
    s_N+=nir; sq_N+=nir*nir;
    s_NDVI+=ndvi; sq_NDVI+=ndvi*ndvi;

    s_ax+=ax; sq_ax+=ax*ax;
    s_ay+=ay; sq_ay+=ay*ay;
    s_az+=az; sq_az+=az*az;
  }

  // --- CALCULS (Moyenne & Incertitude) ---
  double N = (double)NB_MESURES;
  
  auto calc_uncert = [N](double sum, double sumSq) {
    double var = (sumSq - (sum * sum) / N) / (N - 1);
    if (var < 0) var = 0;
    return sqrt(var);
  };

  // Moyennes
  float m_T = s_T/N; float m_H = s_H/N; float m_P = s_P/N;
  float m_NDVI = s_NDVI/N;
  float m_R = s_R/N; float m_N = s_N/N; // Pour affichage debug
  float m_ax = s_ax/N; float m_ay = s_ay/N; float m_az = s_az/N;

  // Incertitudes
  float u_T = calc_uncert(s_T, sq_T);
  float u_H = calc_uncert(s_H, sq_H);
  float u_P = calc_uncert(s_P, sq_P);
  float u_R = calc_uncert(s_R, sq_R);
  float u_N = calc_uncert(s_N, sq_N);
  float u_NDVI = calc_uncert(s_NDVI, sq_NDVI);
  float u_ax = calc_uncert(s_ax, sq_ax);
  float u_ay = calc_uncert(s_ay, sq_ay);
  float u_az = calc_uncert(s_az, sq_az);

  // --- ECRITURE SD ---

  // 1. MESURES.CSV
  File f1 = SD.open("MESURES.CSV", FILE_WRITE);
  if (f1) {
    f1.print(timeSec); f1.print(";");
    f1.print(m_T); f1.print(";");
    f1.print(m_H); f1.print(";");
    f1.print(m_P); f1.print(";");
    f1.print(m_NDVI); f1.print(";");
    f1.print(m_ax); f1.print(";");
    f1.print(m_ay); f1.print(";");
    f1.println(m_az);
    f1.close();
  }

  // 2. METROLO.CSV
  File f2 = SD.open("METROLO.CSV", FILE_WRITE);
  if (f2) {
    f2.print(timeSec); f2.print(";");
    f2.print(u_T, 4); f2.print(";"); f2.print(u_H, 4); f2.print(";"); f2.print(u_P, 4); f2.print(";");
    f2.print(u_R, 4); f2.print(";"); f2.print(u_N, 4); f2.print(";"); f2.print(u_NDVI, 4); f2.print(";");
    f2.print(u_ax, 4); f2.print(";"); f2.print(u_ay, 4); f2.print(";"); f2.println(u_az, 4);
    f2.close();
  }

  // --- AFFICHAGE (Pour comprendre le NDVI=1) ---
  Serial.print("\n[ T: "); Serial.print(timeSec); Serial.println("s ]");
  
  // DEBUG : Affiche les valeurs brutes pour comprendre le "NDVI=1"
  Serial.print("LUMIERE : Rouge="); Serial.print(m_R); 
  Serial.print(" | NIR="); Serial.println(m_N);
  if (m_R < 1.0) Serial.println(">>> ATTENTION : Rouge trop faible (=0) -> NDVI force a 1");

  Serial.print("NDVI    : "); Serial.print(m_NDVI, 3);
  Serial.print(" (+/- "); Serial.print(u_NDVI, 4); Serial.println(")");

  Serial.print("METEO   : "); Serial.print(m_T, 1); Serial.print(" C | ");
  Serial.print(m_H, 1); Serial.print(" % | ");
  Serial.print(m_P, 0); Serial.println(" hPa");

  Serial.println("Sauvegarde OK.");
  delay(10000); 
}
