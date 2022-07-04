import Adafruit_DHT
import time

SENSOR_DHT = Adafruit_DHT.DHT11
PIN_DHT = 7

while True:
	humedad, temperatura = Adafruit_DHT.read(SENSOR_DHT, PIN_DHT)
	if humedad is not None and temperatura is not None:
		print("Temp: {0:0.1f}C Hum: {1:0.1f}%".format(temperatura, humedad))
	else:
		print("Fallo en la lectura, revisa el circuito")
	time.sleep(3)
