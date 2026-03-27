#include <Arduino.h>
#include <Arduino_BMI270_BMM150.h>

static unsigned long lastPrintMs = 0;
const unsigned long printPeriodMs = 100; // 10 Hz affichage

void setup() {
    Serial.begin(115200);
    delay(1500);

    Serial.println("Boot OK - IMU bring-up");

    if (!IMU.begin()) {
        Serial.println("Erreur: initialisation IMU impossible");
        while (1) {
            delay(1000);
        }
    }

    Serial.println("IMU initialisee");
    Serial.print("Frequence accel disponible: ");
    Serial.print(IMU.accelerationSampleRate());
    Serial.println(" Hz");

    Serial.print("Frequence gyro disponible: ");
    Serial.print(IMU.gyroscopeSampleRate());
    Serial.println(" Hz");
}

void loop() {
    float ax, ay, az;
    float gx, gy, gz;

    if (millis() - lastPrintMs >= printPeriodMs) {
        lastPrintMs = millis();

        bool accelReady = IMU.accelerationAvailable();
        bool gyroReady  = IMU.gyroscopeAvailable();

        if (accelReady) {
            IMU.readAcceleration(ax, ay, az);
        }

        if (gyroReady) {
            IMU.readGyroscope(gx, gy, gz);
        }

        if (accelReady || gyroReady) {
            Serial.print("ACC[g]: ");
            Serial.print(ax, 4); Serial.print(", ");
            Serial.print(ay, 4); Serial.print(", ");
            Serial.print(az, 4);

            Serial.print(" | GYR[dps]: ");
            Serial.print(gx, 4); Serial.print(", ");
            Serial.print(gy, 4); Serial.print(", ");
            Serial.println(gz, 4);
        }
    }
}