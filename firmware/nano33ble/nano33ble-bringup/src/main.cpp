#include <Arduino.h>
#include <Arduino_BMI270_BMM150.h>

static unsigned long lastReadMs = 0;
const unsigned long readPeriodMs = 20; // 50 Hz 

void setup() {
    Serial.begin(230400);
    delay(1500);

    Serial.println("time_ms,ax,ay,az,gx,gy,gz");
}

void loop() {
    float ax, ay, az;
    float gx, gy, gz;

    if (millis() - lastReadMs >= readPeriodMs) {
        lastReadMs += readPeriodMs;

        bool accelReady = IMU.accelerationAvailable();
        bool gyroReady  = IMU.gyroscopeAvailable();

        if (accelReady) {
            IMU.readAcceleration(ax, ay, az);
        }

        if (gyroReady) {
            IMU.readGyroscope(gx, gy, gz);
        }

        if (accelReady || gyroReady) {
            Serial.print(lastReadMs); Serial.print(",");
            Serial.print(ax, 4); Serial.print(",");
            Serial.print(ay, 4); Serial.print(",");
            Serial.print(az, 4); Serial.print(",");
            Serial.print(gx, 4); Serial.print(",");
            Serial.print(gy, 4); Serial.print(",");
            Serial.println(gz, 4);
        }
    }
}