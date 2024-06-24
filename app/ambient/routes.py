from flask import Blueprint,render_template, url_for,request,jsonify,redirect,session, json, redirect, current_app
from flask_login import login_required
import subprocess
import sys
import os
import spidev
import numpy as np
import time,datetime
import shutil
from datetime import datetime
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt

from . import ambient_bp

sys.path.append(ambient_bp.static_folder)

@ambient_bp.route('/',methods=["GET","POST"])
@ambient_bp.route("/home",methods=["GET","POST"])
@login_required
def ambient_home():
    return render_template("ambient.html",title="Ambient Monitor")

ambient_bp._title="Ambiemt Monitoring"



plt_settings = {"cooler" : 
                    {"ylimit_cax1_min": 0, "ylimit_cax1_max":50, "ylimit_cax2_min":0, "ylimit_cax2_max":100, "camount": 100},
                "outside" : 
                    {"ylimit_oax1_min": 0, "ylimit_oax1_max":50, "ylimit_oax2_min":0, "ylimit_oax2_max":100, "oamount": 100},
                "darkbox" : 
                    {"ylimit_dax1_min": 0, "ylimit_dax1_max":50, "ylimit_dax2_min":0, "ylimit_dax2_max":100, "damount": 100}
                }

@ambient_bp.route("/update_cooler", methods=["POST"])
def update_cooler():
    if not os.path.exists(f'{ambient_bp.static_folder}/cooler.txt'):
        with open(f'{ambient_bp.static_folder}/cooler.txt', 'w') as file:
            pass 
    with open(f'{ambient_bp.static_folder}/cooler.txt', 'r') as logfile:
        MakeMonitorPlotCooler("cooler", logfile)
        
    while True:
        try:
            # Attempt to open and read the file to ensure it is fully written
            with open(f'{ambient_bp.static_folder}/Ambient_cooler.png', 'rb') as f:
                f.read()
            break  # If successful, break out of the loop 
        except Exception as e:
            print(f"Error reading file: {e}")
            time.sleep(0.1)
    
    return jsonify(success=True)

@ambient_bp.route("/update_darkbox", methods=["POST"])
def update_darkbox():
    if not os.path.exists(f'{ambient_bp.static_folder}/darkbox.txt'):
        with open(f'{ambient_bp.static_folder}/darkbox.txt', 'w') as file:
            pass 
    with open(f'{ambient_bp.static_folder}/darkbox.txt', 'r') as logfile:
        MakeMonitorPlotDarkbox("darkbox", logfile)
        
    while True:
        try:
            # Attempt to open and read the file to ensure it is fully written
            with open(f'{ambient_bp.static_folder}/Ambient_darkbox.png', 'rb') as f:
                f.read()
            break  # If successful, break out of the loop 
        except Exception as e:
            print(f"Error reading file: {e}")
            time.sleep(0.1)    
        
    return jsonify(success=True)

@ambient_bp.route("/update_outside", methods=["POST"])
def update_outside():
    if not os.path.exists(f'{ambient_bp.static_folder}/outside.txt'):
        with open(f'{ambient_bp.static_folder}/outside.txt', 'w') as file:
            pass 
    with open(f'{ambient_bp.static_folder}/outside.txt', 'r') as logfile:
        MakeMonitorPlotOutside("outside", logfile)
        
    while True:
        try:
            # Attempt to open and read the file to ensure it is fully written
            with open(f'{ambient_bp.static_folder}/Ambient_outside.png', 'rb') as f:
                f.read()
            break  # If successful, break out of the loop 
        except Exception as e:
            print(f"Error reading file: {e}")
            time.sleep(0.1)      
        
    return jsonify(success=True)

@ambient_bp.route("/set_plot_settings", methods=["POST"])
def set_plot_settings():
    global plt_settings
    
    name=request.json["name"]
    subname=request.json["subname"]
    id=request.json["id"]
    if id == -1:
        plt_settings[name][subname] = None
    else:
        value=float(request.json["value"])
        plt_settings[name][subname] = value

    return jsonify(success=True)
    
def MakeMonitorPlotCooler(name,logfile):
    global plt_settings
    # Read each line from the provided file object
    timestamps = []
    temperatures = []
    humidities = []
    for line in logfile:
        # Strip any leading/trailing whitespace or newlines
        line = line.strip()
        
        # Split the line into entries by the semicolon
        timestamp,name,temp_hum = line.split(":") #["ts1,v1","ts2,v2",...]
        temperature, humidity = temp_hum.strip("\n").split(";")
        timestamps.append(float(timestamp))
        temperatures.append(float(temperature))
        humidities.append(float(humidity))
        
    if plt_settings["cooler"]["camount"] > len(timestamps) or plt_settings["cooler"]["camount"] == -1:
        plt_settings["cooler"]["camount"] = len(timestamps)
                  
    last_100_timestamps = timestamps[-int(plt_settings["cooler"]["camount"]):]
    last_100_temperatures = temperatures[-int(plt_settings["cooler"]["camount"]):]
    last_100_humidities = humidities[-int(plt_settings["cooler"]["camount"]):]
    
    # Plot timestamp vs value for each entry
    fig, ax1 = plt.subplots(figsize=(600/100,400/100), dpi=100)
    ax1.plot(last_100_timestamps, last_100_temperatures, color='r', marker='', linestyle='-', markersize=3, label=f"Temperature")
    ax1.set_xlabel('UNIX Timestamp in ms')
    ax1.set_ylim(plt_settings["cooler"]["ylimit_cax1_min"], plt_settings["cooler"]["ylimit_cax1_max"])
    ax1.set_ylabel('Temperature in °C', color='r', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='r', labelsize=10)
        
    ax2 = ax1.twinx()
    ax2.plot(last_100_timestamps, last_100_humidities, color='b', marker='', linestyle='-', markersize=3, label=f"Humidity")
    ax2.set_ylim(plt_settings["cooler"]["ylimit_cax2_min"], plt_settings["cooler"]["ylimit_cax2_max"])
    ax2.set_ylabel('Humidity in %', color='b', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='b', labelsize=10)

    # Combine all legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    #ax1.legend(lines1 + lines2 , labels1 + labels2, loc='best', fontsize=16)

    ax1.grid()
    plt.title(f'Ambient {name}')
    plt.savefig(f'{ambient_bp.static_folder}/Ambient_{name}.png')
    time.sleep(2)   
    plt.close()
    
