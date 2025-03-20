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

// Define an initial timestamp
unsigned long startIdle = micros();

// Define the MAC address of the central sink node
uint8_t broadcastAddress[] = {0x8C, 0xAA, 0xB5, 0x84, 0xFB, 0x90};

// Create peer interface
esp_now_peer_info_t peerInfo;

// state transitions:
// off/deep_sleep -> idle (booting) -> sensor_reading -> wifi_on -> transmission -> deep_sleep

// Timing printout format (comma-separated):
// idle, sensor, wifi_on, transmission, distance - timestamps in microseconds, distance in cm

// Function to measure the distance
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

  // Initialize the sensor
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Measure the idle time
  unsigned long endIdle = micros();
  Serial.print(String(endIdle - startIdle) + ","); // Timestamp to boot and idle

  // Measure the distance
  int distance = measureDistance();

  // Measure the time to read the sensor
  unsigned long endReadSensor = micros();
  Serial.print(String(endReadSensor - endIdle) + ","); // Timestamp to read the sensor

  // Turn on WiFi
  WiFi.mode(WIFI_STA); // Station mode
  esp_now_init();      // Initialize ESP-NOW

  // Set the peer info
  memcpy(peerInfo.peer_addr, broadcastAddress, 6); // Copy the MAC address
  peerInfo.channel = 0;                            // Set the channel
  peerInfo.encrypt = false;                        // No encryption
  esp_now_add_peer(&peerInfo);                     // Add the peer

  // Measure the time to turn on WiFi
  unsigned long endWiFiOn = micros();
  Serial.print(String(endWiFiOn - endReadSensor) + ","); // Timestamp to turn on WiFi

  // Send the message
  String status = distance < DISTANCE_THRESHOLD ? "Occupied" : "Free";        // Determine the status
  esp_now_send(broadcastAddress, (uint8_t *)status.c_str(), status.length()); // Send the status

  // Measure the time to send the message
  unsigned long endTransmission = micros();
  Serial.print(String(endTransmission - endWiFiOn) + ", "); // Timestamp to send the message
  Serial.println(String(distance) + ", ");                  // Print the distance

  // // Prepare to sleep
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  Serial.println("Deep Sleep Time: \t " + String(TIME_TO_SLEEP * uS_TO_S_FACTOR) + " us");
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
