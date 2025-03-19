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

//deep sleep = 31s, idle = ca 42009us, wifi on = ca 220906us, sensor_reading = 23528us, transmission time = ca 497us

// state transitions: 
// off/deep_sleep -> idle (booting) -> wifi_on -> sensor_reading -> transmission -> deep_sleep 

int measureDistance()
{
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  Serial.print("\r\nDuration in read_sensor state:\t" + String(duration) + " us");

  int distance = duration * 0.034 / 2;
  Serial.print("\r\nDistance (cm):\t");
  Serial.println(distance);
  return distance;
}

// callback when data is sent
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status)
{
  Serial.print("Send status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Ok" : "Error");
}

void OnDataRecv(const uint8_t *mac, const uint8_t *data, int data_len)
{
  Serial.print("Received data:\t");
  Serial.println((char *)data);
  Serial.println("");
}

void setup()
{
  // Initialize
  Serial.begin(115200);
  unsigned long endIdle = micros();
  unsigned long idleTime = endIdle - startIdle;
  Serial.println("Idle state time:\t" + String(idleTime));  // idleTime state is the time in wakeup state, before the WiFi is turned on. 
  
  // Turn on WiFi
  unsigned long startWiFiOn = micros();
  WiFi.mode(WIFI_STA);
  esp_now_init();

  // Initialize the HC-SR04 pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // send and receive callback
  esp_now_register_send_cb(OnDataSent);
  esp_now_register_recv_cb(OnDataRecv);

  // Set the peer info
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  esp_now_add_peer(&peerInfo);

  // WiFi is not turned off, but it transitions to read_sensor state. 
  unsigned long endWiFiOn = micros();
  unsigned long wiFiOnTime = endWiFiOn - startWiFiOn;
  Serial.println("WiFiOn state time:\t" + String(wiFiOnTime));

  // Measure the distance
  unsigned long startReadSensor = micros();  
  int distance = measureDistance();
  unsigned long endReadSensor = micros();  
  unsigned long readSensorTime = endReadSensor - startReadSensor;
  Serial.println("read_sensor :\t" + String(readSensorTime));

  // Send the message
  unsigned long startTransmission = micros();  // Timestamp before sending
  String status = distance < DISTANCE_THRESHOLD ? "Occupied" : "Free";
  Serial.println("Sending data:\t" + String(status));
  esp_now_send(broadcastAddress, (uint8_t *)status.c_str(), status.length());
  unsigned long endTransmission = micros();  // Timestamp after sending
  unsigned long transmissionTime = endTransmission - startTransmission;
  Serial.println("Transmission state time:\t" + String(transmissionTime));

  // // Prepare to sleep
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  Serial.println("ESP32 sleep for " + String(TIME_TO_SLEEP) + " Seconds\n");
  Serial.flush();
  esp_deep_sleep_start();
  Serial.println("This will never be printed");
}

void loop()
{
  // This is not going to be called
}

