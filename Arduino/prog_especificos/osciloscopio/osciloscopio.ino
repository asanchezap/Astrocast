void setup() {
  Serial.begin(500000);
  pinMode(2, INPUT);
  pinMode(3, INPUT);
}

void loop() {
  Serial.print(digitalRead(2));
  Serial.print(" "); 
  Serial.println(digitalRead(3));
}
