import numpy as np
#correct spi mode is spi.mode = 0b01


class DAC_80508:
    """
    Class for the used Octal DAC 80508 from Ti
    Datasheet: https://www.ti.com/lit/ds/symlink/dac80508.pdf?ts=1619120994235&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FDAC80508
    Initialises the DAC. Sets Internal Voltage Reference Gain to 2

    Args:
        cs_pin (int): The Output Line of the Multiplexer which is connected to the DAC
        spi (SpiDev spi): The SPI Interface to be used for communication
        muxer (Multiplexer Object): The Multiplexer which controls the CS Routing
    """
    def __init__(self,cs_pin,spi,muxer):
        """Initialises the DAC. Sets Internal Voltage Reference Gain to 2

        Args:
            cs_pin (int): The Output Line of the Multiplexer which is connected to the DAC
            spi (SpiDev spi): The SPI Interface to be used for communication
            muxer (Multiplexer Object): The Multiplexer which controls the CS Routing
        """
        self.cs_pin=cs_pin
        self.muxer=muxer
        self.spi=spi
        self.input_voltage=38.6#V
        self.gain=10
        self.spi_mode=0b01
        self.full_voltage_range=5.1#V
        self.get_device_id()
        self.set_all_gain(True)
    

    
    def read(self, reg):
        """Low Level one Register read function. 
        Selects MUX Line
        Selects correct SPI Mode 
        Gets the Data from the Register like described in the Datasheet

        Args:
            reg (int): The Register which should be read

        Returns:
            int: Value of the 16 bit Register as an Integer
        """
        self.muxer.set_cs(self.cs_pin)
        if self.spi.mode!=self.spi_mode:
            self.spi.mode=self.spi_mode
        self.spi.xfer2([reg|0x80,0x00,0x00])
        self.muxer.cs_high()
        self.muxer.cs_low()
        retval=self.spi.xfer2([reg|0x80,0x00,0x00])
        self.muxer.cs_high()
        if retval[0]!=(reg|0x80):
            raise RuntimeError
            print("Error in Read")
        return (retval[1]<<8)+retval[2]


    def write(self, reg, value):
        """Low Level Register Write Function.
        Selects MUX Line
        Selects correct SPI Mode 
        Writes the Value to the specified Register like described in the Datasheet
        Args:
            reg (int): The Register to be written to
            value (int): The Value to be written to the Register  
        """
        self.muxer.set_cs(self.cs_pin)
        if self.spi.mode!=self.spi_mode:
            self.spi.mode=self.spi_mode
        self.spi.xfer2([reg,value>>8,value&255])
        self.muxer.cs_high()


    def get_device_id(self):
        """Gets the Device ID of the DAC should always be 517
        """
        val=self.read(0x01)
        msg=val
        if (val>>2)!=517:#"00001000000101":
            print(f"Device ID Register Value {msg} device id {(val>>2):014b} {(val>>2)} does not match 00001000000101 517")
        self.device_id=val>>2
        self.version_id=val&3

    def voltage_to_LSB(self,voltage):
        """Converts the voltage to the nearest corresponding LSB Value. 
        The LSB Value is estimated by the gain and full voltage range.

        Args:
            voltage (float): The voltage that should be converted to LSB

        Returns:
            int: LSB Value corresponding to Voltage
        """
        return int(voltage/(self.full_voltage_range*self.gain) *65535)
    
    def LSB_to_voltage(self,voltage_LSB):
        """Converts the voltage in LSB to a estimated float Voltage in Volts.

        Args:
            voltage_LSB (int): Voltage in LSB to be converted in Volts

        Returns:
            float: Voltage in Volts
        """
        return (voltage_LSB/65535*self.full_voltage_range)*self.gain

    def set_voltage(self, channel, voltage):
        """Sets the DAC channel (0-7) to the desired voltage

        Args:
            channel (int): Channel 0-7 which should be set
            voltage (float): Voltage the channel should be set to

        Returns:
            float: The estimated Voltage which is set
        """
        voltage_lsb=self.voltage_to_LSB(voltage)
        self.write(0x2, (1<<channel)<<8)
        self.write(0x6, voltage_lsb)
        voltage_lsb_ret=self.get_voltage_LSB(channel)
        if voltage_lsb!=voltage_lsb_ret:
            print(f"Could not set Channel {channel} to Voltage {voltage} Return Value of Register {0x8+channel} was {voltage_lsb_ret} tried to set it to {voltage_lsb}")
        return self.LSB_to_voltage(voltage_lsb_ret)
    
    def get_voltage_LSB(self,channel):
        """Gets the set voltage of a specified channel in LSB

        Args:
            channel (int): Channel of which the voltage Register should be read 

        Returns:
            int: Value of Voltage Register of the specified channel
        """
        voltage_lsb_ret=self.read(0x8+channel)
        return self.read(0x8+channel)
    
    def get_voltage(self,channel):
        """Gets the estimated set voltage of a specified channel in Volts

        Args:
            channel (int): Channel of which the voltage Register should be read and converted

        Returns:
            float: in Volts Converted Value of Voltage Register of the specified channel
        """
        return self.LSB_to_voltage(self.get_voltage_LSB(channel))

    def get_all_voltages(self):
        """Gets the estimated set voltage of all channels in Volts

        Returns:
            list of float: in Volts Converted Values of Voltage Registers of all channels
        """
        voltages=np.zeros(8)
        for channel in range(8):
            voltages[channel]=self.get_voltage(channel)
        return voltages

    def set_all_gain(self,gain_x2=True):
        """Sets the gain to two of all DAC Channels -> Voltage Range between 0-5V using the internal Voltage Reference (2.5V)

        Args:
            gain_x2 (bool, optional): Whether to set the Gain to two or not. Defaults to True.
        """
        if gain_x2:
            self.write(0x04,0b11111111)
        else:
            self.write(0x04,0)