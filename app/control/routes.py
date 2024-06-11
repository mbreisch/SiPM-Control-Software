from flask import Blueprint,render_template, url_for,request,jsonify,redirect,session, json, redirect, current_app
from flask_login import login_required
import subprocess
import sys
import os
from flask import jsonify
import numpy as np
import time,datetime
import shutil
from datetime import datetime
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import requests
from w1thermsensor import W1ThermSensor, Unit

from . import control_bp

sys.path.append(control_bp.static_folder)

@control_bp.route('/',methods=["GET","POST"])
@login_required
def control_home():
    return render_template("control.html",title="Control Interface")

from hw_scripts.Temperature_Sensor import DS18B20
from hw_scripts.voltage_card import Voltage_Card
from hw_scripts.Multiplexer import Muxer

control_bp.paths=["/sys/bus/w1/devices/28-00000c7e5ff0/w1_slave"]
control_bp.pixel=8

control_bp._title="Overall Control"

@control_bp.route("/init_temperature",methods=["POST"])
def init_temperature():
    """Initialises the Temperature Sensors. 
    Looks for all available sensors.
    Called POST at /init_temperature

    Returns:
        json: data contains working sensors
    """
    source_path = "/home/pi/SiPM-Control-Software/temperature_for_plot.log"
    destination_directory = "/home/pi/SiPM-Control-Software/backup_logs/"
    
    if os.path.exists(source_path):
        timestamp = round(time.time() * 1000)
        original_filename = os.path.basename(source_path)
        new_filename = f"{original_filename[:-4]}_{timestamp}.log"
        destination_path = os.path.join(destination_directory, new_filename)
        shutil.copy(source_path, destination_path)
        os.remove(source_path)
    
    control_bp.sensors=[]
    sensors=[0]*control_bp.pixel
    sens=W1ThermSensor.get_available_sensors()
    control_bp.paths=[sensor.id for sensor in sens]
    for temp_idx in range(control_bp.pixel):
        try:
            sensor=DS18B20(f"/sys/bus/w1/devices/28-{control_bp.paths[temp_idx]}/w1_slave",temp_idx)
            control_bp.sensors.append(sensor)
            sensors[temp_idx]=1
        except Exception as e:
            print(f"Got Exception {e} in init Temperature")
    print(control_bp.paths)
    return jsonify(data=sensors,success=True)
    
    
@control_bp.route("/get_temp_values",methods=["POST"])
def ajax_response():
    """Tries to get Data of the initialised Temperature Sensors. 
    Saves the values with their timestamp in a array in Order of their occurence in control_bp.sensors.
    Called POST at /init_temperature
    
    Returns:
        json: data contains list of time of temperature measurement and temperature 
    """
    try:
        times=[-1]*control_bp.pixel
        temps=[-1]*control_bp.pixel
        paths=[0]*control_bp.pixel
        for idx,sensor in enumerate(control_bp.sensors):
            sensor.get_temperature()
            times[sensor.idx]=int(sensor.data[0]*1000)
            temps[sensor.idx]=f"{sensor.data[1]:.2f}"
            try:
                paths[sensor.idx]=sensor.path.split("/")[5]
            except IndexError:
                paths[sensor.idx]="0"
        with open("/home/pi/SiPM-Control-Software/temp.log","a") as templogfile:
            for idx in range(len(times)):
                templogfile.write(f"\n{times[idx]};{temps[idx]};{paths[idx]}")
        with open("/home/pi/SiPM-Control-Software/temperature_for_plot.log","a") as templogfile2:
            if 0.0 not in temps and 0.0 not in times:
                for idx in range(len(times)):
                    templogfile2.write(f"{times[idx]},{temps[idx]};")
                templogfile2.write(f"\n")
        with open("/home/pi/SiPM-Control-Software/temperature_for_plot.log", 'r') as logfile:    
            MakeMonitorPlotForTemperature(logfile)
        return jsonify(data={"times":times,"temps":temps,"paths":paths,"Exception":None},success=True)
    except Exception as e:
        return jsonify(data={"times":[],"temps":[],"paths":[],"Exception":str(e)},success=False)
    

@control_bp.route("/init_dac",methods=["POST"])
def init_dac():
    """Initialises a Voltage Card and Multiplexer. Is called with POST Request at /init_dac

    Returns:
        json: Success Statement
    """
    
    source_path = "/home/pi/SiPM-Control-Software/voltage_for_plot.log"
    destination_directory = "/home/pi/SiPM-Control-Software/backup_logs/"
    
    if os.path.exists(source_path):
        timestamp = int(time.time() * 1000)
        original_filename = os.path.basename(source_path)
        new_filename = f"{original_filename[:-4]}_{timestamp}.log"
        destination_path = os.path.join(destination_directory, new_filename)
        shutil.copy(source_path, destination_path)
        os.remove(source_path)
    
    #requests.post("http://127.0.0.1:5000/app_temp/init_temperature")
    control_bp.temp_index=0
    muxer_lines=[12,13,19,16]
    control_bp.muxer=Muxer(muxer_lines)
    control_bp.dac_cs=0
    control_bp.adc_cs=1
    control_bp.volt_card=Voltage_Card(control_bp.dac_cs,control_bp.adc_cs,control_bp.spi,control_bp.muxer)
    return jsonify(data="Done",success=True)
    
    
    
@control_bp.route("/set_dac_value",methods=["POST"])
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
        set_voltage,adc_volt=control_bp.volt_card.set_voltage(channel,volt)
        return jsonify(data={"voltage":f"{set_voltage:.4f}","adc_voltage":f"{adc_volt:.3f}","Exception":None},success=False)
    except Exception as e:
        print(f"Exception {e} in ajax response")
        return jsonify(data={"voltage":0,"Exception":str(e)},success=False)

