import os
import platform
import json
import subprocess
import time

class Common:
  #This is intended to be a static variable to store the platform once it is retrieved
  osPlatform=""
  config = None 
  def __init__(self):
    pass
  
  @staticmethod
  def OSCheck():
    if(Common.osPlatform == ""):
      Common.osPlatform = platform.system()
    return Common.osPlatform
  
  

  
  @staticmethod
  def getJson(jsonValue):
    return json.loads(jsonValue)

  @staticmethod
  def readJsonFile(file):
    # read file
    with open(file, 'r') as myfile:
        data=myfile.read()
    # parse file
    obj = json.loads(data)
    print("usd: " + str(obj['env']))
    return obj

  @staticmethod
  def getConfig():
    #Just read the file if it was not readed previously
    if(Common.config==None):
      # read file
      with open("./config/config.json", 'r') as myfile:
          data=myfile.read()
      # parse file
      Common.config = json.loads(data) 
    return Common.config

  # This function issues the command via subprocess check_output which  returns
  # the  stdout.
  # params:
  #    command to issue (string)
  # returns:
  #    result which contains the stout (string)
  @staticmethod
  def executeCmd(cmd=""):
    result = ""
    if cmd != "" :
      try:
        result= subprocess.check_output(cmd, shell = True)
      except subprocess.CalledProcessError as notZero:
        print ("executeCmd - returned a non zero response , this means there was an error")
        result =""
      except Exception as e :
        print ("executeCmd - Execution returned ")
        result = ""
        print(e)
    else :
      print ("executeCmd - No command provided... Nothing to do")

    print("executeCmd - result: " , result)
    return result