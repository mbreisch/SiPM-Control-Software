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
from termcolor import colored
import requests

from . import daq_bp

sys.path.append(daq_bp.static_folder)

@daq_bp.route('/',methods=["GET","POST"])
@daq_bp.route("/home",methods=["GET","POST"])
@login_required
def daq_home():
    return render_template("daq.html",title="DAQ Control")

daq_bp._title="DAQ Control"