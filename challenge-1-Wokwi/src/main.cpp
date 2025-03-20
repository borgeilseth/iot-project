#include <Arduino.h>
#include <esp_now.h>
#include <WiFi.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// Define the HC-SR04 pins
#define TRIG_PIN 5
#define ECHO_PIN 18

// Define the threshold distance in cm
#define DISTANCE_THRESHOLD 50

// Define the time to sleep in seconds
#define uS_TO_S_FACTOR 1000000
#define TIME_TO_SLEEP 31

unsigned long startIdle = micros();

// Define the MAC address of the central sink node
uint8_t broadcastAddress[] = {0x8C, 0xAA, 0xB5, 0x84, 0xFB, 0x90};

// Create peer interface
esp_now_peer_info_t peerInfo;

// deep sleep = 31s, idle = ca 42009us, wifi on = ca 220906us, sensor_reading = 23528us, transmission time = ca 497us

// state transitions:
// off/deep_sleep -> idle (booting) -> wifi_on -> sensor_reading -> transmission -> deep_sleep

// Timing printout order:
// idle, wifi_on, sensor_reading, transmission

int measureDistance()
{
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  int distance = round(duration * 0.034 / 2);
  return distance;
}

void setup()
{
  // Initialize
  Serial.begin(115200);
  Serial.println("\n--------------------------------");
  Serial.println("idle, wifi_on, sensor_reading, transmission, distance");
  unsigned long endIdle = micros();
  Serial.print(String(endIdle - startIdle) + ","); // Timestamp to boot and idle

  // Turn on WiFi
  WiFi.mode(WIFI_STA);
  esp_now_init();

  // Initialize the HC-SR04 pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Set the peer info
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  esp_now_add_peer(&peerInfo);

  // WiFi is not turned off, but it transitions to read_sensor state.
  unsigned long endWiFiOn = micros();
  Serial.print(String(endWiFiOn - endIdle) + ","); // Timestamp to turn on WiFi

  // Measure the distance
  int distance = measureDistance();
  unsigned long endReadSensor = micros();
  Serial.print(String(endReadSensor - endWiFiOn) + ","); // Timestamp to read the sensor

  // Send the message
  String status = distance < DISTANCE_THRESHOLD ? "Occupied" : "Free";        // Determine the status
  esp_now_send(broadcastAddress, (uint8_t *)status.c_str(), status.length()); // Send the status

  unsigned long endTransmission = micros();                     // Timestamp after sending
  Serial.print(String(endTransmission - endReadSensor) + ", "); // Timestamp to send the message
  Serial.print(String(distance) + ", ");                        // Print the distance

  // // Prepare to sleep
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  Serial.println("\nDeep Sleep Time: \t " + String(TIME_TO_SLEEP * uS_TO_S_FACTOR) + " us");
  Serial.println("--------------------------------\n");
  Serial.flush();
  esp_deep_sleep_start();
  Serial.println("This will never be printed");
}

void loop()
{
  // This is not going to be called
  delay(10);
}
