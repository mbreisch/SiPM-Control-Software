import time, sys
import numpy as np

class DS18B20:
    """Used Temperature Sensor at Underside of SiPM Shuttle.
    Initialise Temperature Sensor with 1 Wire Protocol at GPIO4

    Args:
        path (str): Systempath to Temperature Sensor
        idx (int): Index of Sensor on SiPM Array
    """
    def __init__(self,path,idx):
        """Initialise Temperature Sensor with 1 Wire Protocol at GPIO4

        Args:
            path (str): Systempath to Temperature Sensor
            idx (int): Index of Sensor on SiPM Array
        """
        self.idx=idx
        self.path=path
        self.data=[False,False]
        self.get_temperature()
        

    def get_temperature(self):
        """Gets the Temperature
        """
        with open(self.path,"r") as f:
            lines=f.readlines()
        if lines[0].endswith("YES\n"):
            print(lines[1])
            temperaturStr = lines[1].find('t=')
            if temperaturStr!=-1:
                temp_data=float(lines[1][temperaturStr+2:])/1000
                self.data=[time.time(),temp_data]
                print(self.data)
        
        
# Systempfad zum den Sensor, weitere Systempfade könnten über ein Array
# oder weiteren Variablen hier hinzugefügt werden.
#sensor = '/sys/bus/w1/devices/28-02161f5a48ee/w1_slave'
 
