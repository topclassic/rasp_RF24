
#!/usr/bin/python
import MySQLdb
import time
import datetime
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev

GPIO.setmode (GPIO.BCM)

# Set link
pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin (0, 17)
radio.setPayloadSize(60)
radio.setChannel (0x60)

radio.setDataRate(NRF24.BR_2MBPS)
radio.setPALevel(NRF24.PA_MIN)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()
radio.openWritingPipe(pipes[1]);
radio.openReadingPipe(0, pipes[1])
radio.printDetails()

radio.startListening()

# Open database connection
db = MySQLdb.connect(host="localhost", user="root", passwd="devilsecret", db="smartelectric")	
# Start loop send and recev
while(True):
	ackPL = [1]
	while  not radio.available(0):
		time.sleep(1/1000)
	#set cursor database	
	c = db.cursor()


	#receive
	receivedMessage = []
	radio.read(receivedMessage, radio.getDynamicPayloadSize())


	id_outlet = ""
	unit = ""
	watt = ""
	checkchar = 0
	for n in receivedMessage:
		# frame format header
		if(n >=32 and n <=126):
			#4 char
			if(checkchar <= 4):
				id_outlet += chr(n)
			#5 char	
			if(checkchar >= 5 and checkchar <= 13):
				unit += chr(n)
			#5 char	
			if(checkchar >= 14 and checkchar <= 22):
				watt += chr(n)

			checkchar = checkchar+1

	radio.writeAckPayload(1, ackPL, len(ackPL))
	print("Loaded payload reply of {}".format(ackPL))		
	print(id_outlet + unit + watt)
	# Check id_outlet 
	check_id = 1
	# Select database
	c.execute("SELECT id_outlet FROM smartelectric")	
	for row in c.fetchall() :
		# Data from rows
		data_id = str(row[0])
		# Change variable
		data_id_int = (int)(data_id )
		id_outlet_int = (int)(id_outlet)
		# Check id_outlet is first or not
		if(data_id_int == id_outlet_int):
			check_id  += 1	

	if(check_id  == 1):
		# Insert if id_outlet first contact
		limitpower = 0.0
		c.execute("INSERT INTO smartelectric (id_outlet, limitpower) VALUES (%s,%s)",(id_outlet, limitpower))
		db.commit()	
		print("ok")
	check_id  = 0

	# update power every 5 min
	c.execute("UPDATE smartelectric SET power=%s WHERE id_outlet=%s ",(watt,id_outlet))
	db.commit()

	# Select limit from database
	c.execute("SELECT id_outlet, limitpower FROM smartelectric")
	for row in c.fetchall() :
		
		data_idoutlet = str(row[0])
		data_limit = str(row[1])

		limit_float = (float)(data_limit)

		limit_str = "%4s%.2f" % (data_idoutlet, limit_float)
		print limit_str
		#send	
		radio.stopListening();
		message = list(limit_str)
		radio.write(message)
		print ("We sent the message of{}".format(message))
		radio.startListening()
		time.sleep(1)