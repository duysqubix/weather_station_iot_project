/******************************************************************************
MQTT_Switch_Example.ino
Example for controlling a light using an MQTT switch
by: Alex Wende, SparkFun Electronics

This sketch connects the ESP32 to a MQTT broker and subcribes to the topic
room/light. When the button is pressed, the client will toggle between
publishing "on" and "off".
******************************************************************************/
#define DRIVER_OUTPUT (1)
#define RECIEVER_OUTPUT (0)

#include "Arduino.h"
#include <Wire.h>
#include <MLX90393.h> //From https://github.com/tedyapo/arduino-MLX90393 by Theodore Yapo
MLX90393 mlx;
MLX90393::txyz data; //Create a structure, called data, of four floats (t, x, y, and z)


const int RTSPin = 4;
bool state = 0;


void setup() {

    //RS485 RTS Pin Setup
    pinMode(RTSPin, OUTPUT);
    digitalWrite(RTSPin, DRIVER_OUTPUT);
    
    Serial.begin(115200); // Start serial communication at 115200 baud
    delay(100);
    Wire.begin();
    byte status = mlx.begin(0, 1);
    Serial.print("Start status: 0x");
    if (status < 0x10) Serial.print("0"); //Pretty output
    Serial.println(status, BIN);

    mlx.setGainSel(1);
    mlx.setResolution(0, 0, 0); //x, y, z
    mlx.setOverSampling(0);
    mlx.setDigitalFiltering(0);
    delay(100);
    Serial.println("READY FOR TRANSMISSION");
    Serial.println("x,y,z,tot,temp");

}

String tmp_mag;
String tmp_mag_x;
String tmp_mag_y;
String tmp_mag_z;
String tmp_temp;
String tmp_concat_string;

void publish_data() {
    char temp[50];

    tmp_mag = String(sqrt(pow(data.x, 2) + pow(data.y, 2) + pow(data.z, 2)));
    tmp_mag_x = String(data.x);
    tmp_mag_y = String(data.y);
    tmp_mag_z = String(data.z);
    tmp_temp = String(data.t);
    tmp_concat_string = tmp_mag_x + "," + tmp_mag_y + "," + tmp_mag_z + "," + tmp_temp;

    Serial.print(tmp_mag_x);
    Serial.print(',');
    Serial.print(tmp_mag_y);
    Serial.print(',');
    Serial.print(tmp_mag_z);
    Serial.print(',');
    Serial.print(tmp_mag);
    Serial.print(',');
    Serial.println(tmp_temp);
    delay(1000);

}


void loop() {
    mlx.readData(data);
    publish_data();
}
