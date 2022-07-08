# This file is used to make a web-server so that Replit can allow this bot to run it background

from flask import Flask
from threading import Thread

app = Flask("")

@app.route("/")
def home():
    return "Web Server is Live."

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()