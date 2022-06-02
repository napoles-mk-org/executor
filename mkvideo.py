import os
import subprocess
import time

# This class comprise the methos to handle the recording of a video.
# It requires ffmpeg and tmux libraries to be running in the Linux box.
# Currently it only supports linux (ubuntu?)
class Video:
  # This is the constructor, input might change when we support windows (gdigrab/desktop)
  # or mac(avfoundation?) . Check https://www.ffmpeg.org/ffmpeg.html
  #
  # Keep in mind that the default port we have used is :99 , that is specified when
  # starting the Xvfb  process (ie. Xvfb :99  1366x768x16)
  # FYI  TMUX reference: https://gist.github.com/henrik/1967800
  #
  def __init__(self, port= ":99.0", dimension="1366x768", nameFile = "default.mp4", session = "Muukrecording", input ="x11grab"):
    self.port = port
    self.dimension = dimension
    self.nameFile = nameFile
    self.session = session
    self.input = input

  # this function should get the OS
  # def getOs():
  #   pass
  def setNameFile(self, nameFile):
    self.nameFile = nameFile

  # This function checks the libraries to be able to record the video.
  # returns:
  #    Boolean whether it satisfies or not.
  def checkLibraries (self):
    status = True

    cmds = ["tmux -V | grep tmux", "ffmpeg  -version | grep version"]
    notFoundStr = "command not found"
    for x in cmds :
      #print("Cmd: " , x)
      res = self.executeCmd(x)
      if res == "" or notFoundStr in str(res):
        print("checkLibraries - The library is not installed : " ,  x)
        status = False
        break

    return status

  # this function checks whether there is an active tmux session
  # This is important because we cannot start more than one session with
  # the same name.
  # returns:
  #    Boolean whether there is an active session  or not
  def checkActiveSession(self):
    status = False
    cmd = "tmux ls | grep " + self.session

    result = self.executeCmd(cmd)
    # Verify if there is an existing session
    if result != "" and self.session in str(result):
      print("checkActiveSession - There is an active sessions")
      status = True

    return status

  # this function starts the  tmux session. It does not check whether there is
  #  already an active session though
  # returns:
  #    Boolean whether there was able to start the session or not
  def startSession(self):
    status = True
    cmd = "tmux new-session -d -s "+self.session

    res = self.executeCmd(cmd)

    return status

  #This function kills a tmux active session. It assumes you have already
  # confirmed that there is an active session.
  # returns:
  #    Boolean whether there was able to kill the session or not
  def killSession(self):
    status = True
    cmd = "tmux kill-session -t "+self.session

    res = self.executeCmd(cmd)

    return status

  # This function starts the recording of the video in a new TMUX sessions.
  # which means that there should not be an  active session already. This
  # must be verified prior calling this function
  # Returns:
  #    Boolean whether there was able to start the recording
  def startRecording(self):
    status = True
    # The following command starts the recording creating a new TMUX session.
    # such session should not exist. All parameters are required and the -y
    # means that it will overwrite the file in case that exists.
    cmd = "tmux new-session -d -s "+ self.session +"  'ffmpeg -video_size "+ self.dimension + " -framerate 25 -f "+self.input + " -threads 4 -i "+self.port +" -y " + self.nameFile+"'"
    print("startRecoring - start the recording : " , cmd)

    resStr = self.executeCmd(cmd)
    # This means there was  an error...
    if resStr != "":
      status =  True
    else:
      status =  False
      print("startRecoring - There was an error starting the recording")

    return status

  # This function stops the recording of the video. Basically  it sends
  # the "q" key to the tmux terminal. This does  not mean that kills the tmux
  # session though
  # Returns:
  #    Boolean whether there was able to stop the recording
  def stopRecording(self):
    status = True
    cmd = "tmux send-keys -t "+self.session+ " q "
    print("stopRecording - start the recording : " , cmd)

    resStr = self.executeCmd(cmd)
    # This means there was  an error...
    if resStr != "":
      status =  True
    else:
      status =  False

    time.sleep(1)
    return status

  # This function issues the command via subprocess check_output which  returns
  # the  stdout.
  # params:
  #    command to issue (string)
  # returns:
  #    result which contains the stout (string)
  def executeCmd(self, cmd=""):
    result = ""
    if cmd != "" :
      try:
        print("executeCmd - command received: ", cmd)
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


  # this function starts the recording of the video in a safe way.
  # params:
  #   Name of the file (string)
  # returns
  #   Boolean
  def checkAndStartRecording(self, nameFile=""):
    status = True
    # only perform this function if we have the libraries....

    status = self.checkLibraries()
    if status == True:

      if nameFile != "":
        self.setNameFile(nameFile)

      status = self.checkActiveSession()
      # this means there is an existing active session, something must have happened
      # but we need to kill it before we continue
      if status == True:
        status = self.killSession()

      # ok, lets the fun begin...
      status = self.startRecording()
      if status == True:
        print("checkAndStartRercording - Recording started successfully")
      else:
        print("checkAndStartRercording - There was a failure during the recording")
    else:
      print("checkAndStartRercording - Libraries not installed... nothing to  do")

    return status

  # this function stops the recording of the video in a safe way
  # returns
  #   Boolean
  def checkAndStopRecording(self):
    status = True

    status = self.checkActiveSession()
    # this means there is an existing active session, something must have happened
    # but we need to kill it before we continue
    if status == True:
      status = self.stopRecording()
      if status == True:
        print("checkAndStopRercording - Recording stopped successfully")
      else:
        print("checkAndStopRercording - There was a failure during the recording")
    else:
      print("checkAndStopRercording - No active sessions... nothing to stop")

    return status

def startRecording():
  status = True

  return status
