/*
  IOT PROYECT WITH ARDUINO AND ASTROCAST MODULE
  
  Description:  
    - Reads temperature sensor (LM35) and sends the data via the Astrocast module to the satellite each hour
    - Checks ACK from satellite each 5 min. If available gets RTC
    - El ID de mensaje es un contador ascendente
    
  Arduino compatibility checked: Arduino MEGA

  Author: Amelia Sánchez - Hispasat
  Date: july 2022

*/

#include <astronode.h>
#include <LowPower.h>

// -----------------------------------------------------------------------------------------------
// Definitions ASTROCAST
// -----------------------------------------------------------------------------------------------

#define ASTRONODE_SERIAL Serial1
#define ASTRONODE_SERIAL_BAUDRATE 9600

#define ASTRONODE_WLAN_SSID "DIGIFIBRA-AS3x"
#define ASTRONODE_WLAN_KEY "95uUaTGsDX"
//#define ASTRONODE_WLAN_SSID "MiFibra-DA72"
//#define ASTRONODE_WLAN_KEY "a3rSfZJQ"
#define ASTRONODE_AUTH_TOKEN "zPxrSpbuRY4TpX3ZIVAWdBpKMJRuwicc6Q0cEzaShajiUX3amDD2wrn6AWOiHQ6IV2WH60viVQPcrgYXOQi2NjPOD2KRU0lz"

#define ASTRONODE_GEO_LAT 0.0
#define ASTRONODE_GEO_LON 0.0

ASTRONODE astronode;

// -----------------------------------------------------------------------------------------------
// Program variables
// -----------------------------------------------------------------------------------------------

uint16_t counter = 0;
bool event = true;



void setup(){  
  pinMode(13, OUTPUT);
  digitalWrite(13, HIGH);
  Serial.begin(9600);
  while (!Serial);
  
  //Enable debugging messages on Astronode S library
  astronode.enableDebugging(Serial, false);

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
  if (astronode.config.product_id == TYPE_WIFI_DEVKIT){
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

  attachInterrupt(digitalPinToInterrupt(2), inter, RISING);
  digitalWrite(13, LOW);
}





void inter(){
  event = true;
  Serial.println("heyy");
}

void send_pl(){
  // Read temperature sensor and create message
  int an = analogRead(A2);
  float temp = an;
  temp = temp*5000/10240;
  Serial.println(temp);
  String dataString = "ARDUINO: Temp[*C] = " + String(temp);
  uint8_t dataArray[dataString.length()];
  dataString.toCharArray(dataArray, dataString.length());

  // Send message
  ans_status_e result = astronode.enqueue_payload(dataArray, sizeof(dataArray), counter);
  if (result == ANS_STATUS_SUCCESS) {
    counter++;
  } else Serial.println("message NOT sent");
}


void loop()  {  
  //Querry RTC time
  uint32_t rtc_time;
  ans_status_e result = astronode.rtc_read(&rtc_time);
  Serial.println(rtc_time);

  send_pl();

  if(digitalRead(2) == HIGH){
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

  // A dormir durante 30 min
  for(int i=0; i<=6; i++){ 
    // A dormir durante 5 min
    for(int i=0; i<=38; i++) LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  }
}
