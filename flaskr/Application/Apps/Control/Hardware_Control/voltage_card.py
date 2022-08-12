from DAC.Hardware_Control.DAC_80508 import DAC_80508 
from DAC.Hardware_Control.ADC import ADS_8166
import time
from simple_pid import PID
import numpy as np
import threading

class Voltage_Card:
    """Software Representation of one Voltage Card. 
    One Voltage Card provides 8 controllable Output Voltages in the Range of approx 0-38V
    Init all controllable Hardware Components of the Voltage Card.

        Args:
            cs_dac (int): CS Line of the Multiplexer Corresponding to the DAC
            cs_adc (int): CS Line of the Multiplexer Corresponding to the ADC
            spi (SpiDev spi): SPI Interface
            muxer (Muxer): Multiplexer for CS Selection 
    """
    def __init__(self,cs_dac,cs_adc,spi,muxer):
        """Init all controllable Hardware Components of the Voltage Card.

        Args:
            cs_dac (int): CS Line of the Multiplexer Corresponding to the DAC
            cs_adc (int): CS Line of the Multiplexer Corresponding to the ADC
            spi (SpiDev spi): SPI Interface
            muxer (Muxer): Multiplexer for CS Selection 
        """
        self.path_voltages=f"voltages_cs_adc_{cs_adc}"
        self.setted_volts=dict(zip([x for x in range(8)],[0 for y in range(8)]))
        np.save(f"{self.path_voltages}_adc.npy",np.zeros(8))
        np.save(f"{self.path_voltages}_set.npy",np.zeros(8))
        self.muxer=muxer
        self.dac=DAC_80508(cs_dac,spi,muxer)
        self.adc=ADS_8166(cs_adc,spi,muxer)
        self.debug=False
        self.spi=spi
        #self.volt_thread = threading.Thread(target=self.update_voltages)
        #self.volt_thread.start()

    def update_voltages(self):
        channels=8
        uncertainty=0.3
        samplesize=10
        
        while True:
            set_volts=np.load(f"{self.path_voltages}_set.npy")
            adc_volts=np.zeros(8)
            for channel in range(channels):
                adc_volt=self.adc.get_voltage(channel,std=0.1,samples=5)
                if adc_volt==0:
                    print(channel)
                    self.muxer.set_cs(0)#
                    time.sleep(0.05)
                    self.muxer.set_cs(1)
                    adc_volt=self.adc.get_voltage(channel,std=0.1,samples=5)
                    if adc_volt==0:
                        print("continue")
                        continue
                if not abs(set_volts[channel]-adc_volt)<=uncertainty:
                    print(f"Before Channel {channel} voltage set {set_volts[channel]} adc volt {adc_volt}")
                    set_voltage=self.dac.get_voltage(channel)
                    adc_volt=self.adc.get_voltage(channel,std=0.01,samples=samplesize)
                    set_voltage+=(set_volts[channel]-adc_volt)
                    if set_voltage>=set_volts[channel]+2:
                        set_voltage=set_volts[channel]+1
                    if set_voltage<0:
                        set_voltage=0
                        if set_volts[channel]==0:
                            adc_volts[channel]=adc_volt
                            continue
                    if set_voltage>=38:
                        set_voltage=40
                        if set_volts[channel]>=38:
                            adc_volts[channel]=adc_volt
                            continue
                    self.dac.set_voltage(channel,set_voltage)
                    time.sleep(0.005)
                    adc_volt=self.adc.get_voltage(channel,std=0.01,samples=samplesize)
                    #print(f"After Channel {channel} voltage set {set_volts[channel]} adc volt {adc_volt}")
                adc_volts[channel]=adc_volt
            np.save(f"{self.path_voltages}_adc.npy",adc_volts)
            #print(adc_volts)
            time.sleep(0.03)

                



    def set_voltage(self,channel,voltage):
        """Sets the Voltage of a given channel to a given voltage

        Args:
            channel (int): Channel (0-7)
            voltage (float): desired Voltage in Volts

        Returns:
            Tuple of floats: The estimated set Voltage of the DAC; The measured Voltage of the ADC
        """
        if voltage>=31:
            voltage=31
        uncertainty=0.1
        if self.debug:
            print(f"Channel {channel} Voltage {voltage}")
        adc_volt_before=self.adc.get_voltage(channel)
        #dac_volt_before=self.dac.get_voltage(channel)
        adc_volt=self.adc.get_voltage(channel)
        set_voltage=voltage
        self.setted_volts[channel]=voltage
        while True:
            set_voltage=self.dac.set_voltage(channel,set_voltage)
            time.sleep(0.001)
            adc_volt=self.adc.get_voltage(channel,std=0.01,samples=10)
            set_voltage+=(voltage-adc_volt)
            if set_voltage<0:
                set_voltage=0
                if voltage==0:
                    break
            if set_voltage>=38:
                set_voltage=40
                if voltage>=38:
                    break
            #dac_volt_before=self.dac.get_voltage(channel)
            #print(adc_volt)
            if abs(voltage-adc_volt)<=uncertainty:
                time.sleep(0.005)
                adc_volt=self.adc.get_voltage(channel,std=0.03,samples=30)
                if abs(voltage-adc_volt)<=uncertainty:
                    print(f"Done {adc_volt}")
                    break
                print(f"close {adc_volt}")


        #set_voltage=self.dac.set_voltage(channel,voltage)
        time.sleep(0.01)
        adc_volt=self.adc.get_voltage(channel)
        return voltage,adc_volt

    def set_voltage_pid(self,channel,voltage):
        """Sets the Voltage of a given channel to a given voltage

        Args:
            channel (int): Channel (0-7)
            voltage (float): desired Voltage in Volts

        Returns:
            Tuple of floats: The estimated set Voltage of the DAC; The measured Voltage of the ADC
        """
        if self.debug:
            print(f"Channel {channel} Voltage {voltage}")
        set_voltage=self.dac.set_voltage(channel,voltage)
        pid = PID(1.2, 0, 0, setpoint=voltage)
        pid.tunings = (3, 10, 0.1)
        pid.output_limits = (0, 40)  
        pid.sample_time = 0.001
        adc_volt=self.adc.get_voltage(channel,std=0.05,samples=10)
        while True:
            # Compute new output from the PID according to the systems current value
            control = pid(adc_volt)

            # Feed the PID output to the system and get its current value
            self.dac.set_voltage(channel,control)
            adc_volt=self.adc.get_voltage(channel,std=5,samples=5)
            print(f"Voltage is {adc_volt} Control was {adc_volt}")
            time.sleep(0.005)
            if abs(adc_volt-voltage)<=0.002:
                time.sleep(0.005)
                adc_volt=self.adc.get_voltage(channel,std=0.005,samples=20)
                if abs(adc_volt-voltage)<=0.005:
                    print(f"Voltage is {adc_volt} voltage wanted: {voltage} break")
                    break
                else:
                    print(f"close {adc_volt}")


        time.sleep(0.01)
        adc_volt=self.adc.get_voltage(channel)
        return set_voltage,adc_volt

    def get_all_voltages_file(self):
        voltages=np.load(f"{self.path_voltages}_adc.npy")
        return voltages

    def set_voltage_file(self,channel,voltage):
        set_volts=np.load(f"{self.path_voltages}_set.npy")
        set_volts[channel]=voltage
        np.save(f"{self.path_voltages}_set.npy",set_volts)
        return voltage,self.get_all_voltages_file()[channel]

    def get_all_voltages(self):
        """Gets all Voltages from ADC

        Returns:
            np.array: All measured Voltages
        """
        voltages=np.zeros(8)
        for channelidx in range(8):
            voltages[channelidx]=self.get_single_voltage(channelidx)
        return voltages

    def get_single_voltage(self,channel):
        self.dac.read(0x01)
        time.sleep(0.005)
        return self.adc.get_voltage(channel,0.03,30)

    def get_single_voltage_dac(self,channel):
        return self.dac.get_voltage(channel),self.setted_volts[channel]

    def set_voltage_(self,channel,voltage):
        """Sets the Voltage of a given channel to a given voltage

        Args:
            channel (int): Channel (0-7)
            voltage (float): desired Voltage in Volts

        Returns:
            Tuple of floats: The estimated set Voltage of the DAC; The measured Voltage of the ADC
        """
        if voltage>=31:
            voltage=31
        if self.debug:
            print(f"Channel {channel} Voltage {voltage}")
        set_voltage=self.dac.set_voltage(channel,voltage)
        time.sleep(0.01)
        adc_volt=self.adc.get_voltage(channel)
        return set_voltage,adc_volt