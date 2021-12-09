import sys
import time
import Adafruit_DHT
from pushbullet import Pushbullet

pb = Pushbullet("o.h5n1DNMmwsjMJ3v5OJeCHgh6bFsTe9J0")
#print(pb.devices)

sensor = Adafruit_DHT.AM2302
#GPIO pin number, not the board pin number
pin = 4

humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

#Continue getting readings every 60s while we are gettting valid readings
while humidity>0:
   
    # Un-comment the line below to convert the temperature to Fahrenheit.
    temperature = temperature * 9/5.0 + 32
    
    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    # If this happens try again!
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
		push = pb.push_note("Alert!","Temp={0:0.1f}*  Humidity={1:0.1f}%".format(temperature, humidity))
		
    else:
        print('Failed to get reading. Try again!')
        sys.exit(1)

    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    time.sleep(60)
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
