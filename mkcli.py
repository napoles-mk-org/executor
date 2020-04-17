import argparse
import shutil
import os
import subprocess
import json
import xml.etree.ElementTree
from time import strftime
from utils.Common import Common
from utils.RequestUtil import RequestUtil
from utils.APIRequest import APIRequest


def run(args):
  

  #Gets the value from the flags
  config ={}
  try:
    config = Common.getConfig()
  except Exception as ex:
    print("There is not config file on /config/config.json ",ex)


  print("Starting process")
  field = args.field
  value = args.value
  noexec = args.noexec
  route = 'src/test/groovy'
  browser = args.browser
  executionNumber = None
  
  #This options will be available for server running:
  if(config["onCloud"]):
    from .CloudHelper import CloudHelper
    executionNumber = args.executionnumber or None
    cloudHelper=CloudHelper(executionNumber)
    
  dimensions = args.dimensions
  if dimensions is not None:
    checkDimensions = isinstance(dimensions[0], int) & isinstance(dimensions[1],int)
  else:
    checkDimensions = False

  #Exit code to report at circleci
  exitCode = 1
  #Check if we received a browser and get the string for the gradlew task command
  browserName = getBrowserName(browser)



  apiRequest=APIRequest()


  dirname = os.path.dirname(__file__)
  if dirname == "":
    dirname = "."

  userId = ''
  if field == "hashtag":
    value = "#"+value

  valueArr = []
  valueArr.append(value)

  # Getting the bearer token
  path = dirname + '/key.pub'
  token=''
  try:
    key_file = open(path,'r')
    key = key_file.read()
    apiRequest.generateToken(key)
     
  except Exception as ex:
    print("Key file was not found on the repository (Download it from the Muuktest portal)")
    print (ex)
    exit(exitCode)

  allowed_fields = ['tag','name', 'hashtag']
  if field in allowed_fields:
    print("Downloading test")
    #Delete the old files
    if os.path.exists("test.rar"):
      os.remove('test.rar')

    if os.path.exists(route):
      print("copy dir")
      folderName = strftime("%m_%d_%Y_%H_%M_%S")
      dest = "bckSrc/"+folderName
      print(dest)
      shutil.copytree(route, dest)
      shutil.copytree("build/", dest+"/build")
      shutil.rmtree(route, ignore_errors=True)
      if(config["onCloud"]):
        cloudHelper.backupVideo("bckSrc/"+folderName)
    os.makedirs(route)

    values = {'property': field, 'value[]': valueArr}
    # Add screen dimension data if it is set as an argument
    if checkDimensions == True:
      values['dimensions'] = [dimensions[0],dimensions[1]]

    response = apiRequest.downloadByProperty(values)

    # response = request.urlopen(url,data)
    file = response.read()
    flag = False

    try:
      decode_text = file.decode("utf-8")
      json_decode = json.loads(file.decode("utf-8"))
      print(json_decode["message"])
    except:
      flag = True

    if (flag == True):
      print("The test has been downloaded successfully")
      fileobj = open('test.zip',"wb")
      fileobj.write(file)
      fileobj.close()

      # Unzip the file // the library needs the file to end in .rar for some reason
      shutil.unpack_archive('test.zip', extract_dir=route, format='zip')

      if os.path.exists("src/test/groovy/executionNumber.execution"):
        try:
          execFile = open('src/test/groovy/executionNumber.execution', 'r')
          executionNumber = execFile.read()
        except Exception as e:
          print("Cannot read executionNumber file")
          print(e)
      else:
        print("executionNumber.execution file not found")


      apiRequest.sendTrackingData(2)

      if noexec == False :
        #Execute the test
        if(config["onCloud"]):
          cloudHelper.startRecording()
        
        try:
          print("Executing test...")
          exitCode = executeTest(dirname=dirname,browserName=browserName)
        except Exception as e:
          print("Error during gradlew compilation and/or execution ")
          print(e)
          
        if(config["onCloud"]):
          cloudHelper.stopRecording()

        apiRequest.uploadImages(browserName=browserName)
        apiRequest.sendFeedback(browserName=browserName,executionNumber=executionNumber)
        apiRequest.sendTrackingData(3)
        if(config["onCloud"]):
          cloudHelper.uploadLogs(dirname,executionNumber,dest)
  else:
    print(field+': is not an allowed property')

  print("exiting script with exitcode: " + str(exitCode))
  exit(exitCode)

#function that returns the task command for a browser if supported
#parameters
# browser: browsername
#returns
# a String to be used on gradlew task
def getBrowserName(browser):
  switcher = {
    "chrome":"chromeTest",
    "firefox": "firefoxTest"
  }
  #select a browser from the list or return firefox as default
  return switcher.get(browser,"firefoxTest")

def executeTest(dirname="", browserName="chromeTest"):
  exitCode=1
  platform = Common.OSCheck()
  slash="/"
  if(platform=="Linux" or platform=="MacOS" or platform=="Darwin"):
    os.system('chmod 544 ' + dirname + '/gradlew')
  if(platform=="Windows"):
    slash="\\"

  try:
    exitCode = subprocess.call(dirname + slash+'gradlew clean '+browserName, shell=True)
  except Exception as e:
    print("Error during gradlew compilation and/or execution ")
    print(e)
  return exitCode


def main():
  parser=argparse.ArgumentParser(description="MuukTest cli to download tests from the cloud")
  parser.add_argument("-p",help="property to search the test for" ,dest="field", type=str, required=True)
  parser.add_argument("-t",help="value of the test or hashtag field" ,dest="value", type=str, required=True)
  parser.add_argument("-noexec",help="(Optional). If set then only download the scripts", dest="noexec", action="store_true")
  parser.add_argument("-browser",help="(Optional). Select one of the available browsers to run the test (default firefox)", type=str, dest="browser")
  parser.add_argument("-dimensions",help="(Optional). Dimensions to execute the tests, a pair of values for width height, ex. -dimensions 1800 300", type=int, nargs=2, dest="dimensions")
  parser.set_defaults(func=run)
  args=parser.parse_args()
  args.func(args)


if __name__=="__main__":
	main()