@control_bp.route("/get_single_adc_value",methods=["POST"])
def get_single_voltage():
    """Gets the voltage from the specified voltage card. 
    At the moment from the single available voltage card.
    Request must contain desired channel as ["channel"]

    Returns:
        json: json with voltages as array under voltages
    """
    volt_card_idx=float(request.json["voltage_card"])
    channel_idx=int(request.json["channel"])
    voltage=control_bp.volt_card.get_single_voltage(channel_idx)
    timestamp=time.time()
    voltage_dac,voltage_dac_set=control_bp.volt_card.get_single_voltage_dac(channel_idx)
    return jsonify(data={"time":timestamp,"voltage_dac":voltage_dac,"channel":channel_idx,"voltage":voltage,"voltage_dac_set":voltage_dac_set})

@control_bp.route("/get_adc_value",methods=["POST"])
def get_voltage():
    """Gets the voltage from the specified voltage card. 
    At the moment from the single available voltage card.

    Returns:
        json: json with voltages as array under voltages
    """
    volt_card_idx=float(request.json["voltage_card"])
    print(volt_card_idx)
    try:
        voltages=control_bp.volt_card.get_all_voltages()
    except Exception as e:
        return jsonify(data={"Exception":str(e)})
    voltages=[f"{volt:.3f}" for volt in voltages]
    with open("/home/pi/SiPM-Control-Software/voltage.log","a") as voltlogfile:
        timestamp=datetime.now().strftime("%d-%m-%Y--%H:%M:%S")
        for idx,voltage in enumerate(voltages):
            voltlogfile.write(f"\n{timestamp};{idx};{voltage}")
            
    with open("/home/pi/SiPM-Control-Software/voltage_for_plot.log","a") as voltagelogfile2:
        timestamp = round(time.time() * 1000)
        for idx,voltage in enumerate(voltages):
            voltagelogfile2.write(f"{timestamp},{voltage};")
        voltagelogfile2.write(f"\n")
    with open("/home/pi/SiPM-Control-Software/voltage_for_plot.log", 'r') as logfile:    
        MakeMonitorPlotForBias(logfile) 
             
    if control_bp.temp_index%11==0:
        #requests.post("http://127.0.0.1:5000/app_temp/get_temp_values")
        control_bp.temp_index-=10
    control_bp.temp_index+=1
    return jsonify(data={"voltages":voltages,"Exception":None})

@control_bp.route("/check_plot_status", methods=["GET"])
def check_plot_status():
    plot_type = request.args.get("plot_type")  # 'voltage' or 'temperature'
    plot_filename = request.args.get("filename")  # Filename of the plot to check
    
    plot_path = f"/home/pi/SiPM-Control-Software/flaskr/Application/Apps/Control/static/{plot_filename}.png"
    if os.path.exists(plot_path):
        return jsonify({"status": "ready", "filename": plot_filename})
    else:
        return jsonify({"status": "not ready"})

def MakeMonitorPlotForTemperature(logfile):
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
                    
                    if timestamp==-1 or value==-1:
                        continue
                    
                    # Add to the current line's list
                    timestamps[enum].append(timestamp)
                    values[enum].append(value)
                  
    last_1000_timestamps = [sublist[-1000:] for sublist in timestamps]
    last_1000_values = [sublist[-1000:] for sublist in values]
    
    #print(last_1000_timestamps)
    
    # Plot timestamp vs value for each entry
    fig = plt.figure(0 ,figsize=(1000/100,600/100), dpi=100)
    for channel in range(0,8):
        plt.plot(last_1000_timestamps[channel], last_1000_values[channel], marker='', linestyle='-', markersize=3, label=f"CH-{channel}")

    ax = plt.gca()  # Get the current axis
    ax.xaxis.set_major_locator(ticker.MaxNLocator(5))  # Max of 5 major ticks
    ax.xaxis.set_minor_locator(ticker.NullLocator())  # No minor ticks

    # Add labels and title
    plt.xlabel('Timestamp')
    plt.grid()
    plt.ylabel('Temperature in °C')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.title(f'Timestamp vs Temperature')
    plt.savefig(f'/home/pi/SiPM-Control-Software/flaskr/Application/Apps/Control/static/MonitoringTemperature.png')
    plt.close()
    
def MakeMonitorPlotForBias(logfile):
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
                    
                    if timestamp==-1 or value==-1:
                        continue
                    
                    # Add to the current line's list
                    timestamps[enum].append(timestamp)
                    values[enum].append(value)
                  
    last_1000_timestamps = [sublist[-1000:] for sublist in timestamps]
    last_1000_values = [sublist[-1000:] for sublist in values]
    
    #print(last_1000_timestamps)
    
    # Plot timestamp vs value for each entry
    fig = plt.figure(1 ,figsize=(1000/100,600/100), dpi=100)
    for channel in range(0,8):
        plt.plot(last_1000_timestamps[channel], last_1000_values[channel], marker='', linestyle='-', markersize=3, label=f"CH-{channel}")

    ax = plt.gca()  # Get the current axis
    ax.xaxis.set_major_locator(ticker.MaxNLocator(5))  # Max of 5 major ticks
    ax.xaxis.set_minor_locator(ticker.NullLocator())  # No minor ticks

    # Add labels and title
    plt.xlabel('Timestamp')
    plt.grid()
    plt.ylabel('Bias Voltage in V')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.title(f'Timestamp vs Bias Voltage')
    plt.savefig(f'/home/pi/SiPM-Control-Software/flaskr/Application/Apps/Control/static/MonitoringVoltage.png')
    plt.close()
