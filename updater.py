import os
import json
import zipfile
import requests
import subprocess


def update(user_config):

    try:
        remote_commit_hash = json.decoder.JSONDecoder().decode(requests.get("https://api.github.com/repos/manuel-covas/zoom-earlybird/commits", headers={"Accept": "application/vnd.github.v3+json"}).text)[0]["sha"]

        if remote_commit_hash != user_config["local_commit_hash"]:
            print("New version available. Updating...")

            update_zip = open("update.zip", "wb")
            update_zip.write(requests.get("https://github.com/manuel-covas/zoom-earlybird/archive/refs/heads/main.zip", stream=True).raw.read())
            update_zip.close()

            update_zip = zipfile.ZipFile("update.zip")
            
            for member in update_zip.namelist():
                try:
                    trimmed_name = member.split("zoom-earlybird-main")[1]
                    if len(trimmed_name) < 2:
                        continue
                    
                    temp = open(trimmed_name[1::], "wb")
                    temp.write(update_zip.read(member))
                    temp.close()
                except:
                    print("Failed to extract "+member+" from update.zip")

            update_zip.close()
            os.remove("update.zip")
            user_config["local_commit_hash"] = remote_commit_hash
            
            return True
        else:
            return False

    except:

        print("Update check failed, continuing.")
        return False