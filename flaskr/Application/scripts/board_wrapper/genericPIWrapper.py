import logging
try: 
    import sys
except RuntimeError:
    print(' Error importing sys! ')
try:
    import math
except RuntimeError:
    print(' Error importing math! ') 
try:
    import time  
except RuntimeError:
    print(' Error importing time! ')
try:
    import spidev                               # SPI 
except RuntimeError:
    print(' Error importing spidev! ')
try:
    import smbus2 as smbus                      # I2C
except RuntimeError:
    print(' Error importing smbus! ')
try:
    import RPi.GPIO as GPIO                     # GPIO in Rpi 
except RuntimeError:
    print(' Error importing RPi.GPIO! ')
try:
    import os
except RuntimeError:
    print(' Error importing os! ')

# Raspberry Pi3 GPIO Definitions
# PinName   | GPIO  | Comments
TXD0        = 14    # UART interface
RXD0        = 15    # UART interface
GEN0        = 17
GEN1        = 18
GEN2        = 27
GEN3        = 22
GEN4        = 23
GEN5        = 24
GEN6        = 25
CE0_N       = 8     # SPI interface
CE1_N       = 7     # SPI interface
SDA_0       = 2     # I2C interface
SCL_0       = 3     # I2C interface
GCLK        = 4
MOSI        = 10    # SPI interface
MISO        = 9     # SPI interface
SCLK        = 11    # SPI interface

# Additional available GPIOs
#           12, 16, 20, 21, 5

# Shuttle Board Pin Definitions
# PinName           | GPIO      | Comments
Shuttle_MISO        = MISO      # SPI interface
Shuttle_MOSI        = MOSI      # SPI interface
Shuttle_SCK         = SCLK      # SPI interface
Shuttle_CS          = CE0_N     # SPI interface  (Jumper J104)       
Shuttle_IO5_INTA    = GEN6      # Jumper J112)
Shuttle_IO0         = GEN3      # Direct
Shuttle_IO1         = 19        # Jumper 111
Shuttle_IO2         = GCLK      # Direct
Shuttle_IO3         = 12        # Direct
Shuttle_SDA         = SDA_0     # Jumper J504
Shuttle_SCL         = SCL_0     # Jumper J505
Shuttle_IO8         = GEN5      # Direct
Shuttle_INTB_IO6    = GEN1      # Direct
Shuttle_INTC_IO7    = GEN2      # Direct
Shuttle_IO4         = GEN0      # Direct

# AX, AY, AZ, AMUX: no connection
 
class genericAPI():
    debug  = False  
    communication_via_SPI = False    
    interface = ''    
    dummy     = 0
    sensorID  = 0
    i2c_SetSpeed = False
    spi_port = 0                # Selected SPI port in Raspberry pi: 0

    def __init__(self, adapter = 'PTGO', **kwargs):
        """

        :rtype: object
        """
        print(' genericAPiWrapper for RPi is initialized')              
        self.setDebug(True)
