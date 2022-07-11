/*
  IOT PROYECT WITH ARDUINO AND ASTROCAST MODULE
  
  Description:  
    - Reads temperature sensor (LM35) and sends the data via the Astrocast module to the satellite each hour
    - Checks ACK from satellite each 5 min. If available gets RTC
    - El ID de mensaje es un contador ascendente
    
  Arduino compatibility checked: Arduino MEGA

  Author: Amelia Sánchez (Hispasat)
  Date: july 2022

*/

#include <astronode.h>

#define ASTRONODE_SERIAL Serial1
#define ASTRONODE_SERIAL_BAUDRATE 9600


// -----------------------------------------------------------------------------------------------
// Definitions
// -----------------------------------------------------------------------------------------------

//#define ASTRONODE_WLAN_SSID "DIGIFIBRA-AS3x"
//#define ASTRONODE_WLAN_KEY "95uUaTGsDX"
#define ASTRONODE_WLAN_SSID "MiFibra-DA72"
#define ASTRONODE_WLAN_KEY "a3rSfZJQ"
#define ASTRONODE_AUTH_TOKEN "zPxrSpbuRY4TpX3ZIVAWdBpKMJRuwicc6Q0cEzaShajiUX3amDD2wrn6AWOiHQ6IV2WH60viVQPcrgYXOQi2NjPOD2KRU0lz"

#define ASTRONODE_GEO_LAT 0.0
#define ASTRONODE_GEO_LON 0.0

#define ASTRONODE_WITH_PLD_ACK true
#define ASTRONODE_WITH_GEO_LOC true
#define ASTRONODE_WITH_EPHEMERIS true
#define ASTRONODE_WITH_DEEP_SLEEP_EN false
#define ASTRONODE_WITH_MSG_ACK_PIN_EN false
#define ASTRONODE_WITH_MSG_RESET_PIN_EN false

int sz = 25;
uint8_t data2[30] = {"Hello Astrocast from Arduino!"};
uint8_t data[25] = {"ARDUINO: Temp[*C] = 25.03"};


uint16_t counter = 0;

ASTRONODE astronode;

void setup()
{
  Serial.begin(9600);
  while (!Serial);
  
  //Enable debugging messages on Astronode S library
  astronode.enableDebugging(Serial, false);

  ASTRONODE_SERIAL.begin(ASTRONODE_SERIAL_BAUDRATE);

  //Initialize terminal
  astronode.begin(ASTRONODE_SERIAL);

  //Write configuration
  astronode.configuration_write(ASTRONODE_WITH_PLD_ACK,
                                ASTRONODE_WITH_GEO_LOC,
                                ASTRONODE_WITH_EPHEMERIS,
                                ASTRONODE_WITH_DEEP_SLEEP_EN,
                                ASTRONODE_WITH_MSG_ACK_PIN_EN,
                                ASTRONODE_WITH_MSG_RESET_PIN_EN);

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

  delay(1000);
}



float temp;
float an;
int i = 0;
int decenas;
int unidades;
int decimas;
int centesimas;


void rellenarTemperatura(uint8_t d[25], float t){
  decenas = int(t/10);
  unidades = int(t-decenas*10);
  decimas = int(10*(t-unidades-decenas*10));
  centesimas = int(t*100-decimas*10-unidades*100-decenas*1000);
  d[20] = char(decenas);
  d[21] = char(unidades);
  d[23] = char(decimas);
  d[24] = char(centesimas);
}

void loop()  {
  // Lectura de temperatura y creación del mensaje a enviar
  an = analogRead(A2);
  temp = an*5000/10240;;
  rellenarTemperatura(&data[25], temp);


  //Envío el mensaje al módulo astrocast
  //if (astronode.enqueue_payload(data2, sizeof(data2), counter) == ANS_STATUS_SUCCESS){
  if (astronode.enqueue_payload(data2, sz, counter) == ANS_STATUS_SUCCESS){
    Serial.println("Message enqueued: ");
    counter++;
  }
  Serial.println("one");
/*
  // For para enviar mensaje cada hora pero revisar si hay ACK cada 5 min (1h = 60min = 12*5min)
  for(i=0; i<12; i++){
    //Poll for new events
    uint8_t event_type;
    astronode.event_read(&event_type);

    if (event_type == EVENT_MSG_ACK){
      uint16_t counter_read = 0;
      if (astronode.read_satellite_ack(&counter_read) == ANS_STATUS_SUCCESS){
        //Querry RTC time and clear ACK
        uint32_t rtc_time;
        astronode.rtc_read(&rtc_time);
        Serial.println(rtc_time);
        astronode.clear_satellite_ack();
      }
    }
    else if (event_type == EVENT_RESET){
      astronode.clear_reset_event();
    }
    delay(5*60*1000);
  }*/
  delay(10000);
}
