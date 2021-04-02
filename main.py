import os
import time
import datetime
import psutil
import getpass
import subprocess

import json
import secrets

# Local code

from updater import update
from telemetry import start_telemetry
from ssologin import sso_login
from platform_specific import *


# Configuration

def save_config():
    config_file = open("config.json", "w")
    config_file.write(json.encoder.JSONEncoder(indent=4).encode(user_config))
    config_file.close()

user_config = {}

try:
    config_file = open("config.json", "r")
    user_config = json.decoder.JSONDecoder().decode(config_file.read())
    config_file.close()
except:
    print("Creating new configuration file.")

    user_config = {
        "telemetry_id": secrets.token_hex(16),  # Random ID for telemetry, in config.json set to "opt-out" to opt-out of telemetry
        "local_commit_hash": "",
        "zoom_path": whereis_zoom(),
        "identity_provider": input("Identity provider URL (choose from list): "),
        "username": input("Username (<username>@domain.com): "),
        "password": getpass.getpass(),
        "schedule": {
            "Monday": [
                {"time": "08:00:00", "url": ""}
            ],
            "Tuesday": [
                {"time": "08:00:00", "url": ""}
            ],
            "Wednesday": [
                {"time": "08:00:00", "url": ""}
            ],
            "Thursday": [
                {"time": "08:00:00", "url": ""}
            ],
            "Friday": [
                {"time": "08:00:00", "url": ""}
            ],
            "Saturday": [
                {"time": "08:00:00", "url": ""}
            ],
            "Sunday": [
                {"time": "08:00:00", "url": ""}
            ]
        }
    }
    try:
        # Check that the provided file exists
        open(user_config["zoom_path"], "r").close()
    except:
        print("Failed to open file at "+user_config["zoom_path"]+"! Invalid path?")
        exit(0)

    save_config()
    print("Configuration saved, go fill in your schedule. (config.json)")
    exit(0)


# Set your telemetry_id to "opt-out" to opt-out of telemetry

start_telemetry(user_config)


# Check for a new version

if update(user_config):
    save_config()
    print("Updated to commit "+user_config["local_commit_hash"])
    print("Restarting...")
    subprocess.Popen(args=[psutil.Process().cmdline()[0], "main.py"], cwd=os.getcwd())
    exit(0)
else:
    print("\nCurrently running commit "+user_config["local_commit_hash"])



# Parse meeting schedule

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

current_time = datetime.datetime.now()
current_weekday = current_time.weekday()

print("\nLoaded Zoom meetings schedule:")

for weekday in weekdays:

    if weekdays[current_weekday] == weekday:
        print("\n"+weekday+": (today)")
    else:
        print("\n"+weekday+":")

    meetings = user_config["schedule"][weekday]

    for meeting in meetings:
        if meeting["time"].count(":") != 2:
            print("Invalid meeting time: " + meeting.meeting["time"] + "\nFormat: HH:MM:SS")
            exit(0)
        split_time = meeting["time"].split(":")
        meeting["time"] = (datetime.datetime.now() + datetime.timedelta(days = weekdays.index(weekday) - current_weekday)).replace(hour=int(split_time[0]), minute=int(split_time[1]), second=int(split_time[2]), microsecond=0)

    meetings.sort(key=lambda item: item["time"])

    for meeting in meetings:
        print(str(meeting["time"]) + " - " + meeting["url"])




def attend(should_sleep):

    current_time = datetime.datetime.now()
    attending_weekday = current_weekday
    attending_meetings = []
    meetings = user_config["schedule"]

    loops = 0
    while True:

        for meeting in meetings[weekdays[attending_weekday]]:
            if meeting["time"] >= current_time:
                attending_meetings.append(meeting)

        if len(attending_meetings) > 0:
            break

        if attending_weekday < 6:
            attending_weekday += 1
        else:
            attending_weekday = 0
            seven_day_delta = datetime.timedelta(days=7)

            for weekday in weekdays:
                for meeting in meetings[weekday]:
                    meeting["time"] += seven_day_delta

        loops += 1
        if loops == 7:
            print("No meetings scheduled, fill in config.json")
            exit(0)
        
        print("No meetings left for today, checking " + weekdays[attending_weekday])
    

    time_delta = attending_meetings[0]["time"] - current_time

    if should_sleep:
        if time_delta < datetime.timedelta(minutes=5):
            print("Refusing to sleep for less than 5 minutes.")
        else:
            suspend_machine(int(time_delta.total_seconds()))


    # Probe periodically to be suspension safe and compensate for inaccurate wakeup times
    
    sso_signed_in = False

    for meeting in attending_meetings:

        print("Waiting, "+meeting["url"]+" scheduled for " + str(meeting["time"]))

        while True:
            time.sleep(30)
            if datetime.datetime.now() > meeting["time"]:
                break
        
        seek_and_terminate()

        if not sso_signed_in:
            try:
                sso_url = sso_login(user_config)
                zoom_pass_url(sso_url, user_config)
                sso_signed_in = True
                time.sleep(10)
            except Exception as exception:
                print("Error in SSO login flow:")
                print(exception)

        
        zoom_pass_url(meeting["url"], user_config)

    print("Done with today's meetings.")



while True:
    print("\n"+
            "Options:\n"+
            "  sso:         test sso login\n"+
            "  test-wakeup: test machine wakeup scheduling\n"+
            "  arm:         arm script, schedule wakeup and suspend machine\n"+
            "  arm-nosleep: arm script but let you deal with suspend/wakeup")
    
    try:
        choice = input("zoom-earlybird > ")
    except:
        exit(0)

    if choice == "sso":
        try:
            zoom_pass_url(sso_login(user_config), user_config)
        except Exception as exception:
            print("Error in SSO login flow:")
            print(exception)
    elif choice == "test-wakeup":
        print("Testing machine wakeup, sleeping for 2 minutes...")
        suspend_machine(120)
    elif choice == "arm":
        attend(True)
    elif choice == "arm-nosleep":
        attend(False)
    else:
        continue