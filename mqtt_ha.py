#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/local/bin/python3
# -*- coding: utf-8 -*-
# <xbar.title>Battery remaining (Python)</xbar.title>
# <xbar.version>v1.0.0</xbar.version>
# <xbar.author>Eric Ripa</xbar.author>
# <xbar.author.github>eripa</xbar.author.github>
# <xbar.desc>Show battery charge percentage and time remaining</xbar.desc>
# <xbar.image>http://i.imgur.com/P6aNey5.png</xbar.image>
# <xbar.dependencies>python</xbar.dependencies>

from __future__ import print_function
import re
import sys
import subprocess
import random
import time
from paho.mqtt import client as mqtt_client


broker = ''
port = 1883
topic = "home/macbook/temperature"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'mqtt'
password = ''


def parse_pmset():
    output = subprocess.check_output(["/usr/bin/pmset", "-g", "batt"])
    output = output.decode("utf-8").split('\n')
    regex = re.compile(r'^.*\s(?P<charge>\d+%);\s((?P<status>discharging|'
                       r'charging|finishing charge|charged);\s(?P<remain>\(no estimate\)|\d+:\d+) '
                       r'(remaining )?present|AC attached; not charging present): true$')

    battery = {
        "charge": "unknown",
        "status": "unknown",
        "remaining": "unknown",
    }

    battery_match = regex.match(output[1])
    if not battery_match:
        return battery

    battery["charge"] = battery_match.group("charge")
    battery["status"] = battery_match.group("status")
    battery["remaining"] = battery_match.group("remain")
    if battery["remaining"] == "(no estimate)":
        battery["remaining"] = "calculating.."
    if battery["remaining"] == "0:00" and battery["status"] == "charged":
        battery["remaining"] = "∞"
    return battery


def connect_mqtt():
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    #client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    msg_count = 0
    time.sleep(1)
        
    battery = parse_pmset()
    refresh_interval = sys.argv[0].split('.')[1]
    print("{}| size=12".format(battery["charge"]))

    msg = battery["charge"].replace('%', '')

    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print("{}| size=12".format(battery["charge"]))
    else:
        print(f"Failed to send message to topic {topic}")


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)

if __name__ == '__main__':
    run()
