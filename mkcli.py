import argparse
import shutil
import os
import subprocess
from urllib import request
import requests
import json
import urllib
import xml.etree.ElementTree
from time import strftime
from mkcloud import gatherScreenshots, resizeImages
#import ssl

def gatherFeedbackData(browserName):
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


def run(args):
  #Gets the value from the flags
  print("Starting process")
  field = args.field
  value = args.value
  noexec = args.noexec
  route = 'src/test/groovy'
  browser = args.browser
  dimensions = args.dimensions
  if dimensions is not None:
    checkDimensions = True
  else:
    checkDimensions = False

  executionNumber = None
  #Exit code to report at circleci
  exitCode = 1
  #Check if we received a browser and get the string for the gradlew task command
  browserName = getBrowserName(browser)
  muuktestRoute = 'https://portal.muuktest.com:8081/'
  supportRoute = 'https://testing.muuktest.com:8082/'


  #muuktestRoute = 'https://localhost:8081/'
  #supportRoute = 'https://localhost:8082/'



  dirname = os.path.dirname(__file__)
  if dirname == "":
    dirname = "."

  userId = ''
  if field == "hashtag":
    value = "#"+value

  valueArr = []
  valueArr.append(value)

  #Getting the bearer token
  path = dirname + '/key.pub'
  token=''
  try:
    key_file = open(path,'r')
    key = key_file.read()
    r = requests.post(muuktestRoute+"generate_token_executer", data={'key': key})
    #r = requests.post(muuktestRoute+"generate_token_executer", data={'key': key}, verify=False)
    responseObject = json.loads(r.content)
    token = responseObject["token"]
    userId = responseObject["userId"]
    organizationId = responseObject["organizationId"]
  except Exception as ex:
    print("Key file was not found on the repository (Download it from the Muuktest portal)")
    print (ex)
    exit(exitCode)

  auth = {'Authorization': 'Bearer ' + token}

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
    os.makedirs(route)

    values = {'property': field, 'value[]': valueArr, 'userId': userId}
    # Add screen dimension data if it is set as an argument
    if checkDimensions == True:
      resultExtractDimensions = extractDimensions(dimensions)
      if resultExtractDimensions['success'] == True:
        values['dimensions'] = resultExtractDimensions['dimensions']
      else:
        print("Dimensions error")
        exit(1)

    # This route downloads the scripts by the property.
    url = muuktestRoute+'download_byproperty/'
    #context = ssl._create_unverified_context()
    data = urllib.parse.urlencode(values, doseq=True).encode('UTF-8')

    #now using urlopen get the file and store it locally
    auth_request = request.Request(url,headers=auth, data=data)
    auth_request.add_header('Authorization', 'Bearer '+token)
    response = request.urlopen(auth_request)
    #response = request.urlopen(auth_request, context=context)

    #response = request.urlopen(url,data)
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

      #Unzip the file // the library needs the file to end in .rar for some reason
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

      os.system('chmod 544 ' + dirname + '/gradlew')

      #save the dowonloaded test entry to the database
      payload = {
        "action": 2,
        "userId": userId,
        "organizationId": organizationId,
        "options": {
          "executor": True
        }
      }

      try:
        requests.post(supportRoute+"tracking_data", json=payload)
        # equests.post(supportRoute+"tracking_data", json=payload, verify=False)
      except Exception as e:
        print("No connection to support Data Base")


      if noexec == False :
        #Execute the test
        print("Executing test...")
        try:
          exitCode = subprocess.call(dirname + '/gradlew clean '+browserName, shell=True)
        except Exception as e:
          print("Error during gradlew compilation and/or execution ")
          print(e)

        testsExecuted = gatherFeedbackData(browserName)
        url = muuktestRoute+'feedback/'
        values = {'tests': testsExecuted, 'userId': userId, 'browser': browserName,'executionNumber': int(executionNumber)}
        hed = {'Authorization': 'Bearer ' + token}

        #CLOUD SCREENSHOTS STARTS #
        resizeImages(browserName)
        #cloudKey = getCloudKey()
        filesData = gatherScreenshots(browserName)
        try:
          if filesData != {}:
            requests.post(muuktestRoute + 'upload_cloud_steps_images/', headers=hed, files = filesData)
            #requests.post(muuktestRoute + 'upload_cloud_steps_images/', data={'cloudKey': cloudKey}, headers=hed, files = filesData, verify=False)
          else:
            print ("filesData empty.. cannot send screenshots")
        except Exception as e:
          print("Cannot send screenshots")
          print(e)
        #CLOUD SCREENSHOTS ENDS
        try:
          #Executions feedback
          requests.post(url, json=values, headers=hed)
          #requests.post(url, json=values, headers=hed, verify=False)

          #save the executed test entry to the database
          requests.post(supportRoute+"tracking_data", data={
            'action': 3,
            'userId': userId,
            'organizationId': organizationId
          })
        except Exception as e:
          print("Not connection to support Data Base")
          print(e)
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

def extractDimensions(dimensions):
  dimensionsLength = len(dimensions)
  dimensionsArray = [0] * 2
  success = True
  if dimensionsLength > 0 and dimensionsLength <=2:
    if dimensionsLength == 1:
      if "x" in dimensions[0].lower():
        dimensionsSplitted = dimensions[0].lower().split("x")
        if len(dimensionsSplitted) == 2:
          if dimensionsSplitted[0].isdigit() and dimensionsSplitted[1].isdigit():
            dimensionsArray = convertDimensionsToArray(dimensionsSplitted[0], dimensionsSplitted[1])
          else:
            print("The values received cant be converted to numbers")
            success = False
        else:
          print("Dimension arguments must be equal to 2")
          success = False
      else:
        print("Dimensinos should be separated by 'x' or space. ex: 1200x900 or 1200 900")
        success = False
    if dimensionsLength == 2:
      if dimensions[0].isdigit() and dimensions[1].isdigit():
        dimensionsArray = convertDimensionsToArray(dimensions[0], dimensions[1])
      else:
        print("The values received cant be converted to numbers")
        success = False
  else:
    print("dimensions arguments may not be more than 2 or less than 0")
    success = False
  return {'success': success, 'dimensions': dimensionsArray}

def convertDimensionsToArray(width, height):
  dimensionArray = [0]*2
  try:
    dimensionArray[0] = int(width)
    dimensionArray[1] = int(height)
  except Exception as ex:
    print("Error on convertion ",ex)
  return dimensionArray

def main():
  parser=argparse.ArgumentParser(description="MuukTest cli to download tests from the cloud")
  parser.add_argument("-p",help="property to search the test for" ,dest="field", type=str, required=True)
  parser.add_argument("-t",help="value of the test or hashtag field" ,dest="value", type=str, required=True)
  parser.add_argument("-noexec",help="(Optional). If set then only download the scripts", dest="noexec", action="store_true")
  parser.add_argument("-browser",help="(Optional). Select one of the available browsers to run the test (default firefox)", type=str, dest="browser")
  parser.add_argument("-dimensions",help="(Optional). Dimensions to execute the tests, a pair of values for width and height, ex. -dimensions 900x600 OR -dimensions 900 600", type=str, nargs="*", dest="dimensions")
  parser.set_defaults(func=run)
  args=parser.parse_args()
  args.func(args)


if __name__=="__main__":
	main()
