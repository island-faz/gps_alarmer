import json
import pika
from shapely.geometry import Point, Polygon

class Alarmer:
 "Write doc here"

 def __init__(self, host, m_queue, area_file_path):
  self.error = False
  try:
   with open(area_file_path) as json_data:
    m_area = json.load(json_data)
    self.area = Polygon(m_area['coords']) # check if poly is a loop
  except FileNotFoundError: # Area data file not found exception
   self.report_error("file '" + area_file_path + "' not found")
  except json.decoder.JSONDecodeError: # Invalid Json area data exception
   self.report_error("Invalid Json data in file '" + area_file_path + "'")
  else: # No exception we try to connect
   self.connect(host, m_queue)

   
 def connect(self, host, m_queue):
  try:
   self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
   self.channel = self.connection.channel()
   self.channel.basic_consume(queue=m_queue, auto_ack=True, on_message_callback=self.callback)
  except pika.exceptions.ChannelClosedByBroker:
   self.report_error("Cannot connect to channel (queue) '" + m_queue + "'") # Wrong channel
  except:
   self.report_error("Cannot connect to '" + host + "'") # Wrong host

   
 def start(self):
  if (self.error == False):
   self.channel.start_consuming()
  else:
   self.report_error("Cannot start server, please check logs.")

   
 def callback(self, ch, method, properties, body):
  try:
   data = json.loads(body)
  except json.decoder.JSONDecodeError:
   self.report_error("Invalid Json data from broker")
  else:
   self.check_position(data) # Checking the position


 def check_position(self, data):
  try:
   #print(data['speed'])
   self.pos = Point(float(data['x']), float(data['y']))
  except:
   self.report_error("Invalid Json data from broker", False)
  else:
   if (self.pos.within(self.area) == False):
    self.report_out_area()
   else:
    print("In area")


 def report_out_area(self):
  print("Out of area")
   
   
 def report_error(self, error, error_is_bloking = True):
  self.error = error_is_blocking
  print("Error: " + error)
