import subprocess
import os,time,sys,signal,platform
def start_app(path="/mnt/d/SiALG_DATA/sipm_ctl/flaskr"):
    """Starts Flask Development Server close with ctrl+c

    Args:
        path (str): Path to Application
    """
    os.chdir(path)
    cwd=os.getcwd()
    print(cwd)
    commands=f"cd {cwd}; export FLASK_APP=Application; export FLASK_ENV=development; flask run --host=0.0.0.0"
    try:
        proc=subprocess.Popen(commands,shell=True)
        while True:
            time.sleep(60)
    except Exception as e:
        print(f"Stop Flask Server Exception {e}")
        proc.send_signal(signal.SIGINT)
        subprocess.Popen.kill(proc)

if sys.argv[1][0]=="/":
    start_app(sys.argv[1])
else:
    pass
    start_app()