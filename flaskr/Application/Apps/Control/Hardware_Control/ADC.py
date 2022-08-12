import numpy as np
#correct spi mode is spi.mode = 0b01
import time

class ADS_8166:
    """
    Class for the used Octal ADC ADS 816x from Ti
    Datasheet: https://www.ti.com/lit/ds/symlink/ads8166.pdf?ts=1619135690040&ref_url=https%253A%252F%252Fwww.google.com%252F
    Initialises the ADC

    Args:
        cs_pin (int): The Output Line of the Multiplexer which is connected to the ADC
        spi (SpiDev spi): The SPI Interface to be used for communication
        muxer (Multiplexer Object): The Multiplexer which controls the CS Routing
    """
    def __init__(self,cs_pin,spi,muxer):
        """Initialises the ADC

        Args:
            cs_pin (int): The Output Line of the Multiplexer which is connected to the ADC
            spi (SpiDev spi): The SPI Interface to be used for communication
            muxer (Multiplexer Object): The Multiplexer which controls the CS Routing
        """
        self.write_access_to_regs=False
        self.fullrange_voltage=4.096#V works better with 5V but should be 4.096
        self.resistor1=270#kohm
        self.resistor2=30#kohm
        self.cs_pin=cs_pin
        self.spi=spi
        self.spi_mode=0b00
        self.muxer=muxer
        #self.set_spi_mode()

    def xfer(self,data):
        """Wrapper for SPI xfer function 
        additionally handles CS Line and SPI Mode Selection

        Args:
            data (list of int): Data for SpiDev xfer function

        Returns:
            list of int: returned Data of SpiDev xfer function
        """
        self.muxer.set_cs(self.cs_pin)
        if self.spi.mode!=self.spi_mode:
            self.spi.mode=self.spi_mode
        ret_data=self.spi.xfer(data)
        self.muxer.cs_high()
        return ret_data



    def read(self, reg):
        """Single Register Read function as specified for the ADC in the Datasheet

        Args:
            reg (int): Register to be read

        Returns:
            int: Value of specified Register
        """
        first_read_byte=(reg>>8)+(1<<4)   
        second_read_byte=reg&255
        self.xfer([first_read_byte,second_read_byte,0x00])
        retval=self.xfer([first_read_byte,second_read_byte,0x00])
        if retval[1]!=0x00 or retval[2]!=0x00:
            #raise Warning
            print(f"Error in Read returned {retval}")
        return retval[0]


    def write(self, reg, value):
        """Single Register Write function as specified for the ADC in the Datasheet

        Args:
            reg (int): Register the value should be written to
            value (int): Value to be written to the Register
        """
        first_write_byte=(reg>>8)+(1<<3)    
        second_write_byte=reg&255
        self.xfer([first_write_byte,second_write_byte,value])


    def set_spi_mode(self,spi_mode=0b01):
        """Change SPI Mode of the ADC.
        At startup spi mode of the ADC is always 01

        Args:
            spi_mode (int, optional): Desired SPI Mode. Defaults to 0b01.
        """
        self.spi.mode=0
        if not self.write_access_to_regs:
            self.write_access(True)
        self.write(0x08,spi_mode)
        self.spi.mode=spi_mode
        ret_val=self.read(0x08)
        if ret_val!=spi_mode:
            print(f"SPI Mode could not be set readback was {ret_val} wanted mode was {spi_mode}")
            return 0
        self.spi_mode=spi_mode
    
    def write_access(self,enable=True):
        """Enable Write Access to the ADC Registers.

        Args:
            enable (bool, optional): Whether Write Access should be enabled or not. Defaults to True.
        """
        if enable:
            self.write_access_to_regs=True
            access_code=0b10101010
            self.write(0x00,access_code)
            ret_val=self.read(0x00)
            if ret_val!=access_code:
                self.write_access_to_regs=False
                print(f"Access could not be enabled got {ret_val} expected {access_code}")
        else:
            self.write(0x00,0x00)

    def enabled_channel_id(self):
        """Enable broadcast of Channel ID before Data Frame.
        """
        if not self.write_access_to_regs:
            self.write_access(True)
        self.write(0x10,1<<4)
    
    def debug_mode(self,enable=True):
        """Set the Debug Mode of the ADC on or off. 
        In Debug mode the ADC returns fixed Data Values as described in the Datasheet.

        Args:
            enable (bool, optional): Whether to turn debug mode on or off. Defaults to True.
        """
        if not self.write_access_to_regs:
            self.write_access(True)
        self.write(0x10,1)

    def select_channel(self,channel,debug=False):
        """Selects the channel of which the ADC should broadcast Data.

        Args:
            channel (int): Channel 1-8 of which the ADC should broadcast the Voltage
            debug (bool, optional): Enables/Disables Print statement for debugging Purposes. Defaults to False.
        """
        self.write(0x1d,channel)
        if debug:
            print(f"Selected Channel is {channel} Readback is {self.read(0x1d)}")
    
    def on_the_fly_mode(self,enable=True):
        """Enables the on the fly Readout mode of the ADC

        Args:
            enable (bool, optional): Enable/Disable. Defaults to True.
        """
        if not self.write_access_to_regs:
            self.write_access(True)
        was_val=self.read(0x1c)
        if enable:
            self.write(0x1c,1)
        else:
            self.write(0x1c,0)
        is_val=self.read(0x1c)
        print(f"The value of 0x1c was {was_val} new value is {is_val}")
    
    def convert_single_value(self,value):
        """Converts the LSB Value to a Voltage in Volts.
        Based on the specified Voltage Divider Resistors and the Voltage Reference (internal V_ref=4.096V)

        Args:
            value (int): Voltage Register Value in LSB which should be converted

        Returns:
            float: Converted Value in Volts
        """
        return (value/65535*self.fullrange_voltage)*(self.resistor1+self.resistor2)/self.resistor2

    def convert_values(self,values):
        """For one value same Function as convert_single_value.
        For list of values in LSB converts all of them to Volts using convert_single_value.


        Args:
            values (int or list of int): LSB Voltage Values

        Returns:
            float or list of float: The converted value(s)
        """
        if isinstance(values,list):
            print(values)
            return [self.convert_single_value(val) for val in values]
        return self.convert_single_value(values)

    def get_values_on_the_fly(self,channels):
        """Get Values of the ADC when it is in on the fly Mode.

        Args:
            channels (list of int): Channels to get the voltage data from

        Returns:
            list of int: Voltage Values of channels in LSB
        """
        if not isinstance(channels,list):
            channels=[channels]
        channels+=[0]
        vals=np.zeros(len(channels))
        for idx,channel in enumerate(channels):
            val=self.xfer([(1<<7)+(channel<<3),0])
            vals[idx]=(val[0]<<8)+val[1]
        return vals[1:]

    def get_voltage(self,channel,std=0.01,samples=100):
        """Gets Voltage of specified channel in Default ADC Mode.
        Takes samples Measurements of channel till the STD of samples consecutive Values is smaller than std.

        Args:
            channel (int): Channel index 0-7
            std (float, optional): Upper Limit of Standard Deviation for 100 Measurments. Defaults to 0.01.
            samples (int,optional): Samples to be taken. Defaults to 100

        Returns:
            float: Mean Voltage of Channel over samples Measurements
        """
        self.select_channel(channel)
        self.xfer([0,0])
        self.xfer([0,0])
        vals=np.zeros(samples)
        time.sleep(0.01)
        for idx in range(int(samples/2)):
            val=self.xfer([0,0])
            val=(val[0]<<8)+val[1]
            vals[idx]=100
            time.sleep(0.005)
        time.sleep(0.005)
        while self.convert_single_value(np.std(vals))>=std:
            for idx in range(samples):
                val=self.xfer([0,0])
                val=(val[0]<<8)+val[1]
                vals[idx]=val
                time.sleep(0.01)
        #print(f"Standard deviation {self.convert_single_value(np.std(vals))}")
        return self.convert_single_value(np.mean(vals))

    def get_all_voltages(self):
        """Gets the Voltage from all eight channels

        Returns:
            np.array: Voltages from all eight channels
        """
        channels=2
        voltages=np.zeros(channels)
        for channel in range(channels):
            voltages[channel]=self.get_voltage(channel)
            time.sleep(0.1)
        return voltages