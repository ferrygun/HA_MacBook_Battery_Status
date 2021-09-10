#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/local/bin/python3
# -*- coding: utf-8 -*-
# <xbar.title>Battery remaining (Python)</xbar.title>
# <xbar.version>v1.0.0</xbar.version>
# <xbar.author>Ferry Djaja</xbar.author>
# <xbar.author.github>ferrydjaja</xbar.author.github>
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
username = ''
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

def main():
    battery = parse_pmset()
    refresh_interval = sys.argv[0].split('.')[1]
    print("{}| size=12".format(battery["charge"]))
    print(battery["charge"].replace('%', ''))
    print("---")
    print("Status: {}".format(battery["status"]))
    print("Remaining: {}".format(battery["remaining"]))
    print("Refresh (current interval: {}) | refresh=true".format(refresh_interval))

def connect_mqtt():
    #def on_connect(client, userdata, flags, rc):
    #    if rc == 0:
    #        print("Connected to MQTT Broker!")
    #    else:
    #        print("Failed to connect, return code %d\n", rc)

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
    #print(battery["charge"].replace('%', ''))
    #print("---")
    #print("Status: {}".format(battery["status"]))
    #print("Remaining: {}".format(battery["remaining"]))
    #print("Refresh (current interval: {}) | refresh=true".format(refresh_interval))

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
