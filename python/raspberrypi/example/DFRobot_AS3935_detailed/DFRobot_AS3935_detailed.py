'''
 # @file DFRobot_AS3935_detailed.py
 # @brief SEN0290 Lightning Sensor
 # @n This sensor can detect lightning and display the distance and intensity of the lightning within 40 km
 # @n It can be set as indoor or outdoor mode.
 # @n The module has three I2C, these addresses are:
 # @n  AS3935_ADD1  0x01   A0 = 1  A1 = 0
 # @n  AS3935_ADD2  0x02   A0 = 0  A1 = 1
 # @n  AS3935_ADD3  0x03   A0 = 1  A1 = 1
 # @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
 # @licence     The MIT License (MIT)
 # @author [TangJie](jie.tang@dfrobot.com)
 # @version  V1.0.2
 # @date  2019-09-28
 # @url https://github.com/DFRobor/DFRobot_AS3935
'''
import sys
import pika
import json
import datetime
sys.path.append('../')
import time
from DFRobot_AS3935_Lib import DFRobot_AS3935
import RPi.GPIO as GPIO
from datetime import datetime

#I2C address
AS3935_I2C_ADDR1 = 0X01
AS3935_I2C_ADDR2 = 0X02
AS3935_I2C_ADDR3 = 0X03

#Antenna tuning capcitance (must be integer multiple of 8, 8 - 120 pf)
AS3935_CAPACITANCE = 96
IRQ_PIN = 37

GPIO.setmode(GPIO.BOARD)

sensor = DFRobot_AS3935(AS3935_I2C_ADDR2, bus = 1)
if (sensor.reset()):
  print("init sensor sucess.")
else:
  print("init sensor fail")
  while True:
    pass
#Configure sensor
sensor.power_up()

#set indoors or outdoors models
sensor.set_indoors()
#sensor.set_outdoors()

#disturber detection
sensor.disturber_en()
#sensor.disturber_dis()

sensor.set_irq_output_source(0)
time.sleep(0.5)
#set capacitance
sensor.set_tuning_caps(AS3935_CAPACITANCE)

# Connect the IRQ and GND pin to the oscilloscope.
# uncomment the following sentences to fine tune the antenna for better performance.
# This will dispaly the antenna's resonance frequency/16 on IRQ pin (The resonance frequency will be divided by 16 on this pin)
# Tuning AS3935_CAPACITANCE to make the frequency within 500/16 kHz plus 3.5% to 500/16 kHz minus 3.5%
#
# sensor.setLco_fdiv(0)
# sensor.setIrq_output_source(3)

#Set the noise level,use a default value greater than 7
sensor.set_noise_floor_lv1(2)
#noiseLv = sensor.get_noise_floor_lv1()

#used to modify WDTH,alues should only be between 0x00 and 0x0F (0 and 7)
sensor.set_watchdog_threshold(2)
#wtdgThreshold = sensor.get_watchdog_threshold()

#used to modify SREJ (spike rejection),values should only be between 0x00 and 0x0F (0 and 7)
sensor.set_spike_rejection(2)
#spikeRejection = sensor.get_spike_rejection()

#view all register data
#sensor.print_all_regs()

#setup rabbitmq message queue
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=300, blocked_connection_timeout=600))
global rabbitChannel
rabbitChannel = connection.channel()
rabbitChannel.queue_declare(queue='lightning_data')
hasNotDisturbed = True

def callback_handle(channel):
  global sensor
  global hasNotDisturbed
  time.sleep(0.005)
  intSrc = sensor.get_interrupt_src()
  if intSrc == 1:
    lightning_distKm = sensor.get_lightning_distKm()
    lightning_energy_val = sensor.get_strike_energy_raw()
    print('Lightning occurs! - Distance: {} - Intensity: {} - Time: {}'.format(lightning_distKm, lightning_energy_val, datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")))    
    #print('Distance: %dkm'%lightning_distKm)
    #print('Intensity: %d '%lightning_energy_val)
    
    message = {
      "message": 'Lightning occurs!',
      "distance": lightning_distKm,
      "intensity": lightning_energy_val,
      "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    }
    rabbitChannel.basic_publish(exchange='', routing_key='lightning_data', body=json.dumps(message))
  elif intSrc == 2:
    if hasNotDisturbed:
      print('Disturber discovered! - Time: {}'.format(datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")))
      hasNotDisturbed = False
    message = {
      "message": 'Disturber discovered!',
      "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    }
    rabbitChannel.basic_publish(exchange='', routing_key='lightning_data', body=json.dumps(message))
  elif intSrc == 3:
    print('Noise level too high!')
    message = {
      "message": 'Noise level too high!',
      "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    }
    rabbitChannel.basic_publish(exchange='', routing_key='lightning_data', body=json.dumps(message))
  else:
    pass
#Set to input mode

GPIO.setup(IRQ_PIN, GPIO.IN)
#Set the interrupt pin, the interrupt function, rising along the trigger
GPIO.add_event_detect(IRQ_PIN, GPIO.RISING, callback = callback_handle)
print("start lightning detect.")

while True:
  connection.process_data_events()
  print("sent heartbeat")
  time.sleep(1.0)


