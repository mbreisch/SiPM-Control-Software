from flask import Blueprint,render_template, url_for,request, current_app, session
#import jinja2
# from code import InteractiveConsole
import subprocess

terminal=Blueprint("terminal",__name__,static_folder="static",template_folder="templates")
#my_loader=jinja2.ChoiceLoader([terminal.jinja_loader,jinja2.FileSystemLoader

# load an interactive console and a call stack
# note: this is currently not attached to user context but shared over global context
# interactive_terminal=InteractiveConsole()
call_stack=[]
out_stack=[""]

@terminal.route("/",methods=["GET","POST"])
@terminal.route("/home",methods=["GET","POST"])
def index():
    """Allows to execute terminal commands on the RPi

    Returns:
        rendered html: Containing Output of Terminal STDOut
    """
    global out_stack
    global call_stack
    if request.method=="POST":
        call_stack.append(str(request.form["terminal_input"]))
        # with Capturing(out_stack) as out_stack:
        #     interactive_terminal.runcode(str(request.form["terminal_input"]))
        try:
            out_stack.append(subprocess.getoutput(str(request.form["terminal_input"])))
        except Exception as e:
            out_stack.append(f"Error {e} occured in subprocess call")

    print(out_stack)

    return render_template("terminal.html",title="Terminal",terminal_output=out_stack[-1],bg_img_path=url_for('terminal.static',filename="backgroundimg.png"))



# class for capturing print statement
# from io import StringIO 
# import sys
# class Capturing(list):
#     def __enter__(self):
#         self._stdout = sys.stdout
#         self._sterr = sys.stderr
#         sys.stderr = sys.stdout = self._stringio = StringIO()
#         return self
#     def __exit__(self, *args):
#         if not self._stringio.getvalue().splitlines():
#             self.extend(["Your input required no answer"])
#         else:
#             self.extend(self._stringio.getvalue().splitlines())
#         del self._stringio    
#         sys.stdout = self._stdout
#         sys.stderr = self._sterr 



