from datetime import datetime
from flask import Flask, redirect, url_for, render_template, request, current_app,jsonify
from os import path, getcwd,listdir
import spidev
import sys
sys.path.append(path.join(getcwd(),"Application","Apps"))
import fcntl
import struct
import socket


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def init_blueprints():
    """Initialises all flask blueprints

    Returns:
        html template: rendered flask html templates
    """
    # register the terminal in navbar
    from Application.NavBarItems.Terminal.terminal_app import terminal
    current_app.register_blueprint(terminal,url_prefix="/terminal")
    # register all other apps
    import Application.Apps as all_apps
    real_apps=[]
    for application in dir(all_apps):
        if application[:2]!="__":
            current_app.register_blueprint(getattr(all_apps,application),url_prefix=f"/{application}")
            getattr(all_apps,application)._str=application
            real_apps.append(getattr(all_apps,application))
        
    print(dir(all_apps))
    spi = spidev.SpiDev()
    spi_port=0
    speedHZ=400000
    spi.open(spi_port, 1)
    spi.max_speed_hz = speedHZ
    for app in real_apps:
        app.spi=spi


    @current_app.route("/home")
    @current_app.route("/")
    def index():
        """Renders Homepage to Navigate to all Apps in Apps Directory.

        Returns:
            rendered html: Homepage of Application
        """
        return render_template("index.html", title="Home",bg_img_path=url_for('static', filename="fallback_bg.jpeg"),apps=real_apps)
        
    @current_app.route("/sysinfo",methods=["POST"])
    def sysinfo():
        import re,uuid

        mac=':'.join(re.findall('..', '%012x' % uuid.getnode())) 
        ip_eth0=get_ip_address(b"eth0")
        ip_wlan0=get_ip_address(b"wlan0")
        host= socket.gethostname()
        date=datetime.now().strftime("%d-%m-%Y--%H:%M:%S")
        return jsonify(data={"hostname":host,"mac":mac,"ip_eth0":ip_eth0,"ip_wlan0":ip_wlan0,"date":date})
        

