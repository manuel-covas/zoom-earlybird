import platform
import psutil
import subprocess
import datetime
import time


# Attempt to find the path to zoom's executable

def whereis_zoom():

    if platform.system() == "Windows":
        return input("Windows detected, please enter path to Zoom.exe: ")

    elif platform.system() == "Linux":
        
        try:
            whereis_path = subprocess.run(args=["whereis", "zoom"], capture_output=True).stdout.decode("UTF-8").split("\n")[0].strip().split("zoom: ")[1]
        except:
            whereis_path = "Failed to find zoom"

        if input("Linux detected, does '"+whereis_path+"' look right? [y/n]: ") == "y":
            return whereis_path
        return input("Please enter path to zoom executable: ")

    elif platform.system() == "Darwin":
        return input("macOS detected, please enter path to zoom executable: ")


# Terminate all zoom processes

def seek_and_terminate():
    for pid in psutil.pids():
        
        try:
            process = psutil.Process(pid)
            path = process.cmdline()[0].lower()
            
            if path.count("zoom.exe") > 0 or path.count("zoom-client") or path.count("bin\\zoom") > 0 or path.count("bin/zoom") > 0 or path.count("zoom/zoom") > 0 or path.count("zoom.us") > 0:
                process.terminate()
                print("Terminated {0} (PID: {1})".format(path, pid))
        except:
            continue

    time.sleep(1)


# Pass an URL to zoom

def zoom_pass_url(url, user_config):
    subprocess.Popen(args=[user_config["zoom_path"], "--url=\""+url+"\""])


# Suspend machine for duration_seconds

def suspend_machine(duration_seconds):
    
    system_name = platform.system()

    if system_name == "Windows":
        
        print("Windows detected, scheduling wakeup with Task Scheduler...")
        print("Deleting any previous task...")
        subprocess.run(args=["schtasks", "/Delete", "/TN", "zoom-earlybird", "/F"])

        wakeup_time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(seconds=duration_seconds)

        base_task = open("windows-wakeup-task-template.xml", "r")
        wakeup_task = base_task.read().format(year   = wakeup_time.year,
                                              month  = wakeup_time.month,
                                              day    = wakeup_time.day,
                                              hour   = wakeup_time.hour,
                                              minute = wakeup_time.minute,
                                              second = wakeup_time.second)
        base_task.close()
        
        wakeup_task_file = open("windows-wakeup-task.xml", "w")
        wakeup_task_file.write(wakeup_task)
        wakeup_task_file.close()

        print("Scheduling wakeup task for " + str(wakeup_time) + "...")
        
        if subprocess.run(args=["schtasks", "/Create", "/XML", "windows-wakeup-task.xml", "/TN", "zoom-earlybird", "/F"]).returncode != 0:
            print("Failed to schedule wakeup task, not suspending.")
            return

        print("Wakeup task sheduled. Suspending with psshutdown.exe...")
        time.sleep(5)

        subprocess.run(args=["psshutdown.exe", "-d", "-t", "0"])

    elif system_name == "Linux":

        print("Linux detected, suspending with RTCWake...")
        time.sleep(5)

        subprocess.run(args=["sudo", "rtcwake", "-m", "mem", "-s", str(duration_seconds)])

    elif system_name == "Darwin":

        print("macOS detected, suspending with pmset...")
        time.sleep(5)

        if subprocess.run(args=["pmset", "relative", "wake", str(duration_seconds)]).returncode != 0:
            print("pmset failed, not suspending.")
            return

        subprocess.run(args=["pmset", "sleepnow"])

    else:
        print("Unknown operating system, not suspending.")