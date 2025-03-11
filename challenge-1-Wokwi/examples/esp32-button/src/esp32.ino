#define LED  12  // The digital pin to which a led is connected.
#define BUTTON 4 // The digital pin to which the button is connected

bool led_value = 0;

void IRAM_ATTR triggr_led(){
  digitalWrite(LED, !digitalRead(LED));
}

void setup() {
  //Pin Setup
  pinMode(LED, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);
  //Serial Setup
  Serial.begin(115200);
  //ISR
  attachInterrupt(BUTTON, triggr_led, RISING);


}
void loop() {
  delay(10);
}
