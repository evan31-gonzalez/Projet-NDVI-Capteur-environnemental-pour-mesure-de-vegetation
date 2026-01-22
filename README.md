# Projet NDVI : Capteur environnemental pour la vigne

Projet tutoré de développement instrumental, collaboratif entre **CESBIO** et l'**IUT Mesures Physiques**, visant la conception et la réalisation d’un capteur NDVI (Normalized Difference Vegetation Index) destiné au suivi de l’état de la vigne à partir de mesures spectrales.

Le capteur est conçu pour être utilisé en conditions réelles dans les vignes de Gaillac, dans un contexte de suivi agronomique et environnemental.

---

## Objectif du projet
L’objectif du projet est de développer un capteur NDVI à bas coût permettant d’évaluer la vigueur et le développement foliaire de la vigne à partir de mesures spectrales dans le rouge et le proche infrarouge.

Le dispositif vise à fournir des mesures in situ, complémentaires aux méthodes de télédétection satellitaire, et exploitables directement sur le terrain viticole.

---

## Principe de fonctionnement
Le NDVI est calculé à partir des réflectances mesurées dans deux bandes spectrales :
- Rouge : λ ≈ 680 nm  
- Proche infrarouge (PIR) : λ ≈ 810 nm  

La relation utilisée est :

NDVI = (ρPIR − ρRouge) / (ρPIR + ρRouge)

Les données sont acquises par des capteurs spectraux, traitées par un microcontrôleur, puis enregistrées afin de permettre le calcul et l’analyse de l’indice NDVI.

---

## Mesure de la réflectance
Le système utilise deux capteurs spectraux AS7265x afin de dissocier la lumière réfléchie par la vigne de la lumière incidente :

- un capteur orienté vers la vigne, destiné à mesurer la lumière réfléchie par la végétation,
- un capteur orienté vers le ciel, destiné à mesurer la lumière incidente.

Cette configuration permet de corriger les variations d’éclairement naturel (conditions météorologiques, heure de la journée, orientation du capteur) et de calculer une réflectance fiable. Le NDVI est ainsi déterminé à partir de mesures normalisées, comparables dans le temps et entre différentes parcelles.

---

## Matériel utilisé
Le système de mesure repose sur les composants suivants :

- Deux capteurs spectraux AS7265x pour la mesure de la réflectance (vigne / ciel)
- Microcontrôleur Arduino Nano  
- Capteur environnemental BME280 (température, humidité, pression atmosphérique)  
- Capteur inertiel MPU6050 (accéléromètre et gyroscope)  
- Multiplexeur I2C TCA9548A pour la gestion de plusieurs capteurs sur le bus I2C  
- Module horloge temps réel DS3231 pour l’horodatage des mesures  
- Module lecteur de carte SD pour l’enregistrement local des données  

Les mesures sont horodatées et stockées sur carte SD afin de permettre une exploitation ultérieure.

---

## Outils de conception et de développement
Le projet s’appuie sur les outils suivants :

- Eagle pour la conception des schémas électroniques et des cartes PCB  
- Fusion 360 pour la modélisation 3D du boîtier et des supports mécaniques  
- Arduino IDE pour le développement du code embarqué  

---

## Travaux réalisés
Le projet comprend :
- la conception électronique du capteur,
- la programmation embarquée,
- la modélisation 3D du boîtier,
- la conception de cartes PCB,
- la soudure et l’intégration de l’ensemble des capteurs sur support provisoire, réalisées avant la réception du PCB afin de valider le fonctionnement du système,
- l’intégration des différents capteurs,
- l’étalonnage et les tests du dispositif,
- l’exploitation et la visualisation des données acquises.

---

## Organisation du dépôt
- /code/arduino : code embarqué Arduino
- /code/python : scripts Python de visualisation et d’exploitation des données
- /pcb : schémas et fichiers de conception PCB
- /3D : modèles 3D du boîtier et des supports
- /docs : documentation, comptes rendus et supports de présentation

---

## Contexte expérimental
Ce projet est réalisé dans le cadre du BUT Mesures Physiques (Techniques d’Instrumentation).

Les campagnes de mesures terrain sont prévues sur des parcelles de vigne situées à Gaillac, avec des phases de tests, d’étalonnage et de validation prévues à partir de mars 2026.

---

## Équipe – Groupe 1
- Evan GONZALEZ
- Félix GRUÈS  
- Yannis FABRE  
- Sandro BARROT  
- Taha GHISSASSI  

---

## Encadrement
Projet encadré par :
- Mme Aurore Brut  
- M. Jean-Pascal Dezalay

---

## Licence
Ce projet est distribué sous licence MIT.


---

## Protocole
= Objectif
Ce protocole décrit la mise en œuvre et l’utilisation du capteur NDVI développé dans le cadre du projet tutoré.
Le dispositif permet de mesurer l’indice de végétation NDVI d’une parcelle viticole à partir de mesures de réflectance
dans le rouge et le proche infrarouge.

== Préparation du système
1. Vérifier que l’ensemble des capteurs est correctement câblé à la carte Arduino.
2. Insérer une carte SD formatée dans le lecteur prévu à cet effet.
3. Vérifier le bon branchement du module RTC DS3231 pour l’horodatage des mesures.
4. S’assurer que le boîtier est correctement fermé et que les capteurs spectraux sont dégagés.

== Téléversement du programme
1. Ouvrir le logiciel Arduino IDE sur l’ordinateur.
2. Sélectionner la carte *Arduino Nano 33 IoT* dans le menu *Outils > Type de carte*.
3. Sélectionner le port de communication correspondant à la carte.
4. Ouvrir le fichier du programme Arduino du capteur NDVI.
5. Téléverser le programme sur la carte Arduino.

== Mise en place sur le terrain
1. Positionner le capteur de manière stable au-dessus de la vigne.
2. Orienter le premier capteur spectral vers la végétation.
3. Orienter le second capteur spectral vers le ciel afin de mesurer la lumière incidente.
4. Vérifier que le capteur reste immobile pendant la phase de mesure.

== Exploitation des données
1. Retirer la carte SD après la fin des mesures.
2. Insérer la carte SD dans un ordinateur.
3. Récupérer les fichiers CSV enregistrés.
4. Utiliser les scripts Python fournis pour :
   - afficher les données sous forme de tableaux,
   - tracer l’évolution du NDVI en fonction du temps.

## Entretien et précautions
- Nettoyer régulièrement les capteurs spectraux pour éviter toute perturbation des mesures.
- Vérifier l’état de charge de la batterie avant chaque campagne de mesure.
- Éviter l’exposition prolongée à l’humidité ou à des températures extrêmes sans protection adaptée.
- Couper l’alimentation avant toute manipulation interne du système.


