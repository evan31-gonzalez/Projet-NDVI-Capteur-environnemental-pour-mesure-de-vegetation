# Code Arduino – Capteur NDVI

Ce dossier contient le code embarqué exécuté sur le microcontrôleur Arduino Nano.

Le programme assure :
- l’acquisition des données issues des capteurs spectraux AS7265x,
- la gestion des capteurs environnementaux et inertiels,
- l’horodatage des mesures,
- l’enregistrement des données sur carte SD.

---

## Organisation du code

Chaque version du programme est enregistrée sous forme d’un fichier distinct afin de conserver l’historique du développement.

Les fichiers sont nommés selon la convention :
ndvi_capteur_vX.Y.ino

où X.Y correspond à la version du code.

---

## Version actuelle

- v0.1 : première version fonctionnelle du code Arduino, permettant l’acquisition des données et leur enregistrement.
- V0.4 : dernière version fonctionnelle du code Arduino, permettant l'acquisition et le stockage des données sur un fichier CSV, incluant la carte SD formatée et les autres capteurs fonctionnels. 
