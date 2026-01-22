# Code du capteur NDVI

Ce dossier regroupe l’ensemble du code du projet NDVI.
Il inclut le code embarqué exécuté sur microcontrôleur ainsi que les scripts de
traitement et de visualisation des données.

---

## Organisation du dossier

- **arduino/**  
  Code embarqué du capteur NDVI : acquisition des capteurs, calculs,
  horodatage et enregistrement des données sur carte SD.

- **python/**  
  Scripts Python pour l’exploitation des données : affichage des
 données et tracé de l’évolution du NDVI et des paramètres environnementaux en fonction du temps.

---

## Code Arduino

Le code Arduino permet :
- la communication avec les capteurs spectraux AS7265x (vigne et ciel) via le bus I2C,
- la gestion du multiplexeur TCA9548A,
- la lecture des capteurs environnementaux (BME280, MPU6050),
- l’horodatage des mesures à l’aide du module RTC DS3231,
- l’enregistrement des données sur carte SD.

Le code est développé et testé sur une carte **Arduino Nano 33 IoT**.

### Bibliothèques utilisées :
- `Wire` : Permet la communication I2C entre l'Arduino et les capteurs.
- `Adafruit_BME280` : Fournit des fonctions pour interagir avec le capteur BME280 (température, humidité, pression).
- `Adafruit_MPU6050` : Fournit des fonctions pour interagir avec le capteur MPU6050 (accéléromètre et gyroscope).
- `Adafruit_Sensor` : Interface commune pour les capteurs Adafruit, permettant de gérer les événements de capteurs.

---

## Code Python

Les scripts Python permettent :
- la lecture des fichiers CSV générés par le capteur,
- l’affichage des données sous forme de tableaux,
- le tracé de l’indice NDVI en fonction du temps.

### Bibliothèques utilisées :
- `tkinter` (`tk`) pour la création de l'interface graphique,
- `serial` pour la gestion des communications série avec le capteur,
- `matplotlib.pyplot` (`plt`) pour la création de graphiques,
- `FigureCanvasTkAgg` pour l'intégration des graphiques dans l'interface Tkinter,
- `numpy` (`np`) pour les calculs numériques,
- `time` pour la gestion du temps,
- `random` pour la génération de données aléatoires .
- `re` permet de lire l'Arduino
