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

@ambient_bp.route("/update_cooler", methods=["POST"])
def update_cooler():
    if not os.path.exists(f'{ambient_bp.static_folder}/cooler.txt'):
        with open(f'{ambient_bp.static_folder}/cooler.txt', 'w') as file:
            pass 
    with open(f'{ambient_bp.static_folder}/cooler.txt', 'r') as logfile:
        MakeMonitorPlotCooler("cooler", logfile)
    return jsonify(success=True)

@ambient_bp.route("/update_darkbox", methods=["POST"])
def update_darkbox():
    if not os.path.exists(f'{ambient_bp.static_folder}/darkbox.txt'):
        with open(f'{ambient_bp.static_folder}/darkbox.txt', 'w') as file:
            pass 
    with open(f'{ambient_bp.static_folder}/darkbox.txt', 'r') as logfile:
        MakeMonitorPlotDarkbox("darkbox", logfile)
    return jsonify(success=True)

@ambient_bp.route("/update_outside", methods=["POST"])
def update_outside():
    if not os.path.exists(f'{ambient_bp.static_folder}/outside.txt'):
        with open(f'{ambient_bp.static_folder}/outside.txt', 'w') as file:
            pass 
    with open(f'{ambient_bp.static_folder}/outside.txt', 'r') as logfile:
        MakeMonitorPlotOutside("outside", logfile)
    return jsonify(success=True)
    
def MakeMonitorPlotCooler(name,logfile):
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
        
                  
    last_100_timestamps = timestamps[-100:]
    last_100_temperatures = temperatures[-100:]
    last_100_humidities = humidities[-100:]
    
    # Plot timestamp vs value for each entry
    fig, ax1 = plt.subplots(figsize=(1000/100,600/100), dpi=100)
    ax1.plot(last_100_timestamps, last_100_temperatures, color='k', marker='', linestyle='-', markersize=3, label=f"Temperature")
    ax1.set_xlabel('UNIX Timestamp in ms')
    ax1.set_ylabel('Temperature in °C', color='k', fontsize=16)
    ax1.tick_params(axis='y', labelcolor='k', labelsize=14)
        
    ax2 = ax1.twinx()
    ax2.plot(last_100_timestamps, last_100_humidities, color='b', marker='', linestyle='-', markersize=3, label=f"Humidity")
    ax2.set_ylabel('Humidity in %', color='b', fontsize=16)
    ax2.tick_params(axis='y', labelcolor='b', labelsize=14)

    # Combine all legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2 , labels1 + labels2, loc='best', fontsize=16)

    ax1.grid()
    plt.title(f'Ambient {name}')
    plt.savefig(f'{ambient_bp.static_folder}/Ambient_{name}.png')
    plt.close()
    
def MakeMonitorPlotDarkbox(name,logfile):
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
        
                  
    last_100_timestamps = timestamps[-100:]
    last_100_temperatures = temperatures[-100:]
    last_100_humidities = humidities[-100:]
    
    # Plot timestamp vs value for each entry
    fig, ax1 = plt.subplots(figsize=(1000/100,600/100), dpi=100)
    ax1.plot(last_100_timestamps, last_100_temperatures, marker='', linestyle='-', markersize=3, label=f"Temperature")
    ax1.set_xlabel('UNIX Timestamp in ms')
    ax1.set_ylabel('Temperature in °C', color='k', fontsize=16)
    ax1.tick_params(axis='y', labelcolor='k', labelsize=14)
        
    ax2 = ax1.twinx()
    ax2.plot(last_100_timestamps, last_100_humidities, marker='', linestyle='-', markersize=3, label=f"Humidity")
    ax2.set_ylabel('Humidity in %', color='b', fontsize=16)
    ax2.tick_params(axis='y', labelcolor='b', labelsize=14)

    # Combine all legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2 , labels1 + labels2, loc='best', fontsize=16)

    ax1.grid()
    plt.title(f'Ambient {name}')
    plt.savefig(f'{ambient_bp.static_folder}/Ambient_{name}.png')
    plt.close()
    
def MakeMonitorPlotOutside(name,logfile):
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
        
                  
    last_100_timestamps = timestamps[-100:]
    last_100_temperatures = temperatures[-100:]
    last_100_humidities = humidities[-100:]
    
    # Plot timestamp vs value for each entry
    fig, ax1 = plt.subplots(figsize=(1000/100,600/100), dpi=100)
    ax1.plot(last_100_timestamps, last_100_temperatures, marker='', linestyle='-', markersize=3, label=f"Temperature")
    ax1.set_xlabel('UNIX Timestamp in ms')
    ax1.set_ylabel('Temperature in °C', color='k', fontsize=16)
    ax1.tick_params(axis='y', labelcolor='k', labelsize=14)
        
    ax2 = ax1.twinx()
    ax2.plot(last_100_timestamps, last_100_humidities, marker='', linestyle='-', markersize=3, label=f"Humidity")
    ax2.set_ylabel('Humidity in %', color='b', fontsize=16)
    ax2.tick_params(axis='y', labelcolor='b', labelsize=14)

    # Combine all legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2 , labels1 + labels2, loc='best', fontsize=16)

    ax1.grid()
    plt.title(f'Ambient {name}')
    plt.savefig(f'{ambient_bp.static_folder}/Ambient_{name}.png')
    plt.close()