#        self.setGPIOclean()
        time.sleep(1)
        self.getGPIOSoftVersion()
        self.setGPIOWarning(False)
        self.getBoardInfo()
        self.set_adapter(adapter)
        print(' ------------------------------------------------------------ ')
        self.spi_16bit = False
        self.data_16bit = False   

    def setDebug(self, enable):
        ''' Enable/disable debugging in this wrapper '''
        print(' Enable debug in wrapper: '+ str(enable))
        self.debug = enable
        pass 

    #def getErrorcode(self):
    #    ''' It gets the sensor error register value '''
    #    temp = self.read(0x02, 1, self.id, self.dummy)        
    #    if self.debug:
    #        print(' getErrorcode: ', temp[0])
    #    return temp[0]
    
    def pinConfig(self, pinNr, direction, outputLevel='LOW'):
        ''' Raspberry Pi GPIO Configuration '''
        if self.debug:
            print(' GPIOpinNr: '+ str(pinNr) + ', direction: ' + str(direction) + ', outputLevel: ' + str(outputLevel))
        GPIO.setmode(GPIO.BCM)        
        if direction == 'INPUT':
            if outputLevel == 'HIGH':
                GPIO.setup(pinNr, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            elif outputLevel == 'LOW':
                GPIO.setup(pinNr, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
            else:
                print(' ERROR: pin configuration is not completed')

        elif direction == 'OUTPUT':
            if outputLevel == 'HIGH':
                GPIO.setup(pinNr, GPIO.OUT, initial=1)
                GPIO.output(pinNr, True)
            elif outputLevel == 'LOW':
                GPIO.setup(pinNr, GPIO.OUT, initial=0)
                GPIO.output(pinNr, False)                 
            else:
                print(' ERROR: pin configuration is not completed')
        else:
                print(' ERROR: pin configuration is not completed')               
        pass
               

    def sensorSPIConfig(self,  cs_pin=0, speedKHz=100, spiMode=0, spi_16bit=True):
        
        cs_pin = 0
        speedHz = speedKHz * 1000

        self.spi = spidev.SpiDev()
        self.spi.open(self.spi_port, 0)         # open spi_port, device (cs_pin)                       
        if spiMode == 0:
            self.spi.mode = 0b00         
        elif spiMode == 3:
            self.spi.mode = 0b11
        else:
            print(' ERROR: spi mode selection is incorrect. SPI mode by defult is selected: mode ', self.spi.mode)
             
        if speedHz == 500000:
            self.spi.max_speed_hz = speedHz    
        elif speedHz == 1000000:
            self.spi.max_speed_hz = speedHz
        elif speedHz == 2000000:
            self.spi.max_speed_hz = speedHz
        elif speedHz == 4000000:
            self.spi.max_speed_hz = speedHz
        elif speedHz == 8000000:
            self.spi.max_speed_hz = speedHz
        elif speedHz == 16000000:
            self.spi.max_speed_hz = speedHz
        elif speedHz == 32000000:
            self.spi.max_speed_hz = speedHz
        else:
            self.spi.max_speed_hz = 100000            
        if self.debug:
            print(' SPI config: ')
            print('csPin: ' + str(cs_pin) +', speedHz: '+ str(self.spi.max_speed_hz) +', spiMode: '+ str(self.spi.mode))
        self.communication_via_SPI = True
        self.interface = 'SPI'        
        #self.read(0x00, 1, self.id, self.dummy)[0]          # Dummy byte read
        #return self.getErrorcode()
        self.spi_16bit = spi_16bit

    def read(self, registerAddress, length = 0, sensorAddress = 0, nbDummyBytes = 0):
        ''' It reads length data from register at registerAddress and returns a list '''         
        if self.debug:
            print('                                                    read command: ' + str(hex(registerAddress)) + ', ' + str(length))
        if length == 0:
            readlength = 1
        else:
            readlength = length
        if (self.communication_via_SPI == True):
            to_send = []
            if self.spi_16bit:
                #registerAddress_MSB = self.get_masked_value(registerAddress,8,8)
                #registerAddress_LSB = self.get_masked_value(registerAddress,0,8)
                registerAddress_MSB, registerAddress_LSB = self.word_to_2bytes(registerAddress)
                to_send.append(registerAddress_MSB | 0x80)
                to_send.append(registerAddress_LSB)
                length_bytes = (readlength + nbDummyBytes)*2
            else:
                if self.data_16bit:
                    readlength = readlength * 2
                if registerAddress!=-1:
                    registerAddress = registerAddress | 0x80
                else:
                    registerAddress=0x00
                to_send = [registerAddress]
                length_bytes = readlength + nbDummyBytes
            
            #for i in range (0, len):
            #   to_send.extend([0])
            to_send.extend([0]*length_bytes)
            print(to_send)
            read_temp = self.spi.xfer2(to_send)
            #print(read_temp)
            if self.spi_16bit:
                #here should be dummy word in stead of dummy bytes, but just keep it as a number
                read_temp_no_dummy = read_temp[(nbDummyBytes*2+2):((nbDummyBytes+readlength)*2+2)]
                result = []
                for i in range(0,len(read_temp_no_dummy),2):
                    result.append(self.two_bytes_to_word(read_temp_no_dummy[i],read_temp_no_dummy[i+1]))
            elif self.data_16bit:
                result = [(read_temp[i+1] << 8| read_temp[i]) for i in range(nbDummyBytes+1,len(read_temp),2)]
            else:
                result = read_temp[(nbDummyBytes+1):(nbDummyBytes+readlength+1)]
            
        
        if length == 0:
            result = result[0]
            
        return result
        
    def write(self, registerAddress, data, sensorAddress = 0):
        ''' It writes 'data' to register at 'registerAddress' '''
        if (self.communication_via_SPI == True):
            to_send = []
            if self.spi_16bit:
                #registerAddress_MSB = self.get_masked_value(registerAddress,8,8)
                #registerAddress_LSB = self.get_masked_value(registerAddress,0,8)
                registerAddress_MSB, registerAddress_LSB = self.word_to_2bytes(registerAddress)
                to_send.append(registerAddress_MSB & 0x7F)
                to_send.append(registerAddress_LSB)
                if type(data) is int:
                    msb, lsb = self.word_to_2bytes(data)
                    to_send.extend([msb, lsb])  #single byte write
                else:
                    for word in data:
                        msb, lsb = self.word_to_2bytes(word)
                        to_send.extend([msb, lsb]) #burst write when data is a list
            elif self.data_16bit:
                to_send.append(registerAddress & 0x7F)
                data_8bit = []    
                if type(data) is list:
                    # SensorAddress is 7 for the Board
                    
                    for word in data:
                        msb, lsb = self.word_to_2bytes(word)
                        data_8bit.extend([lsb, msb]) #burst write when data is a list
                    
                else:
                    msb, lsb = self.word_to_2bytes(data)
                    data_8bit.extend([lsb, msb]) #burst write when data is a list
                to_send.extend(data_8bit)
                #print("write debug")
                #print(data_8bit)
                #print(to_send)
            else:
                to_send.append(registerAddress & 0x7F)
                if type(data) is int:
                    to_send.append(data)  #single byte write
                else:
                    to_send.extend(data) #burst write when data is a list
            if self.debug:
            #    print('                                                    write command: ' + str(hex(registerAddress)) + ', ' + str(hex(data)))
                print(to_send)
            read_temp = self.spi.xfer2(to_send)

        pass     
               
    def getGPIOSoftVersion(self):
        ''' It gets the GPIO module version '''
        GPIO.setmode(GPIO.BCM)
        if self.debug:
            print(' getGPIOSoftVersion: version: ', GPIO.VERSION   )
        pass      

    def setGPIOWarning(self, enable):
        ''' It enables/disables the GPIO warning messages '''
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(enable)
        if self.debug:
                print(' setGPIOWarning:', enable)
        pass
          
    def setGPIOclean(self): 
        ''' It sets a GPIO input/output settings clean '''
        GPIO.cleanup()
        if self.debug:
                print(' setGPIOclean: OK')
        pass
                
    def setPinSwitchState(self, pinNr):
        ''' It toggles the signal level of the output pin number pinNr '''
        if self.debug:
            print(' getPinSwitchState: ' + str(pinNr))
        if GPIO.input(pinNr):
            GPIO.output(pinNr, False)
        else:
            GPIO.output(pinNr, True)
        
        # return self.getPinConfig(pinNr).SwitchState
        return GPIO.input(pinNr)

    def getBoardInfo(self, PiRev = True, RAM = True, Rev = True, Type = True, Proc = True , Manuf = True):
        ''' It gets Rpi information: Pi revision, RAM, Revision, Type, Processor, Manufacturer '''
        if self.debug:            
            if (PiRev | RAM | Rev | Type | Proc | Manuf):
                print(' getBoardInfo: Raspberry Pi '             )
            if PiRev:  
                print('                     Revision: ', GPIO.RPI_INFO['P1_REVISION'])
            if RAM:  
                print('                     RAM: ', GPIO.RPI_INFO['RAM'])
            if Rev:  
                print('                     Revision: ', GPIO.RPI_INFO['REVISION']    )
            if Type:  
                print('                     Type: ', GPIO.RPI_INFO['TYPE'] )
            if Proc:  
                print('                     Processor: ', GPIO.RPI_INFO['PROCESSOR']        )
            if Manuf:  
                print('                     Manufacturer: ', GPIO.RPI_INFO['MANUFACTURER']        )
        output = ''
        Info = ''
        Info1 = ''
        Info2 = ''
        Info3 = ''
        Info4 = ''
        Info5 = ''
        Info6 = ''        
        if PiRev:  
            Info = ' Revision: '+ str(GPIO.RPI_INFO['P1_REVISION'])+str(',')
        if RAM:  
            Info2 = ' RAM: '+ str(GPIO.RPI_INFO['RAM'])+str(',')
            seq = (Info, Info2)
            Info = output.join(seq)             
        if Rev:  
            Info3 = ' Revision: '+str(GPIO.RPI_INFO['REVISION'])+str(',')
            seq = (Info, Info3)
            Info = output.join(seq)             
        if Type:  
            Info4 = ' Type: '+str( GPIO.RPI_INFO['TYPE'])+str(',')
            seq = (Info, Info4)
            Info = output.join(seq)
        if Proc:  
            Info5 = ' Processor: '+str(GPIO.RPI_INFO['PROCESSOR'])+str(',')
            seq = (Info, Info5)
            Info = output.join(seq)                            
        if Manuf:  
            Info6 = ' Manufacturer: ' + str(GPIO.RPI_INFO['MANUFACTURER']) 
            seq = (Info, Info6)
            Info = output.join(seq)  
        return Info

    def set_masked_value(self, reg, bit, width, value):
        '''
        Return the modified temp_register value.
        The signal starts at 'bit' in the register, is 'width' bits long
        'Value' should be assign to this signal
        '''
        clear_mask = ((0x1 << width) - 1) << bit
        set_mask = value << bit
        data = reg & (0xFFFF - clear_mask)
        masked_value = data | set_mask
        return masked_value

    def get_masked_value(self, reg, bit, width):
        '''
        Return the masked and shifted value from the reg.
        The signal starts at 'bit' in the register, is 'width' bits long
        'Value' is the current value of the signal.
        '''
        mask = ((0x1 << width) - 1) << bit
        value = (reg & mask) >> bit
        return value

    def initMUX(self):
        '''
        GPIO 6, 13, 19, 26 is used by the MUX board. Only 16 address is available.
        '''
        
        level = {0: 'LOW', 1: 'HIGH'}
        if self.adapter == 'PTGO':
            mux_bit_0 = 0
            mux_bit_1 = 0
            mux_bit_2 = 0
            mux_bit_3 = 0
            self.pinConfig(self.MUX_0, 'OUTPUT', level[mux_bit_0])
            self.pinConfig(self.MUX_1, 'OUTPUT', level[mux_bit_1])
            self.pinConfig(self.MUX_2, 'OUTPUT', level[mux_bit_2])
            self.pinConfig(self.MUX_3, 'OUTPUT', level[mux_bit_3])
            if self.debug:
                print("Muxer initialised")


    def setMUX(self, address):
        '''
        GPIO 6, 13, 19, 26 is used by the MUX board. Only 16 address is available.
        '''
        if self.adapter == 'PTGO':
            if self.mux_select != address:
                level = {0:False, 1:True}
                if address > 15 or address < 0:
                    print('Error, the multiplexer only suppport address from 0 to 15.')
                else:
                    mux_bit_0 = address & 0b0001
                    mux_bit_1 = (address & 0b0010) >> 1
                    mux_bit_2 = (address & 0b0100) >> 2
                    mux_bit_3 = (address & 0b1000) >> 3
                    GPIO.output(self.MUX_0, level[mux_bit_0])
                    GPIO.output(self.MUX_1, level[mux_bit_1])
                    GPIO.output(self.MUX_2, level[mux_bit_2])
                    GPIO.output(self.MUX_3, level[mux_bit_3])
                    self.mux_select = address
                if self.debug:
                    print("Sensor %d is selected by Multiplexer" % self.mux_select)
                
    def set_adapter(self, adapter):
        if adapter == None and self.adapter != None:
            logging.info("Ingore set_adapter(), adapter was set to %s" % self.adapter)
        elif adapter != None:
            self.adapter = adapter
            if self.adapter == 'PTGO':
            # For MUX board used by PTGO device
                self.MUX_0 = 6  # S0 sensor address
                self.MUX_1 = 13  # S1 sensor address
                self.MUX_2 = 19  # S2 sensor address
                self.MUX_3 = 26  # S3 sensor address
                self.initMUX()
                self.mux_select = 0
                
    def word_to_2bytes(self, word):
        MSB = self.get_masked_value(word,8,8)
        LSB = self.get_masked_value(word,0,8)
        return MSB, LSB
    
    def two_bytes_to_word(self, MSB, LSB):
        return (MSB << 8) | LSB
