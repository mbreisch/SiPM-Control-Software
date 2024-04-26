from flask import Blueprint,render_template, url_for,request,jsonify,redirect,session, json, redirect, current_app
import subprocess
import sys
import os
import numpy as np
import time,datetime
from datetime import datetime
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import requests
from w1thermsensor import W1ThermSensor, Unit

app_control=Blueprint("app_control",__name__,static_folder="static",template_folder="templates")
sys.path.append(app_control.static_folder)
from Temperature_Sensor import DS18B20

from DAC.Hardware_Control.voltage_card import Voltage_Card
from DAC.Hardware_Control.Multiplexer import Muxer

app_control._title="Control"
app_control.paths=["/sys/bus/w1/devices/28-00000c7e5ff0/w1_slave"]
app_control.pixel=8

app_control._title="Overall Control"

@app_control.route("/",methods=["GET","POST"])
@app_control.route("/home",methods=["GET","POST"])
def index():
    """Renders Home Page for Temperature APP. 
    Shows all Temperature Sensors on a 8x8 Grid. 
    Sensors not sorted. 
    Called GET/POST at / and /home

    Returns:
        rendered html: The Home Page for the Temperature APP
    """
    return render_template("control.html",title="Control Interface", bg_img_path=url_for('app_control.static',filename="background_dk.jpeg", url_call="/get_json"))

@app_control.route("/init_temperature",methods=["POST"])
def init_temperature():
    """Initialises the Temperature Sensors. 
    Looks for all available sensors.
    Called POST at /init_temperature

    Returns:
        json: data contains working sensors
    """
    app_control.sensors=[]
    sensors=[0]*app_control.pixel
    sens=W1ThermSensor.get_available_sensors()
    app_control.paths=[sensor.id for sensor in sens]
    for temp_idx in range(app_control.pixel):
        try:
            sensor=DS18B20(f"/sys/bus/w1/devices/28-{app_control.paths[temp_idx]}/w1_slave",temp_idx)
            app_control.sensors.append(sensor)
            sensors[temp_idx]=1
        except Exception as e:
            print(f"Got Exception {e} in init Temperature")
    print(app_control.paths)
    return jsonify(data=sensors,success=True)
    
    
    
@app_control.route("/get_temp_values",methods=["POST"])
def ajax_response():
    """Tries to get Data of the initialised Temperature Sensors. 
    Saves the values with their timestamp in a array in Order of their occurence in app_control.sensors.
    Called POST at /init_temperature
    
    Returns:
        json: data contains list of time of temperature measurement and temperature 
    """
    try:
        times=[0]*app_control.pixel
        temps=[0]*app_control.pixel
        paths=[0]*app_control.pixel
        for idx,sensor in enumerate(app_control.sensors):
            sensor.get_temperature()
            times[sensor.idx]=round(time.time() * 1000)#sensor.data[0]
            temps[sensor.idx]=f"{sensor.data[1]:.2f}"
            try:
                paths[sensor.idx]=sensor.path.split("/")[5]
            except IndexError:
                paths[sensor.idx]="0"
        with open("/home/pi/SiPM-Control-Software/temp.log","a") as templogfile:
            for idx in range(len(times)):
                templogfile.write(f"\n{times[idx]};{temps[idx]};{paths[idx]}")
        with open("/home/pi/SiPM-Control-Software/temperature_for_plot.log","a") as templogfile2:
            for idx in range(len(times)):
                templogfile2.write(f"{times[idx]},{temps[idx]};")
            templogfile2.write(f"\n")
        with open("/home/pi/SiPM-Control-Software/temperature_for_plot.log", 'r') as logfile:    
            MakeMonitorPlot(logfile)
        return jsonify(data={"times":times,"temps":temps,"paths":paths},success=True)
    except Exception as e:
        return jsonify(data={"times":[],"temps":[],"paths":[]},success=False)
    

@app_control.route("/init_dac",methods=["POST"])
def init_dac():
    """Initialises a Voltage Card and Multiplexer. Is called with POST Request at /init_dac

    Returns:
        json: Success Statement
    """
    #requests.post("http://127.0.0.1:5000/app_temp/init_temperature")
    app_control.temp_index=0
    muxer_lines=[12,13,19,16]
    app_control.muxer=Muxer(muxer_lines)
    app_control.dac_cs=0
    app_control.adc_cs=1
    app_control.volt_card=Voltage_Card(app_control.dac_cs,app_control.adc_cs,app_control.spi,app_control.muxer)
    return jsonify(data="Done",success=True)
    
    
    
@app_control.route("/set_dac_value",methods=["POST"])
def set_voltage():
    """Sets the Voltage.
    Called by POST of /set_dac_value. 
    Request must contain desired voltage as ["voltage"] and channel as ["channel"]

    Returns:
        json: data contains estimated Voltage of set_voltage of DAC and ADC measured Voltage. In case of Exception 0 for Voltage and Exception str
    """
    print(request.json)
    volt=float(request.json["voltage"])
    channel=request.json["channel"]

    if volt >=30:
        volt = 30
    if volt < 0:
        volt = 0

    try:
        set_voltage,adc_volt=app_control.volt_card.set_voltage(channel,volt)
        return jsonify(data={"voltage":f"{set_voltage:.4f}","adc_voltage":f"{adc_volt:.3f}"},success=False)
    except Exception as e:
        print(f"Exception {e} in ajax response")
        return jsonify(data={"voltage":0,"Exception":str(e)},success=False)

