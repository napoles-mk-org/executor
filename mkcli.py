import argparse
import shutil
import os
import subprocess
from urllib import request
import requests
import json
import urllib
import xml.etree.ElementTree

def sendFeedback():
  path = 'build/test-results/chromeTest'
  testSuccess = True
  error = ''
  feedbackData = []
  for filename in os.listdir(path):
    if filename.endswith('.xml'): 
      e = xml.etree.ElementTree.parse('build/test-results/chromeTest/' + filename).getroot()

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

  print(feedbackData)


def run(args):
  #Gets the value from the flags
  print("Starting process")
  field = args.field
  value = args.value
  noexec = args.noexec
  route = 'src/test/groovy'
  # muuktestRoute = 'http://ec2-3-17-71-29.us-east-2.compute.amazonaws.com:8081/'
  # supportRoute = 'http://ec2-18-219-8-121.us-east-2.compute.amazonaws.com:8082/'

  muuktestRoute = 'http://localhost:8081/'
  supportRoute = 'http://localhost:8082/'


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
    r = requests.post(muuktestRoute+"generate_token_executer", data={'key': key})
    responseObject = json.loads(r.content)
    token = responseObject["token"]
    userId = responseObject["userId"]
    organizationId = responseObject["organizationId"]
  except:
    print("Key file was not found on the repository (Download it from the Muuktest portal)")
    exit()

  auth = {'Authorization': 'Bearer ' + token}

  allowed_fields = ['tag','name', 'hashtag']
  if field in allowed_fields:
    print("Downloading test")
    # #Delete the old files
    if os.path.exists("test.rar"):
      os.remove('test.rar')
    shutil.rmtree(route, ignore_errors=True)
    if not os.path.exists(route):
      os.makedirs(route)

    values = {'property': field, 'value[]': valueArr, 'userId': userId}
    # This route downloads the scripts by the property.
    url = muuktestRoute+'download_byproperty/'
    data = urllib.parse.urlencode(values, doseq=True).encode('UTF-8')

    # now using urlopen get the file and store it locally
    auth_request = request.Request(url,headers=auth, data=data)
    auth_request.add_header('Authorization', 'Bearer '+token)
    response = request.urlopen(auth_request)

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

        os.system('chmod 544 ' + dirname + '/gradlew')
        
        # save the dowonloaded test entry to the database
        payload = {
          "action": 2, 
          "userId": userId, 
          "organizationId": organizationId,
          "options": {
            "executor": True
          }
        }
        # requests.post(supportRoute+"tracking_data", json=payload)

        if noexec == False :
          #Execute the test
          print("Executing test...")
          os.system(dirname + '/gradlew clean test')
          sendFeedback()
           # save the executed test entry to the database
          # requests.post(supportRoute+"tracking_data", data={
          #   'action': 3, 
          #   'userId': userId, 
          #   'organizationId': organizationId
          # })

  else:
    print(field+': is not an allowed property')




def main():
    parser=argparse.ArgumentParser(description="MuukTest cli to download tests from the cloud")
    parser.add_argument("-p",help="property to search the test for" ,dest="field", type=str, required=True)
    parser.add_argument("-t",help="value of the test or hashtag field" ,dest="value", type=str, required=True)
    parser.add_argument("-noexec",help="(Optional). If set then only download the scripts", dest="noexec", action="store_true")
    parser.set_defaults(func=run)
    args=parser.parse_args()
    args.func(args)

if __name__=="__main__":
	main()


