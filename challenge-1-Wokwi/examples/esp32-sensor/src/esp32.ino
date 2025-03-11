/*
* DHT 22:
* Implementation:
* https://github.com/beegee-tokyo/DHTesp/blob/master/DHTesp.cpp
* I2C Read Sensor (161-293)
* Available Functions:
* https://github.com/beegee-tokyo/DHTesp/blob/master/DHTesp.h
* For vscode search your dependencies here: https://registry.platformio.org/
*
*/
#include "DHTesp.h" //https://github.com/beegee-tokyo/DHTesp/tree/master

#define LED  12  // LED Digital pin
#define SLIDE 13 // Potentiometer Digital pin
#define DHT_PIN 15

DHTesp dhtSensor;

void setup() {
pinMode(SLIDE, INPUT);
dhtSensor.setup(DHT_PIN, DHTesp::DHT22);
Serial.begin(115200);
}

void loop() {
  float temperature = dhtSensor.getTemperature();
  float humidity = dhtSensor.getHumidity();
  int slide = analogRead(SLIDE);
  int mapped_value = map(slide, 0, 4095, 0, 100);

  Serial.print(slide);
  Serial.println("Temp: " + String(temperature, 2) + "°C");
  Serial.println("Humidity: " + String(humidity, 1) + "%");
  Serial.println("----");
  delay(1000);
  
  //Serial.print(',');
  //Serial.print(mapped_value);
  //Serial.print(',');
  //Serial.print(temperature);
  //Serial.print(',');
  //Serial.println(humidity);
  //delay(10);

}
