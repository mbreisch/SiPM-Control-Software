from RPi import GPIO
from time import sleep

class Muxer:
    """Multiplexer Control for Multiplexers with max 128 Outputlines and GPIO Bit encoding for output Line.
    Initialies Muxer with specified muxlines

    Args:
        muxlines (list of int, optional): The GPIO Pins of the Raspberry which are used to control the Muxer. Defaults to [].
        
    """
    select=0
    def __init__(self,muxlines=[]):
        """Initialies Muxer with specified muxlines

        Args:
            muxlines (list of int, optional): The GPIO Pins of the Raspberry which are used to control the Muxer. Defaults to [].
        """
        GPIO.cleanup()
        self.muxlines=muxlines
        self.soft_cs=17
        self.configure_output(self.soft_cs)
        for line in self.muxlines:
            self.configure_output(line)
        self.line_count=len(self.muxlines)
        self.debug=False
        

    def configure_output(self,pinNr):
        """Configures RPi GPIO as Output and puts it in a LOW State.

        Args:
            pinNr (int): RPI GPIO Number
        """
        GPIO.setmode(GPIO.BCM)    
        GPIO.setup(pinNr, GPIO.OUT, initial=0)
        GPIO.output(pinNr, False)    
    
    def set_cs(self,cs):
        """Sets the Output Line of the Multiplexer to the specified cs.

        Args:
            cs (int): Desired Outputline.
        """
        if cs!=self.select:
            bits=[int(x) for x in f"{cs:08b}"][::-1]
            bits=bits[:self.line_count]
            for idx,bit in enumerate(bits):
                GPIO.output(self.muxlines[idx], bit)
            Muxer.select=cs
            if self.debug:
                print(f"Mux Lines {self.muxlines} values {bits}")
        self.cs_low()

    def cs_high(self):
        GPIO.output(self.soft_cs,1)
    
    def cs_low(self):
        GPIO.output(self.soft_cs,0)