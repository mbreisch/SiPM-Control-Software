from flask import Blueprint,render_template, url_for,request,jsonify,redirect,session, json, redirect, current_app
import subprocess
import sys
import os
import numpy as np
import time,datetime
import requests


app_dac=Blueprint("app_dac",__name__,static_folder="static",template_folder="templates")
#my_loader=jinja2.ChoiceLoader([terminal.jinja_loader,jinja2.FileSystemLoader
sys.path.append(app_dac.static_folder)

from DAC.Hardware_Control.voltage_card import Voltage_Card
from DAC.Hardware_Control.Multiplexer import Muxer

app_dac._title="Voltage Control"

def GetSettingsFromTxt(channel):
    with open("./Settings.txt", "r") as open_file:
        for line in open_file.readlines(): 
            [key,value] = line.split(",")
            if int(key)==channel:
                return float(value)
 
@app_dac.route("/",methods=["GET","POST"])
@app_dac.route("/home",methods=["GET","POST"])
def index():
    """Renders the Landing Page for the Voltage Control APP. Is called with POST/GET Request at / and /home

    Returns:
        Rendered html: The Html Site to be shown
    """
    return render_template("dac.html",title="Voltage Control", bg_img_path=url_for('app_dac.static',filename="background_dk.jpeg", url_call="/get_json"))

@app_dac.route("/init_dac",methods=["POST"])
def init_dac():
    """Initialises a Voltage Card and Multiplexer. Is called with POST Request at /init_dac

    Returns:
        json: Success Statement
    """
    requests.post("http://127.0.0.1:5000/app_temp/init_temperature")
    app_dac.temp_index=0
    muxer_lines=[12,13,19,16]
    app_dac.muxer=Muxer(muxer_lines)
    app_dac.dac_cs=0
    app_dac.adc_cs=1
    app_dac.volt_card=Voltage_Card(app_dac.dac_cs,app_dac.adc_cs,app_dac.spi,app_dac.muxer)
    return jsonify(data="Done",success=True)
    
    
    
@app_dac.route("/set_dac_value",methods=["POST"])
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

    if volt <= 1.0:
        volt = 0.0
    else:
        volt = GetSettingsFromTxt(channel)

    try:
        set_voltage,adc_volt=app_dac.volt_card.set_voltage(channel,volt)
        return jsonify(data={"voltage":f"{set_voltage:.4f}","adc_voltage":f"{adc_volt:.3f}"},success=False)
    except Exception as e:
        print(f"Exception {e} in ajax response")
        return jsonify(data={"voltage":0,"Exception":str(e)},success=False)

@app_dac.route("/get_single_adc_value",methods=["POST"])
def get_single_voltage():
    """Gets the voltage from the specified voltage card. 
    At the moment from the single available voltage card.
    Request must contain desired channel as ["channel"]

    Returns:
        json: json with voltages as array under voltages
    """
    volt_card_idx=float(request.json["voltage_card"])
    channel_idx=int(request.json["channel"])
    voltage=app_dac.volt_card.get_single_voltage(channel_idx)
    timestamp=time.time()
    voltage_dac,voltage_dac_set=app_dac.volt_card.get_single_voltage_dac(channel_idx)
    return jsonify(data={"time":timestamp,"voltage_dac":voltage_dac,"channel":channel_idx,"voltage":voltage,"voltage_dac_set":voltage_dac_set})

@app_dac.route("/get_adc_value",methods=["POST"])
def get_voltage():
    """Gets the voltage from the specified voltage card. 
    At the moment from the single available voltage card.

    Returns:
        json: json with voltages as array under voltages
    """
    volt_card_idx=float(request.json["voltage_card"])
    print(volt_card_idx)
    try:
        voltages=app_dac.volt_card.get_all_voltages()
    except Exception as e:
        return jsonify(data={"Exception":str(e)})
    voltages=[f"{volt:.3f}" for volt in voltages]
    with open("/home/pi/Desktop/sipm_ctl/voltage.log","a") as voltlogfile:
        timestamp=datetime.datetime.now().strftime("%d-%m-%Y--%H:%M:%S")
        for idx,voltage in enumerate(voltages):
            voltlogfile.write(f"\n{timestamp};{idx};{voltage}")
    if app_dac.temp_index%11==0:
        #requests.post("http://127.0.0.1:5000/app_temp/get_temp_values")
        app_dac.temp_index-=10
    app_dac.temp_index+=1
    return jsonify(data={"voltages":voltages})