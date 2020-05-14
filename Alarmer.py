import json
import pika
from shapely.geometry import Point, Polygon

class Alarmer:
 "Write doc here"
 # declare class variables
 
 def __init__(self, host, m_queue, area_file_path):
  self.error = False
  try:
   with open(area_file_path) as json_data:
    m_area = json.load(json_data)
    self.area = Polygon(m_area['coords']) # check if poly is a loop and if data is valid
  except FileNotFoundError:
   self.__report_error("file '" + area_file_path + "' not found")
  except json.decoder.JSONDecodeError:
   self.__report_error("Invalid Json data in file '" + area_file_path + "'")
  # add except:
  else: # No exception we try to connect
   self.__connect(host, m_queue)

   
 def __connect(self, host, m_queue):
  try:
   self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
   self.channel = self.connection.channel()
   self.channel.basic_consume(queue=m_queue, auto_ack=True, on_message_callback=self.__callback)
  except pika.exceptions.ChannelClosedByBroker:
   self.__report_error("Cannot connect to channel (queue) '" + m_queue + "'") # Wrong channel
  except:
   self.__report_error("Cannot connect to '" + host + "'") # Wrong host

   
 def start(self):
  if (self.error == False):
   self.channel.start_consuming()
  else:
   self.__report_error("Cannot start server, please check logs.")

   
 def __callback(self, ch, method, properties, body):
  try:
   data = json.loads(body)
  except json.decoder.JSONDecodeError:
   self.__report_error("Invalid Json data from broker")
  else:
   self.__check_position(data) # Checking the position


 def __check_position(self, data):
  try:
   #print(data['speed'])
   self.pos = Point(float(data['x']), float(data['y']))
  except:
   self.__report_error("Invalid Json data from broker", False)
  else:
   if (self.pos.within(self.area) == False):
    self.__report_out_area()
   else:
    print("In area")


 def __report_out_area(self):
  print("Out of area")


 def __report_speed_exceeded(self):
  print("Speed exceeded")


 def __report_error(self, error, error_is_bloking = True):
  self.error = error_is_blocking
  print("Error: " + error)
