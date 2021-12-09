from digi.xbee.devices import XBeeDevice
from pushbullet import Pushbullet
from digi.xbee.io import IOLine, IOMode
import time
import threading

pb = Pushbullet("o.fDcFEJQb9GasabSy6NDyoANxe4yHLA2J")
#print(pb.devices)

# Port of XBee on Pi
PORT = "/dev/ttyUSB0"
# Baud rate of local XBee (or any XBee really, they work best on 9600
BAUD_RATE = 9600

#Node ID of remote XBee, set in XCTU console
REMOTE_NODE_ID = "node1"

#Port on remote XBee to listen to
IOLINE_IN = IOLine.DIO0_AD0


def main():
    print("PIR(Motion Detectrion) Sensor Feedback")

    stop = False
    th = None

    #Initialize local XBee on Pi
    local_device = XBeeDevice(PORT, BAUD_RATE)

    try:
        local_device.open()

        # Obtain the remote XBee device from the XBee network.
        xbee_network = local_device.get_network()
        remote_device = xbee_network.discover_device(REMOTE_NODE_ID)
        if remote_device is None:
            print("Could not find the remote device")
            exit(1)

        #Configure desired pin on remote XBee as analog input
        remote_device.set_io_configuration(IOLINE_IN, IOMode.ADC)

        #Actual task that probes the pin every 1 min-defined by sleep(1) below
        def read_adc_task():
            while not stop:
                # Read the analog value from the remote input line.
                value = remote_device.get_adc_value(IOLINE_IN)
                #Motionless values sat at about 550 most of the time, motion was about 1050. 650 is safe limit
                if value > 650:
                    for x in range(1,5):
                        value = remote_device.get_adc_value(IOLINE_IN)
                        if value < 650: break
                        elif x == 4: print("Intruder detected!")
						push = pb.push_note("Alert!","Intruder detected at node1!")

                time.sleep(0.2)

        th = threading.Thread(target=read_adc_task)

        time.sleep(0.5)
        th.start()

        input()

    finally:
        stop = True
        if th is not None and th.isAlive():
            th.join()
        if local_device is not None and local_device.is_open():
            local_device.close()


if __name__ == '__main__':
    main()
