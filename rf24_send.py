import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev

GPIO.setmode (GPIO.BCM)

pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin (0, 17)
radio.setPayloadSize(32)
radio.setChannel (0x60)

radio.setDataRate(NRF24.BR_2MBPS)
radio.setPALevel(NRF24.PA_MIN)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

#radio.openReadingPipe(1, pipes[1])
radio.openWritingPipe(pipes[1])
radio.printDetails()
#radio.startListening()

while True:
	message = list("Hello World")
	radio.write(message)
	print ("We sent the message of{}".format(message))

	# Check if it returned a ackPL
	if radio.isAckPayloadAvailable():
		returnedPL = []
		radio.read(returnedPL, radio.getDynamicPayloadSize())
		print("Our returned payload was {}".format (returnedPL))
	else:
		print("No payload received")
	time.sleep(1)
	