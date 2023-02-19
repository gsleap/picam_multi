"""
This code runs on a PI which should also have a raspberry pi compatible camera attached
Some of the code has been inspired/blatantly copied from
https://github.com/makvoid/Blog-Articles/blob/9ebed1b877006a9eb602e9f58a3ef198b0609cb0/Arducam-64MP-Raspberry-Pi-Camera/control.py
"""
import datetime
import os
import subprocess
import socket
from signal import SIGUSR1
from subprocess import Popen, DEVNULL
from time import sleep
from flask import Flask, request
import shutil

app = Flask(__name__)

TEMP_FILENAME = "/tmp/temp.png"

def get_network_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", 0))
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

print(get_network_ip())
myIP = get_network_ip()
myHost = socket.getfqdn()

def handle_post_capture():
    """
    Handle waiting for and renaming the captured image
    """
    i = 0
    # Wait for image to be captured
    print("Waiting for capture to save...")
    while i < 50:
        i += 1
        # Once detected, break the loop
        if os.path.exists(TEMP_FILENAME):
            break
        # Otherwise, wait for one second and try again
        sleep(0.2)
    # If the request timed out, exit
    if i == 50:
        raise Exception("Image could not be saved (timeout)")
    print(f"looped for {i} seconds")
    # Rename the image from the temporary name to the date string
    name = f"/home/picam/{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S.png')}"
    os.rename(TEMP_FILENAME, name)
    print("Saved capture to:", name)


def camera_take_image(exposure_sec) -> bool():
    """Low level function for talking to the camera"""
    print(f"Taking {exposure_sec} image...")
    #--viewfinder-width 2312 --viewfinder-height 1736
    #cmd = f"libcamera-still -n -t 1 --autofocus-mode manual --lens-position 2 --denoise cdn_off --awb indoor --output {TEMP_FILENAME}"

#     try:
#         process = subprocess.Popen(
#             cmd.split(" "),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             universal_newlines=True,
#         )
#         output, error = process.communicate()
# 
#         if error:
#             print(error)
#             #return False, error
#         else:
#             print(output)
# 
#             # At this point the exposure is being taken.
#             # We need to loop until we see the output file
#         handle_post_capture()
# 
#         return True, ""
#     except Exception as exc:
#         error = f"Error running image capture! {exc}. Cmd={cmd}"
#         print(error)
#         return False, error
    
   #daves modification for SIGUSR1  
    try:
        
        process.send_signal(SIGUSR1)
        #process = Popen(cmd.split(' '), stdout=DEVNULL, stderr=DEVNULL)
        print ("image taken starting post")
        
        # not doing post capture while files are just written out with --datetime
        
        #handle_post_capture()
        return True, ""
    except Exception as exc:
        error = f"Error running image capture! {exc}. Cmd={cmd}"
        print(error)
        return False, error

#start camera
#--width 9152 --height 6944
#--lens-position 1
#cmd = f"libcamera-still -t 0 -n  --autofocus-mode manual --lens-position 2 --gain 8 --shutter 30000 --denoise cdn_off --awb indoor --immediate --width 7908 --height 6000 --signal -e png --output {TEMP_FILENAME}"

#would love to use --immediate below as it is fast but doesnt allow a second image to be taken....

cmd = f"libcamera-still -t 0 -n  --autofocus-mode manual --lens-position 2 --width 9152 --height 6944 --denoise cdn_off --gain 9 --shutter 10000 --awbgains 2.0,1.8 --signal --datetime"

#cmd = f"libcamera-still -t 10000 -n  --autofocus-mode manual --lens-position 2 --denoise cdn_off --gain 9 --shutter 10000 --awbgains 2.0,1.8 --timelapse  1000 --datetime"
process = Popen(cmd.split(' '), stdout=DEVNULL, stderr=DEVNULL)

@app.route("/capture_image", methods=["GET"])
def capture_image():
    """Web Method- triggered from a button on index.html"""
    if os.path.exists(TEMP_FILENAME):
        os.remove(TEMP_FILENAME)
    # Get any params from the web request
    exposure_sec = request.args.get("exposure_sec")

    # Actually tell the camera to take an image
    result, error = camera_take_image(float(exposure_sec))

    # Did it work?
    if result:
        return f"Captured image {exposure_sec}"
    else:
        return f"Failed to capture image {error}!"

@app.route("/test_connection", methods=["GET"])
def test_connection():
    """Web Method- triggered from a button on index.html"""
    #if os.path.exists(TEMP_FILENAME):
        #os.remove(TEMP_FILENAME)
    # Get any params from the web request
    exposure_sec = request.args.get("exposure_sec")

    # Actually tell the camera to take an image
    #result, error = camera_take_image(float(exposure_sec))
    
    # Did it work?
    return f"Online: {myHost}:{myIP}"
    



if __name__ == "__main__":
    # This code will run by simply calling python xxx where xxx is this filename.
    # app.run will execute the Flask server
    app.run(host="0.0.0.0")