@app_control.route("/get_single_adc_value",methods=["POST"])
def get_single_voltage():
    """Gets the voltage from the specified voltage card. 
    At the moment from the single available voltage card.
    Request must contain desired channel as ["channel"]

    Returns:
        json: json with voltages as array under voltages
    """
    volt_card_idx=float(request.json["voltage_card"])
    channel_idx=int(request.json["channel"])
    voltage=app_control.volt_card.get_single_voltage(channel_idx)
    timestamp=time.time()
    voltage_dac,voltage_dac_set=app_control.volt_card.get_single_voltage_dac(channel_idx)
    return jsonify(data={"time":timestamp,"voltage_dac":voltage_dac,"channel":channel_idx,"voltage":voltage,"voltage_dac_set":voltage_dac_set})

@app_control.route("/get_adc_value",methods=["POST"])
def get_voltage():
    """Gets the voltage from the specified voltage card. 
    At the moment from the single available voltage card.

    Returns:
        json: json with voltages as array under voltages
    """
    volt_card_idx=float(request.json["voltage_card"])
    print(volt_card_idx)
    try:
        voltages=app_control.volt_card.get_all_voltages()
    except Exception as e:
        return jsonify(data={"Exception":str(e)})
    voltages=[f"{volt:.3f}" for volt in voltages]
    with open("/home/pi/SiPM-Control-Software/voltage.log","a") as voltlogfile:
        timestamp=datetime.datetime.now().strftime("%d-%m-%Y--%H:%M:%S")
        for idx,voltage in enumerate(voltages):
            voltlogfile.write(f"\n{timestamp};{idx};{voltage}")
    if app_control.temp_index%11==0:
        #requests.post("http://127.0.0.1:5000/app_temp/get_temp_values")
        app_control.temp_index-=10
    app_control.temp_index+=1
    return jsonify(data={"voltages":voltages})

# @app_control.route("/set_all_0",methods=["POST"])
# def set_0():
#     """Sets the Voltage to 0 on all channels.
#     Called by POST of /set_dac_value. 
#     Request must contain desired voltage as ["voltage"] and channel as ["channel"]

#     Returns:
#         json: data contains estimated Voltage of set_voltage of DAC and ADC measured Voltage. In case of Exception 0 for Voltage and Exception str
#     """
#     print(request.json)
#     volt=float(request.json["voltage"])
#     channel=request.json["channel"]

#     if volt >=30:
#         volt = 30
#     if volt < 0:
#         volt = 0

#     try:
#         for ch in range(0,8):
#             set_voltage,adc_volt=app_control.volt_card.set_voltage(ch,0)
#         return jsonify(data={"voltage":f"{set_voltage:.4f}","adc_voltage":f"{adc_volt:.3f}"},success=False)
#     except Exception as e:
#         print(f"Exception {e} in ajax response")
#         return jsonify(data={"voltage":0,"Exception":str(e)},success=False)


def MakeMonitorPlot(logfile):
    # Read each line from the provided file object
    timestamps = [[],[],[],[],[],[],[],[]]
    values = [[],[],[],[],[],[],[],[]]
    for line in logfile:
        # Strip any leading/trailing whitespace or newlines
        line = line.strip()
        
        # Split the line into entries by the semicolon
        entries = line.split(";") #["ts1,v1","ts2,v2",...]
        
        # Initialize lists to store individual line's timestamps and values

        
        # Process each entry
        for enum,entry in enumerate(entries):
            if entry:  # Check if entry is non-empty
                # Split the entry into timestamp and value by the comma
                ts_val = entry.split(",")
                if len(ts_val) == 2:
                    # Convert the timestamp to integer and the value to float
                    timestamp = int(ts_val[0])
                    value = float(ts_val[1])
                    
                    # Add to the current line's list
                    timestamps[enum].append(timestamp)
                    values[enum].append(value)
                  
    last_1000_timestamps = [sublist[-1000:] for sublist in timestamps]
    last_1000_values = [sublist[-1000:] for sublist in values]
    
    #print(last_1000_timestamps)
    
    # Plot timestamp vs value for each entry
    fig = plt.figure(figsize=(1000/100,600/100), dpi=100)
    for channel in range(0,8):
        datetimes = [datetime.fromtimestamp(ts / 1000) for ts in last_1000_timestamps[channel]]
        time_labels = [dt.strftime('%H:%M:%S.%.3f') for dt in datetimes]
        plt.plot(time_labels, last_1000_values[channel], marker='o', linestyle='-', markersize=3, label=f"CH-{channel}")

    ax = plt.gca()  # Get the current axis
    ax.xaxis.set_major_locator(ticker.MaxNLocator(5))  # Max of 5 major ticks
    ax.xaxis.set_minor_locator(ticker.NullLocator())  # No minor ticks

    # Add labels and title
    plt.xlabel('Timestamp')
    plt.ylabel('Temperature in °C')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.title('Timestamp vs Temperature')
    plt.savefig('/home/pi/SiPM-Control-Software/flaskr/Application/Apps/Control/static/MonitoringTemperature.png')
    plt.close()