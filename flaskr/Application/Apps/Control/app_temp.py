from flask import Blueprint,render_template, url_for,request,jsonify,redirect,session, json, redirect, current_app
import subprocess
import sys
import os
import numpy as np
from w1thermsensor import W1ThermSensor, Unit

app_temp=Blueprint("app_temp",__name__,static_folder="static",template_folder="templates")
#my_loader=jinja2.ChoiceLoader([terminal.jinja_loader,jinja2.FileSystemLoader
sys.path.append(app_temp.static_folder)
from Temperature_Sensor import DS18B20


app_temp._title="Temperature"
app_temp.paths=["/sys/bus/w1/devices/28-00000c7e5ff0/w1_slave"]
app_temp.pixel=8

 
@app_temp.route("/",methods=["GET","POST"])
@app_temp.route("/home",methods=["GET","POST"])
def index():
    """Renders Home Page for Temperature APP. 
    Shows all Temperature Sensors on a 8x8 Grid. 
    Sensors not sorted. 
    Called GET/POST at / and /home

    Returns:
        rendered html: The Home Page for the Temperature APP
    """
    return render_template("temperature.html",title="Temperature Interface", bg_img_path=url_for('app_temp.static',filename="background_dk.jpeg", url_call="/get_json"))

@app_temp.route("/init_temperature",methods=["POST"])
def init_temperature():
    """Initialises the Temperature Sensors. 
    Looks for all available sensors.
    Called POST at /init_temperature

    Returns:
        json: data contains working sensors
    """
    app_temp.sensors=[]
    sensors=[0]*app_temp.pixel
    sens=W1ThermSensor.get_available_sensors()
    app_temp.paths=[sensor.id for sensor in sens]
    for temp_idx in range(app_temp.pixel):
        try:
            sensor=DS18B20(f"/sys/bus/w1/devices/28-{app_temp.paths[temp_idx]}/w1_slave",temp_idx)
            app_temp.sensors.append(sensor)
            sensors[temp_idx]=1
        except Exception as e:
            print(f"Got Exception {e} in init Temperature")
    print(app_temp.paths)
    return jsonify(data=sensors,success=True)
    
    
    
@app_temp.route("/get_temp_values",methods=["POST"])
def ajax_response():
    """Tries to get Data of the initialised Temperature Sensors. 
    Saves the values with their timestamp in a array in Order of their occurence in app_temp.sensors.
    Called POST at /init_temperature
    
    Returns:
        json: data contains list of time of temperature measurement and temperature 
    """
    try:
        times=[0]*app_temp.pixel
        temps=[0]*app_temp.pixel
        paths=[0]*app_temp.pixel
        for idx,sensor in enumerate(app_temp.sensors):
            sensor.get_temperature()
            times[sensor.idx]=sensor.data[0]
            temps[sensor.idx]=f"{sensor.data[1]:.1f}"
            try:
                paths[sensor.idx]=sensor.path.split("/")[5]
            except IndexError:
                paths[sensor.idx]="0"
        with open("/home/pi/Desktop/sipm_ctl/temp.log","a") as templogfile:
            for idx in range(len(times)):
                templogfile.write(f"\n{times[idx]};{temps[idx]};{paths[idx]}")
        return jsonify(data={"times":times,"temps":temps,"paths":paths},success=True)
    except Exception as e:
        return jsonify(data={"times":[],"temps":[],"paths":[]},success=False)
    