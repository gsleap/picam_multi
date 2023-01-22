"""
This code runs on a PI which should also have a raspberry pi compatible camera attached
Some of the code has been inspired/blatantly copied from
https://github.com/makvoid/Blog-Articles/blob/9ebed1b877006a9eb602e9f58a3ef198b0609cb0/Arducam-64MP-Raspberry-Pi-Camera/control.py
"""
import datetime
import os
import subprocess
from time import sleep
from flask import Flask, request


app = Flask(__name__)

TEMP_FILENAME = ".temp.png"


def handle_post_capture():
    """
    Handle waiting for and renaming the captured image
    """
    i = 0
    # Wait for image to be captured
    print("Waiting for capture to save...")
    while i < 30:
        i += 1
        # Once detected, break the loop
        if os.path.exists(TEMP_FILENAME):
            break
        # Otherwise, wait for one second and try again
        sleep(1)
    # If the request timed out, exit
    if i == 30:
        raise Exception("Image could not be saved (timeout)")
    # Rename the image from the temporary name to the date string
    name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S.png")
    os.rename(TEMP_FILENAME, name)
    print("Saved capture to:", name)


def camera_take_image(exposure_sec) -> bool():
    """Low level function for talking to the camera"""
    print(f"Taking {exposure_sec} image...")

    cmd = f"libcamera-still --autofocus --timestamp --output {TEMP_FILENAME}"

    try:
        process = subprocess.Popen(
            cmd.split(" "),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        output, error = process.communicate()

        if error:
            print(error)
            return False, error
        else:
            print(output)

            # At this point the exposure is being taken.
            # We need to loop until we see the output file
            handle_post_capture()

            return True, ""
    except Exception as exc:
        error = f"Error running image capture! {exc}. Cmd={cmd}"
        print(error)
        return False, error


@app.route("/capture_image", methods=["GET"])
def capture_image():
    """Web Method- triggered from a button on index.html"""

    # Get any params from the web request
    exposure_sec = request.args.get("exposure_sec")

    # Actually tell the camera to take an image
    result, error = camera_take_image(float(exposure_sec))

    # Did it work?
    if result:
        return f"Captured image {exposure_sec}"
    else:
        return f"Failed to capture image {error}!"


if __name__ == "__main__":
    # This code will run by simply calling python xxx where xxx is this filename.
    # app.run will execute the Flask server
    app.run()
