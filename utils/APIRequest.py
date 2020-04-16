from mkcloud import gatherScreenshots, resizeImages
import json
from .RequestUtil import RequestUtil
import shutil
import os
import json
import urllib
import xml.etree.ElementTree

class APIRequest:

  def __init__(self):
    self.token = ""
    self.userId = ""
    self.organizationId = ""
    self.auth = {}
    self.requestUtil=RequestUtil("dev")


  def generateToken(self,key):
    r = self.requestUtil.httpRequest(path="generate_token_executer", data={'key': key},requestType="post")
    responseObject = json.loads(r.content)
    self.token = responseObject["token"]
    self.userId = responseObject["userId"]
    self.organizationId = responseObject["organizationId"]
    self.auth = {'Authorization': 'Bearer ' + self.token}

  def sendTrackingData(self,action):
    #save the dowonloaded test entry to the database
      payload = {
        "action": action,
        "userId": self.userId,
        "organizationId": self.organizationId,
        "options": {
          "executor": True
        }
      }
      try:
        # requests.post(supportRoute+"tracking_data", json=payload)
        self.requestUtil.httpRequest(path="tracking_data", json=payload,requestType="post",support=True)
      except Exception as e:
        print("No connection to support Data Base")
  
  def uploadImages(self,browserName=""):
    #CLOUD SCREENSHOTS STARTS #
    resizeImages(browserName)
    #cloudKey = getCloudKey()
    filesData = gatherScreenshots(browserName)
    try:
      if filesData != {}:
        # requests.post(muuktestRoute + 'upload_cloud_steps_images/', headers=hed, files = filesData)
        self.requestUtil.httpRequest(path='upload_cloud_steps_images/',
         data={'cloudKey': cloudKey}, headers=hed, files = filesData,requestType="post")
      else:
        print ("filesData empty.. cannot send screenshots")
    except Exception as e:
      print("Cannot send screenshots")
      print(e)

  def sendFeedback(self,browserName=None, executionNumber=None):
    testsExecuted = self.gatherFeedbackData(browserName)
    url = 'feedback/'
    values = {'tests': testsExecuted, 'userId': self.userId, 'browser': browserName,'executionNumber': executionNumber}
    try:
      #Executions feedback
      self.requestUtil.httpRequest(path=url, json=values, headers=self.auth,requestType="post")
      
    except Exception as e:
      print("Not connection to support Data Base")
      print(e)

  def downloadByProperty(self,values):
    # This route downloads the scripts by the property.
    url = 'download_byproperty/'  
    response = self.requestUtil.urllibRequest(path=url,headers=self.auth, values=values,token=self.token )
    return response
  
  def gatherFeedbackData(self,browserName):
    #The path will be relative to the browser used to execute the test (chromeTest/firefoxTest)
    path = 'build/test-results/'+browserName
  
    feedbackData = []
    if os.path.exists(path):
      for filename in os.listdir(path):
        testSuccess = True
        error = ''
        if filename.endswith('.xml'):
          e = xml.etree.ElementTree.parse('build/test-results/'+browserName+'/' + filename).getroot()
  
          if e.attrib['failures'] != "0" :
            testSuccess = False
  
          if testSuccess == False :
            if e.find('testcase') is not None :
              if e.find('testcase').find('failure') is not None :
                error = e.find('testcase').find('failure').attrib['message']
  
          testResult = {
            "className": e.attrib['name'] if e.attrib['name'] is not None else "",
            "success": testSuccess,
            "executionAt": e.attrib['timestamp'] if e.attrib['timestamp'] is not None else "",
            "hostname": e.attrib['hostname'] if e.attrib['hostname'] is not None else "",
            "executionTime": e.attrib['time'] if e.attrib['time'] is not None else "",
            "error":  error,
            "systemoutput":  e.find('system-out').text if e.find('system-out') is not None else ""
          }
          feedbackData.append(testResult)
    else:
      print("gatherFeedbackData - path does not exists ")
      testResult = {
        "success" : False,
        #"executionAt": "",
        "error" : "Test failed during execution. This could be compilation error",
        "compilationError" : True
      }
      feedbackData.append(testResult)
  
    return(feedbackData)