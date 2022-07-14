float num;
float an;


void setup() {
  // Inicializamos comunicación serie
  Serial.begin(9600);
}


void loop() {
    // Esperamos 5 segundos entre medidas
  delay(5000);
 
  an = analogRead(A2);
  num = an*5000/1024;
  Serial.print(analogRead(A2));
  Serial.print("Temperatura: ");
  Serial.print(num/10);
  Serial.print(" *C, ");
  Serial.print((num/10)*1.8+32);
  Serial.println(" *F, "); 
}
