import argparse
import shutil
import os
import subprocess
from urllib import request
import json
import urllib
import sys
import re

def run(args):
  #Gets the value from the flags
  print("Starting process")
  requirements = checkRequirements()

  if requirements == True:
    import requests

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
    valueArr.append("")

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

      #Delete the old files
      if os.path.exists("test.rar"):
        os.remove('test.rar')

      shutil.rmtree(route, ignore_errors=True)

      if not os.path.exists(route):
        os.makedirs(route)

      values = {'property': field, 'value': valueArr, 'userId': userId}

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

        # save the downloaded test entry to the database
        payload = {
          "action": 2,
          "userId": userId,
          "organizationId": organizationId,
          "options": {
            "executor": True
          }
        }

        requests.post(supportRoute+"tracking_data", json=payload)

        if noexec == False :
          #Execute the test
          print("Executing test...")
          os.system(dirname + '/gradlew clean test')
          # save the execute test entry to the database
          requests.post(supportRoute+"tracking_data", data={
            'action': 3,
            'userId': userId,
            'organizationId': organizationId
          })

    else:
      print(field+': is not an allowed property')

  else:
    print("There are not all the requirements to run the executor")
    exit()


def checkPyModule(module):
  # Checking if the module is installed
  import pip
  # Retrieving if the mpython modules installed list
  reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
  installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

  # Check if the module is in the list
  if module["name"] in installed_packages:
    m_installed = True
  else:
    m_installed = False

  return m_installed

# This function install or update the programs or pymodules
# The parameter element is the json with the info of the program or pymodules
# The parameter action is to determinate if we need to install or update
def installAndUpdate(element, action):
  success = False
  #We need to know if the os is Ubuntu
  if sys.platform == "linux":
    os_version = os.uname().version
    if "Ubuntu" in os_version:
      isUbuntu = True;

  name = element["name"]

  #We need to check if is program or pymodule
  if element["type"] == "program":
    # We need to check the action to determinate which cmd to use
    if action == "update":
      cmd = element["update_cmd"]
      question = "You have a older " + name + "version. Do you want to update it? [Y/N]: "
    else:
      cmd = element["install_cmd"]
      question = name + " is not installed. Do you want to install it? [Y/N]: "
  else:
    cmd = "sudo pip install " + name
    question = name + " is not installed. Do you want to install it? [Y/N]: "


  if isUbuntu:
    while 1:
      answer = input(question)
      # Asking to the user if he wants to install or update it
      if ( answer == 'Y' or answer == 'N' or answer == 'y' or answer == 'n'):
        if (answer == 'Y' or answer == 'y') :
          # Installing or updating
          os.system(cmd)
          if action == "update":
            split_cmd = element["version_cmd"].split(" ")
            v = subprocess.check_output(split_cmd, stderr=subprocess.STDOUT).decode('utf-8')

            if element["minimum_version"] in v:
              success = True

          else:
            out = -1

            if element["type"] == "pymodule":
              if checkPyModule(element):
                out = 0
            else:
              out = os.system(element["version_cmd"])

            if out == 0:
              success = True

        break

  else:
    # If the OS is not Ubuntu, we send the link with the info to download it
    print(name + " is not installed. It can be downloaded in the next link:")
    if x["type"] == "pymodule":
      print("https://docs.python.org/3/installing/index.html")
    else:
      print(element["link"])

  return success

# Check if the programs or modules need to install or update
# This function recieve a list of programs or pymodules to install
def checkAndInstall(list):
  pip3_installed = False
  result = True

  for x in list:
    if x["type"] == "pymodule" and pip3_installed:
      installed = checkPyModule(x)
    else:
      try:
        splitcmd = x["version_cmd"].split(" ")
        # Getting the output of the command
        version = subprocess.check_output(splitcmd, stderr=subprocess.STDOUT).decode('utf-8')
        installed = True
      except Exception as e:
        # If it catch an exception the program doesn't exist
        installed = False

    if installed:
      if "minimum_version" in x:
        # If the programs is installed, we need to check his version
        match = re.findall(x["regex"], version.split('"')[1])
        if not match:
          # If it doesn't find a match, we need to update it
          installed = installAndUpdate(x, "update")
      else:
        if "Pip3" == x["name"]:
          pip3_installed = True
    else:
      # If it isn't installed, we need to install
      installed = installAndUpdate(x, "install")

    result &= installed

  return result


def checkRequirements():
  # Array of jsons, this contains the info of the programs or pymodules to install
  programs = [
    {
      "name": "Java",
      "version_cmd": "java -version",
      "install_cmd": "sudo add-apt-repository ppa:webupd8team/java; sudo apt update; sudo apt install oracle-java8-installer",
      "update_cmd": "sudo add-apt-repository ppa:webupd8team/java; sudo apt update; sudo apt install oracle-java8-set-default",
      "link": "https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html",
      "minimum_version": "1.8",
      "regex": "(((10|11)|1\\.8|1\\.9)([\\.+\\d+\\.*])*)",
      "type": "program"
    },
    {
      "name": "Pip3",
      "version_cmd": "pip3 --version",
      "install_cmd": "sudo apt install python3-pip",
      "link": "https://pip.pypa.io/en/stable/installing/",
      "type":"program"
    },
    {
      "name": "requests",
      "type": "pymodule"
    }
  ]

  # Check if the programs are install
  check_reqs = checkAndInstall(programs)

  return check_reqs

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
