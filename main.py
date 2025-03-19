import asyncore
import binascii
import datetime
from datetime import date
from main import get_db_connection
import threading
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from sms import SMS
import os
import paho.mqtt.client as mqtt
object_sms = ''
index = 0

import os
broker_address = os.getenv("BROKER_ADDRESS", "192.168.1.102")



import os
import json

# Read options from Home Assistant's config.yaml
config_path = "/data/options.json"  # Home Assistant stores options here
with open(config_path, "r") as config_file:
    options = json.load(config_file)

# Get sensor IDs from config.yaml
list_of_cold_room_sensors = options.get("cold_room_sensors", [])
list_of_normal_room_sensors = options.get("normal_room_sensors", [])



def drop_row(sensorid):
    conn = get_db_connection()
    conn.execute('DELETE FROM alarms WHERE sensorid='+sensorid)
    conn.commit()
    conn.close()

def send_sms(TypeOfAlarm, sensorid, Gatewayid, value, time) :
    global object_sms
    conn = get_db_connection()
    numbers = conn.execute('SELECT Number FROM numbers ').fetchall()
    alarm_message = 'There are Alarm \n'+ 'Alarm Case :'+str(TypeOfAlarm)+'\n'+'Sensor Id :'+str(sensorid)+'\n'+'Value:'+str(value)+'\n'+'time:'+str(time)+'\n'
    print(len(alarm_message))
    for num in numbers :
        object_sms.write_content(str(num['Number']),alarm_message)
    time.sleep(5)




def send_mqtt(topic):
    print("creating new instance")
    client = mqtt.Client("P1")  # create new instance
    print("connecting to broker")
    client.username_pw_set(username="homeassistant", password="eizisulohzo6AhQuoo2nufieW2ceiZ6niGa6Oopae3ooSiej2kiesee6uih3au9n")

    client.connect(broker_address)  # connect to broker

    # client.subscribe("LastAttendance")
    client.publish(str(topic),"1")


def assign_to_database(TypeOfAlarm, sensorid, Gatewayid, value, time):
    conn = get_db_connection()
    numbers = conn.execute('SELECT * FROM alarms WHERE sensorid=' + sensorid).fetchall()
    if not numbers:
        conn.execute('INSERT INTO alarms (type ,sensorid ,gatewayid ,value ,time,sendstatus ) VALUES (?,?,?,?,?,?)',
                     (TypeOfAlarm, sensorid, Gatewayid, value, time,"Not Sent"))

        alarms = conn.execute('SELECT * FROM duration').fetchall()
        if str(sensorid) in list_of_cold_room_sensors :
            threading.Timer(float(alarms[0]['cold_time']*60), drop_row, args=(sensorid,)).start()
            print('cold_time',sensorid)
            send_mqtt("cold room")
        elif str(sensorid) in list_of_normal_room_sensors:
            threading.Timer(float(alarms[0]['normal_time'] * 60), drop_row, args=(sensorid,)).start()
            print('normal_time',sensorid)
            send_mqtt("normal room")



        #x = threading.Thread(target=send_sms, args=(TypeOfAlarm, sensorid, Gatewayid, value, time,))
        #x.start()
        #send_sms(TypeOfAlarm, sensorid, Gatewayid, value, time)
        #send_mqtt(sensorid)

    conn.commit()
    conn.close()


def delete_database():
    # initialization database
    conn = get_db_connection()
    conn.execute('DELETE FROM alarms')
    conn.execute('DELETE FROM groupm')
    conn.commit()
    conn.close()

def ini_sms():
    global object_sms
    object_sms = SMS()
    time.sleep(5)

def convertdata(s):
    global index
    s = s.replace("\n", "")
    s = s.replace("b'", "")
    s = s.replace("\n\n'", "")
    outlist = s.split("}")
    TypeOfAlarm = outlist[0].split(',')[0].split(":")[1].replace("\"", "")
    sensorid = outlist[4].split(',')[-1].split(":")[1].replace("\"", "")
    Gatewayid = outlist[4].split(',')[-2].split(":")[2].replace("\"", "")
    value = outlist[5].split(',')[4].replace("]]", "")
    time = outlist[5].split(',')[3].replace("]]", "").replace("[[", "").split("\"")[3]

    assign_to_database(TypeOfAlarm, sensorid, Gatewayid, value, time)


class EchoHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(8192)
        if data:
            convertdata(str(data))


class EchoServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        print('Incoming connection from %s' % repr(addr))
        handler = EchoHandler(sock)


if index == 0:
    delete_database()
    index += 1

server = EchoServer('', 5060)
asyncore.loop()
