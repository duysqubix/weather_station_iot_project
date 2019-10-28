/******************************************************************************
MQTT_Switch_Example.ino
Example for controlling a light using an MQTT switch
by: Alex Wende, SparkFun Electronics

This sketch connects the ESP32 to a MQTT broker and subcribes to the topic
room/light. When the button is pressed, the client will toggle between
publishing "on" and "off".
******************************************************************************/
#define T_ON (0)
#define T_OFF (1)
#define TOGGLE(PIN) (digitalRead(PIN) ? digitalWrite(PIN, LOW) : digitalWrite(PIN, HIGH))

#include "Arduino.h"
#include <WiFi.h>
#include <PubSubClient.h>


const char *ssid = "IBR600B-6ce";   // name of your WiFi network
const char *password = "MM190204400464"; // password of the WiFi network
//const char *ssid = "Kabouternet-5G-1";
//const char *password = "Dawie2018";
//const char *ssid = "Duan's iPhone";
//const char *password = "o57rqe0ji4wmy";
//const char *ssid = "FBI Surveillance Van 13";
//const char *password = "Psi6596581";


const char *ID = "Magnometer_IoT";  // Name of our device, must be unique
const char *TOPIC = "iot/magnometer";  // Topic to subcribe to

IPAddress broker(192, 168, 0, 133); // IP address of your MQTT broker eg. 192.168.1.50
WiFiClient wclient;

PubSubClient client(wclient); // Setup MQTT client
bool state = 0;
const int magnetometer_reset_pin = 0;


// Connect to WiFi network
void setup_wifi() {
    Serial.print("\nConnecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password); // Connect to network

    while (WiFi.status() != WL_CONNECTED) { // Wait for connection
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("WiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
}

// Reconnect to client
void reconnect() {
    // Loop until we're reconnected
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        // Attempt to connect
        if (client.connect(ID)) {
            Serial.println("connected");
            Serial.print("Publishing to: ");
            Serial.println(TOPIC);
            Serial.println('\n');

        } else {
            Serial.println(" try again in 5 seconds");
            // Wait 5 seconds before retrying
            delay(5000);
        }
    }
}

void setup() {

    // TURN ON Magnetometer Circuitry
    pinMode(magnetometer_reset_pin, OUTPUT);
    digitalWrite(magnetometer_reset_pin, T_ON);
    
    Serial.begin(115200); // Start serial communication at 115200 baud
    delay(100);
    
    setup_wifi(); // Connect to network
    client.setServer(broker, 1883);

    delay(1000);

}

String mag_info;
char to_send[50];

void publish_data() {
  mag_info = Serial.readStringUntil('\n');
  mag_info.toCharArray(to_send, mag_info.length() + 1);

  if (mag_info.length() > 1){
    Serial.println(to_send);
    client.publish(TOPIC, to_send);
  }

  mag_info = "";

}


void loop() {

    if (!client.connected()) {
        reconnect();
    }
    client.loop();
    publish_data();
    //TOGGLE(magnetometer_reset_pin);

}
