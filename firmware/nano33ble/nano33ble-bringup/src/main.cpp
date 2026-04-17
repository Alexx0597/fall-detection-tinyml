#include <Arduino.h>
#include <Arduino_BMI270_BMM150.h>
#include <Chute_inferencing.h>

#define CONVERT_G_TO_MS2    9.80665f
#define MAX_ACCEPTED_RANGE  2.0f 

static bool debug_nn = false;
static unsigned long lastReadMs = 0;
const unsigned long readPeriodMs = 20; // 50 Hz 

void setup() {
    Serial.begin(230400);
    delay(1500);
    if (!IMU.begin()) {
        Serial.println("Erreur IMU !");
    }
    else {
        Serial.println("IMU INITIALIZED");
    }
}

float ei_get_sign(float number){
    return (number >= 0.0) ? 1.0 : -1.0;
}

void loop() {
    float ax, ay, az;
    float gx, gy, gz;

    float buffer[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE] = { 0 };

    Serial.println("Starting data acq");

    for (size_t ix = 0; ix < EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE; ix += 3) {
        // Determine the next tick (and then sleep later)
        uint64_t next_tick = micros() + (EI_CLASSIFIER_INTERVAL_MS * 1000);

        IMU.readAcceleration(buffer[ix], buffer[ix + 1], buffer[ix + 2]);

        for (int i = 0; i < 3; i++) {
            if (fabs(buffer[ix + i]) > MAX_ACCEPTED_RANGE) {
                buffer[ix + i] = ei_get_sign(buffer[ix + i]) * MAX_ACCEPTED_RANGE;
            }
        }

        buffer[ix + 0] *= CONVERT_G_TO_MS2;
        buffer[ix + 1] *= CONVERT_G_TO_MS2;
        buffer[ix + 2] *= CONVERT_G_TO_MS2;

        int32_t delay_time = next_tick - micros();
        if (delay_time > 0) {
            delayMicroseconds(delay_time);
        }
    }

    Serial.println("Buffer filled");

    // Turn the raw buffer in a signal which we can the classify
    signal_t signal;
    int err = numpy::signal_from_buffer(buffer, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
    if (err != 0) {
        ei_printf("Failed to create signal from buffer (%d)\n", err);
        return;
    }

    Serial.println("Signal created");

    // Run the classifier
    ei_impulse_result_t result = { 0 };

    Serial.println("Inference started");

    err = run_classifier(&signal, &result, debug_nn);
    if (err != EI_IMPULSE_OK) {
        ei_printf("ERR: Failed to run classifier (%d)\n", err);
        return;
    }

    Serial.println("Inference done");

    // print the predictions
    ei_printf("Predictions ");
    ei_printf("(DSP: %d ms., Classification: %d ms., Anomaly: %d ms.)",
        result.timing.dsp, result.timing.classification, result.timing.anomaly);
    ei_printf(": \n");
    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        ei_printf("    %s: %.5f\n", result.classification[ix].label, result.classification[ix].value);
    }

}