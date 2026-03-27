# Bring-up IMU

## Capteur retenu
IMU embarquee Nano 33 BLE Rev2
- Accelerometre 3 axes
- Gyroscope 3 axes
- Magnetometre non utilise pour la V1

## Bibliotheque
Arduino_BMI270_BMM150

## Test realise
- Initialisation IMU OK
- Lecture accelerometre OK
- Lecture gyroscope OK
- Valeurs coherentes a l'arret et en mouvement

## Observation
- A l'arret, un axe accel est proche de 1 g
- Gyroscope proche de 0 dps a l'arret
- Variations visibles lors des mouvements manuels

## Conclusion
Lecture brute capteur validee pour la suite du projet.