def MakeMonitorPlotDarkbox(name,logfile):
    global plt_settings
    # Read each line from the provided file object
    timestamps = []
    temperatures = []
    humidities = []
    for line in logfile:
        # Strip any leading/trailing whitespace or newlines
        line = line.strip()
        
        # Split the line into entries by the semicolon
        timestamp,name,temp_hum = line.split(":") #["ts1,v1","ts2,v2",...]
        temperature, humidity = temp_hum.strip("\n").split(";")
        timestamps.append(float(timestamp))
        temperatures.append(float(temperature))
        humidities.append(float(humidity))
        
    if plt_settings["darkbox"]["damount"] > len(timestamps) or plt_settings["darkbox"]["damount"] == -1:
        plt_settings["darkbox"]["damount"] = len(timestamps)
                  
    last_100_timestamps = timestamps[-int(plt_settings["darkbox"]["damount"]):]
    last_100_temperatures = temperatures[-int(plt_settings["darkbox"]["damount"]):]
    last_100_humidities = humidities[-int(plt_settings["darkbox"]["damount"]):]
    
    # Plot timestamp vs value for each entry
    fig, ax1 = plt.subplots(figsize=(600/100,400/100), dpi=100)
    ax1.plot(last_100_timestamps, last_100_temperatures, color='r', marker='', linestyle='-', markersize=3, label=f"Temperature")
    ax1.set_xlabel('UNIX Timestamp in ms')
    ax1.set_ylim(plt_settings["darkbox"]["ylimit_dax1_min"], plt_settings["darkbox"]["ylimit_dax1_max"])
    ax1.set_ylabel('Temperature in °C', color='r', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='r', labelsize=10)
        
    ax2 = ax1.twinx()
    ax2.plot(last_100_timestamps, last_100_humidities, color='b', marker='', linestyle='-', markersize=3, label=f"Humidity")
    ax2.set_ylim(plt_settings["darkbox"]["ylimit_dax2_min"], plt_settings["darkbox"]["ylimit_dax2_max"])
    ax2.set_ylabel('Humidity in %', color='b', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='b', labelsize=10)

    # Combine all legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    #ax1.legend(lines1 + lines2 , labels1 + labels2, loc='best', fontsize=16)

    ax1.grid()
    plt.title(f'Ambient {name}')
    plt.savefig(f'{ambient_bp.static_folder}/Ambient_{name}.png')
    time.sleep(2)  
    plt.close()
    
def MakeMonitorPlotOutside(name,logfile):
    global plt_settings
    # Read each line from the provided file object
    timestamps = []
    temperatures = []
    humidities = []
    for line in logfile:
        # Strip any leading/trailing whitespace or newlines
        line = line.strip()
        
        # Split the line into entries by the semicolon
        timestamp,name,temp_hum = line.split(":") #["ts1,v1","ts2,v2",...]
        temperature, humidity = temp_hum.strip("\n").split(";")
        timestamps.append(float(timestamp))
        temperatures.append(float(temperature))
        humidities.append(float(humidity))
        
    if plt_settings["outside"]["oamount"] > len(timestamps) or plt_settings["outside"]["oamount"] == -1:
        plt_settings["outside"]["oamount"] = len(timestamps)
                  
    last_100_timestamps = timestamps[-int(plt_settings["outside"]["oamount"]):]
    last_100_temperatures = temperatures[-int(plt_settings["outside"]["oamount"]):]
    last_100_humidities = humidities[-int(plt_settings["outside"]["oamount"]):]
    
    # Plot timestamp vs value for each entry
    fig, ax1 = plt.subplots(figsize=(600/100,400/100), dpi=100)
    ax1.plot(last_100_timestamps, last_100_temperatures, color='r', marker='', linestyle='-', markersize=3, label=f"Temperature")
    ax1.set_xlabel('UNIX Timestamp in ms')
    ax1.set_ylim(plt_settings["outside"]["ylimit_oax1_min"], plt_settings["outside"]["ylimit_oax1_max"])
    ax1.set_ylabel('Temperature in °C', color='r', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='r', labelsize=10)
        
    ax2 = ax1.twinx()
    ax2.plot(last_100_timestamps, last_100_humidities, color='b', marker='', linestyle='-', markersize=3, label=f"Humidity")
    ax2.set_ylim(plt_settings["outside"]["ylimit_oax2_min"], plt_settings["outside"]["ylimit_oax2_max"])
    ax2.set_ylabel('Humidity in %', color='b', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='b', labelsize=10)

    ax1.grid()
    plt.title(f'Ambient {name}')
    plt.savefig(f'{ambient_bp.static_folder}/Ambient_{name}.png')
    time.sleep(2)  
    plt.close()