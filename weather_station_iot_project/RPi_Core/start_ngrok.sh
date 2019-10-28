#! /bin/sh

echo "Resetting"
sleep 30
echo "Attempting to start ngrok"

/usr/bin/ngrok start -config /home/pi/.ngrok2/ngrok.yml \
	       --log=stdout \
	       ssh > /home/pi/ngrok.log &
