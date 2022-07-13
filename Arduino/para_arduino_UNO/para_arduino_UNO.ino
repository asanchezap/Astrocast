/*
  This example enqueue a single message in the queue of the Astronode S.
  It checks periodically if a new event is available.
  If a "satellite acknowledge" event is receieved, a new message is enqueued in the module.

  The circuit:
  - Nucleo-64 STM32l476 (TX -> D2(PA10), RX -> D8(PA9), GND -> GND, 3V3 -> 3V3)
  - Arduino MKR1400 (TX -> D13(RX), RX -> D14 (TX), GND -> GND, 3V3 -> VCC)
  - Arduino UNO (TX -> D2(with level shifter), RX -> D3(with level shifter), GND -> GND, 3V3 -> VCC)
  - Astronode S devkit (sat or wifi) attached
*/

#include <astronode.h>
#define ASTRONODE_SERIAL Serial    // Arduino sin conexion al ordenador


#define ASTRONODE_SERIAL_BAUDRATE 9600

#define ASTRONODE_WLAN_SSID "DIGIFIBRA-AS3x"
#define ASTRONODE_WLAN_KEY "95uUaTGsDX"
//#define ASTRONODE_WLAN_SSID "MiFibra-DA72"
//#define ASTRONODE_WLAN_KEY "a3rSfZJQ"
#define ASTRONODE_AUTH_TOKEN "zPxrSpbuRY4TpX3ZIVAWdBpKMJRuwicc6Q0cEzaShajiUX3amDD2wrn6AWOiHQ6IV2WH60viVQPcrgYXOQi2NjPOD2KRU0lz"

#define ASTRONODE_GEO_LAT 0.0
#define ASTRONODE_GEO_LON 0.0

/*
#define ASTRONODE_WITH_PLD_ACK true
#define ASTRONODE_WITH_GEO_LOC true
#define ASTRONODE_WITH_EPHEMERIS true
#define ASTRONODE_WITH_DEEP_SLEEP_EN false
#define ASTRONODE_WITH_MSG_ACK_PIN_EN true
#define ASTRONODE_WITH_MSG_RESET_PIN_EN true
*/

uint8_t data[30] = {"Hello Astrocast from Arduino!"};
uint16_t counter = 0;

ASTRONODE astronode;

void setup(){  
  //Serial.begin(9600);
  //while (!Serial);
  
  //Enable debugging messages on Astronode S library
  //astronode.enableDebugging(Serial, false);

  ASTRONODE_SERIAL.begin(ASTRONODE_SERIAL_BAUDRATE);

  //Initialize terminal
  astronode.begin(ASTRONODE_SERIAL);

  //Write configuration (ASTRONODE_WITH_PLD_ACK, ASTRONODE_WITH_GEO_LOC, ASTRONODE_WITH_EPHEMERIS, ASTRONODE_WITH_DEEP_SLEEP_EN, ASTRONODE_WITH_MSG_ACK_PIN_EN, ASTRONODE_WITH_MSG_RESET_PIN_EN)
  astronode.configuration_write(true, true, true, false, true, true);

  //Set geolocation
  astronode.geolocation_write((int32_t)(ASTRONODE_GEO_LAT * 10000000), (int32_t)(ASTRONODE_GEO_LON * 10000000));

  //Save configuration
  astronode.configuration_save();

  //Read configuration
  astronode.configuration_read();

  //If Wifi devkit, set credential info
  if (astronode.config.product_id == TYPE_WIFI_DEVKIT)
  {
    //Set WiFi configuration:
    astronode.wifi_configuration_write(ASTRONODE_WLAN_SSID, ASTRONODE_WLAN_KEY, ASTRONODE_AUTH_TOKEN);
  }

  // Get serial number
  String sn;
  astronode.serial_number_read(&sn);

  //Get GUID
  String guid;
  astronode.guid_read(&guid);

  //Clear old messages
  astronode.clear_free_payloads();

  astronode.enqueue_payload(data, sizeof(data), counter);
  counter++;

  attachInterrupt(digitalPinToInterrupt(2), inter, RISING);
}


bool event = true;
void inter(){
  digitalWrite(13, HIGH);
  event = true;
  delay(100);
  digitalWrite(14, LOW);
}

void send_pl(){
  ans_status_e result = astronode.enqueue_payload(data, sizeof(data), counter);
  if (result == ANS_STATUS_SUCCESS) {
    counter++;
  } else 
    Serial.println("message NOT sent");
}

void loop()  {

  //Querry RTC time
  uint32_t rtc_time;
  ans_status_e result = astronode.rtc_read(&rtc_time);
  Serial.println(rtc_time);
  
  //if(digitalRead(2) == HIGH) event = true;

  if(event){
    //Poll for new events
    uint8_t event_type;
    astronode.event_read(&event_type);
    Serial.println(event_type);
  
    if (event_type == EVENT_MSG_ACK){
      uint16_t counter_read = 0;
      if (astronode.read_satellite_ack(&counter_read) == ANS_STATUS_SUCCESS){
        astronode.clear_satellite_ack();
        send_pl();
      }
    }
    else if (event_type == EVENT_RESET){
      astronode.clear_reset_event();
      send_pl();
    }
    event = false;
  }

  delay(10000);
}
