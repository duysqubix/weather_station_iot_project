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
#include <stdint.h>

const char *ssid =  "IBR600B-6ce";   // name of your WiFi network
const char *password =  "MM190204400464"; // password of the WiFi network

const byte SWITCH_PIN = 0;           // Pin to control the light with
const char *ID = "Example_Switch";  // Name of our device, must be unique
const char *TOPIC = "iot/wtx520";  // Topic to subcribe to

IPAddress broker(192,168,0, 133); // IP address of your MQTT broker eg. 192.168.1.50
WiFiClient wclient;

PubSubClient client(wclient); // Setup MQTT client
bool state=0;

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
  Serial.begin(115200); // Start serial communication at 115200 baud
  pinMode(SWITCH_PIN,INPUT);  // Configure SWITCH_Pin as an input
  digitalWrite(SWITCH_PIN,HIGH);  // enable pull-up resistor (active low)
  delay(100);
  setup_wifi(); // Connect to network
  client.setServer(broker, 1883);
}


const byte numChars = 64;
char incoming_data[numChars];
bool newData = false;


void recieve_data(){
  static byte idx = 0;
  char endMarker = '\n';
  char rc;

  while(Serial.available() > 0 && newData == false){
    rc = Serial.read();

    if (rc != endMarker){
      incoming_data[idx++] = rc;

      if (idx >= numChars){
        idx = numChars-1;
      }
    }
    else{
      incoming_data[idx] = '\0';
      idx = 0;
      newData = true;
    }
  }
}

void show_data(){
  if (newData == true){
    Serial.println(incoming_data);
    newData = false;
  }
}

void loop() {
  //"0r2,Ta=25.7C,Ua=13.5P,Pa=0.8428BFPJ\r\n";
  
  if (!client.connected())  // Reconnect if connection is lost
  {
    reconnect();
  }
  client.loop();
  
  recieve_data();
  if (newData == true){
    Serial.print("Sending data via MQTT");
    Serial.println(incoming_data);
    client.publish(TOPIC, incoming_data);
    newData = false;

  }

   delay(5000);
  }
