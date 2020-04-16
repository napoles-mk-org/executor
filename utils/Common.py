import os
import platform
import json

class Common:
  #This is intended to be a static variable to store the platform once it is retrieved
  osPlatform=""
  def __init__(self):
    pass
  
  @staticmethod
  def OSCheck():
    if(Common.osPlatform == ""):
      Common.osPlatform = platform.system()
    return Common.osPlatform
  
  @staticmethod
  def logging(log):
    print(log)
  
  @staticmethod
  def executeCmd():
    pass
  
  @staticmethod
  def getJson(jsonValue):
    return json.loads(jsonValue)

