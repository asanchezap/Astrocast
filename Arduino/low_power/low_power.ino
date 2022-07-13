#include <LowPower.h>
int LED = 13;

volatile int state = LOW;

void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(2), inter, LOW);
  
  LowPower.powerDown(SLEEP_FOREVER, ADC_OFF, BOD_OFF); 
         
  // Solo se despierta del modo sleep con interrupciones de nivel LOW
  // Otra opción es dormir durante 8s varias veces seguidas en un bucle for por ejemplo
}

void inter(){
  digitalWrite(LED, HIGH);
  delay(1000);
  digitalWrite(LED, LOW); 
  LowPower.powerDown(SLEEP_FOREVER, ADC_OFF, BOD_OFF);
}

void loop() {
  //LowPower.powerDown(SLEEP_FOREVER, ADC_OFF, BOD_OFF);      
    
  /*
  LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  digitalWrite(LED, HIGH);
  delay(1000);
  digitalWrite(LED, LOW); 
  */


}
