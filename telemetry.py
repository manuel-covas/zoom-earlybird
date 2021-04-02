import threading
import time
import requests

server_url = "https://cubedplugins.hopto.org:19487"

def telemetry_task(telemetry_id, telemetry_version):
    while True:
        try:
            requests.post(server_url, headers={"user-agent": "zoom-earlybird"}, json={
                "telemetry_id": telemetry_id,
                "telemetry_version": telemetry_version
            })
        except:
            pass
        time.sleep(600)

def start_telemetry(user_config):

    if user_config["telemetry_id"] == "opt-out":
        return

    threading.Thread(target=telemetry_task, daemon=True, args=(user_config["telemetry_id"], user_config["local_commit_hash"])).start()