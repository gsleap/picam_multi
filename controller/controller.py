"""
This code runs on your "control" machine.
It's also a server but only in that it runs a tiny webserver
so you have a simple GUI to control the cameras.
When clicked the button will trigger capture of
all the pi cameras.
"""
import concurrent.futures
import requests
from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates")

# Change this list to be the IP addresses of your PI "servers"
PI_SERVERS = ["127.0.0.1", "192.168.2.119"]


def fetch(url, params):
    """
    Function to make a GET request to a given URL with a parameter
    """
    response = requests.get(url, params=params, timeout=10)
    return response.text


@app.route("/")
def index():
    """
    This method will run when there is a web request
    for '/'
    """
    return render_template("index.html")


@app.route("/capture_image", methods=["GET"])
def capture_image():
    """
    This method will run when there is a web request
    for '/capture_image'
    """
    # Get parameters from web request
    exposure_sec = request.args.get("exposure_sec")

    # Generate URLS
    urls = []
    for server in PI_SERVERS:
        url = f"http://{server}:5000/capture_image"
        urls.append(url)

    # Use a ThreadPoolExecutor to run the functions in parallel
    output = ""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [
            executor.submit(fetch, url, {"exposure_sec": exposure_sec})
            for url in urls
        ]
        for f in concurrent.futures.as_completed(results):
            try:
                result = f.result()
                print(result)
                output += f"{result}</br>"
            except Exception as exc:
                output += f"Error: {exc}</br>"

    return output


if __name__ == "__main__":
    #app.run(port=8080)
    app.run(debug=True, port=8080, host='0.0.0.0')
