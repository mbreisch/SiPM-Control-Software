#from ADC import ADS_8166
from board_wrapper.genericPIWrapper import genericAPI
import spidev
import time
import numpy as np

"""
spi = spidev.SpiDev()
spi_port=0
speedHZ=400000
spi.open(spi_port, 0)
spi.mode = 0b01
spi.max_speed_hz = speedHZ
register=2
time.sleep(0.01)
for k in range(5):
    to_send = [0x81, 0x00, 0x00]
    print(spi.xfer2(to_send))
    to_send=[0x00, 0x00, 0x05]
    print(spi.xfer2(to_send))
    to_send=[0x80, 0x00, 0x00]
    print(spi.xfer2(to_send))
    to_send=[0x00, 0x00, 0x06]
    print(spi.xfer2(to_send))
    to_send=[0x80, 0x00, 0x00]
    print(spi.xfer2(to_send))
    time.sleep(1)

"""
spi = spidev.SpiDev()
spi_port=0
speedHZ=400000
spi.open(spi_port, 1)
spi.max_speed_hz = speedHZ
#myboard=genericAPI()
#myboard.sensorSPIConfig(cs_pin=0, speedKHz=1600, spiMode=1, spi_16bit=False)
dut="ADC"
if dut=="DAC":
    spi.mode = 0b01
    dac=DAC_80508(0,spi)
    print(dac.device_id)
    print(dac.version_id)

    channel_1=0
    channel_2=7
    print(f"All voltages {dac.get_all_voltages()}")
    print(f"Set voltage of channel {channel_1} {dac.set_voltage(channel_1,5)}")
    print(f"All voltages {dac.get_all_voltages()}")
    print(f"Set voltage of channel {channel_2} {dac.set_voltage(channel_2,1.4)}")
    print(f"All voltages {dac.get_all_voltages()}")
    time.sleep(2)
    print(f"Set voltage of channel {channel_1} {dac.set_voltage(channel_1,1)}")
    print(f"All voltages {dac.get_all_voltages()}")
    time.sleep(2)
    print(f"Set voltage of channel {channel_1} {dac.set_voltage(channel_1,0.5)}")
    print(f"All voltages {dac.get_all_voltages()}")
    time.sleep(2)
    print(f"Set voltage of channel {channel_1} to 0V {dac.set_voltage(channel_1,0.01)}")
    print(f"Set voltage of channel {channel_2} to 0V {dac.set_voltage(channel_2,0)}")
    print(f"All voltages {dac.get_all_voltages()}")
else:
    spi.mode = 0b00
    vals=np.zeros(300)
    """
    for k in range(100):
        spi.xfer([0b00001000,29,0])
        val=spi.xfer([0,0])
        vals[3*k]=(val[0]<<8)+val[1]
        spi.xfer([0b00001000,29,1])
        val=spi.xfer([0,0])
        vals[3*k+1]=(val[0]<<8)+val[1]
        spi.xfer([0b00001000,29,2])

        val=spi.xfer([0,0])
        vals[3*k+2]=(val[0]<<8)+val[1]
        #works for selecting the correct channel
    """
    #print(vals)
    read_val=0b00010000
    write_val=0b00001000
    #read 29 should be 2
    print(spi.xfer([read_val,0,0]))#->a connection to mosi must be there result is [x, y, 0, 16, 17, 16, 0, 15] starting with bit four it replies message
    #access
    print(spi.xfer([write_val,0x00,0b10101010]))#->a connection to mosi must be there result is [x, y, 0, 16, 17, 16, 0, 15] starting with bit four it replies message
    #deactivate adc
    print(spi.xfer([read_val,0,0]))#->a connection to mosi must be there result is [x, y, 0, 16, 17, 16, 0, 15] starting with bit four it replies message
    #read
    print(spi.xfer([read_val,0,0]))
    print(spi.xfer([read_val,0,0]))
    print(spi.xfer([read_val,0,0]))

    #for k in range(5):
     #   adc.write_access(True)
      #  time.sleep(1)
        #spi.xfer2([])
    """
    adc.on_the_fly_mode(True)
    for k in range(5):
        raw_vals=adc.get_values_on_the_fly([x for x in range(8)])
        print(f"RAW {raw_vals}")
        print(f"Converted {adc.convert_values(raw_vals)}")

        time.sleep(1)
    """

