from mkcloud import gatherScreenshots, resizeImages
from mkvideo import Video
import os
import shutil

#Coud helper is a class in charge of contain functions that are only relevant to the server,
#and we may not include it on the public executor version
class CloudHelper:
  def __init__(self,organizationId,executionNumber):
    #Remove logs directory and create a new one
      if os.path.exists("logs"):
        shutil.rmtree('logs')
      os.mkdir("logs")
      self.organizationId = organizationId
      self.executionNumber = executionNumber
      self.videoNameFile = str(organizationId) + "_" + str(executionNumber) + ".mp4"
  
  @staticmethod
  def getCloudKey(self):
    return('lkussv97qginpidrtoey-1ec3r3678pe7n0wulh1v9k-zthz8er1ukl59ux1k0epop-mioxpeadsu5iegbjhd4j4')

  def uploadLogs(self,dirname, dest):
    try:
      logPath=dirname+'/logs/'
      if os.path.exists(dirname + '/logs/chrome.log'):
        os.rename(logPath+'chrome.log', logPath+str(self.organizationId) + '_' + str( self.executionNumber) + '.log')
        logFileName = logPath+ str(self.organizationId) + '_' + str( self.executionNumber) + '.log'
        logFile = open(logFileName, 'r')
        files = {'file' : logFile}
        shutil.copytree("logs/", dest+"/logs")

        requests.post( path = 'upload/' , headers=hed, data={'fileType': "logs"} , files=files)
    except Exception as e:
      print("Error on logs uploading")
      print(e)

  def backupVideo(self, dest):
     # internal cloud only
      files =  [f for f in os.listdir(".") if f.endswith('.mp4')]
      shutil.move(files[0], dest) if len(files) == 1 else print("Not a video to backup")
      #########

  def startRecording(self):
    try:
      # internal cloud only
      self.v = Video()
      self.v.checkAndStartRecording(videoNameFile)
    except Exception as e:
      print("Error during gradlew compilation and/or execution ")
      print(e)

  def stopRecording(self):
    self.v.checkAndStopRecording()
    del self.v
    videoFile = open(self.videoNameFile, 'rb')
    files = {'file': videoFile}
    requests.post(path='upload_video/', headers=hed, files=files)