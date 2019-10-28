/******************************************************************************
MQTT_Switch_Example.ino
Example for controlling a light using an MQTT switch
by: Alex Wende, SparkFun Electronics

This sketch connects the ESP32 to a MQTT broker and subcribes to the topic
room/light. When the button is pressed, the client will toggle between
publishing "on" and "off".
******************************************************************************/
#include "Arduino.h"
#include <WiFi.h>
#include <PubSubClient.h>


const char *ssid = "IBR600B-6ce";   // name of your WiFi network
const char *password = "MM190204400464"; // password of the WiFi network

const char *ID = "Geiger_IoT";  // Name of our device, must be unique
const char *TOPIC = "iot/geiger";  // Topic to subcribe to

IPAddress broker(192, 168, 0, 88); // IP address of your MQTT broker eg. 192.168.1.50
WiFiClient wclient;

PubSubClient client(wclient); // Setup MQTT client
bool state = 0;


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

byte status;
void setup() {
    Serial.begin(115200); // Start serial communication at 115200 baud
    delay(100);
    setup_wifi(); // Connect to network
    client.setServer(broker, 1883);
    Serial.print("Start status: 0x");
    if (status < 0x10) Serial.print("0"); //Pretty output
    Serial.println(status, BIN);
    delay(100);

}


String rad_info;
char to_send[50];

void publish_data() {
    rad_info = Serial.readStringUntil('\n');
    rad_info.toCharArray(to_send, rad_info.length() + 1);

    Serial.println(to_send);
  
    client.publish(TOPIC, to_send);


}


void loop() {

    if (!client.connected()) {
        reconnect();
    }
    client.loop();
    
    publish_data();

}
