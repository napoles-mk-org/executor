import argparse
import shutil
import os
import subprocess
from urllib import request
import json
import urllib
import sys
import re

def checkRequirements():

    java_installed = False
    pip_installed = False
    requests_installed = False
    isUbuntu = False;

    platform = sys.platform

    if platform == "linux":
        os_version = os.uname().version
        if "Ubuntu" in os_version:
            isUbuntu = True;

    linkJava = 'https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html';

    # Verifying if java is installed
    try:
        java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT).decode('utf-8')
        match = re.findall('(((10|11)|1\\.8|1\\.9)([\\.+\\d+\\.*])*)', java_version.split('"')[1])
        if not match:
            if isUbuntu == True:
                while 1:
                    answer = input("Java 1.8 or newer. Do you want to update it? [Y/N]: ");
                    if ( answer == 'Y' or answer == 'N' or answer == 'y' or answer == 'n'):
                        if (answer == 'Y' or answer == 'y') :
                            os.system('sudo add-apt-repository ppa:webupd8team/java')
                            os.system('sudo apt update; sudo apt install oracle-java8-set-default');
                            out = os.system('java -version');
                            javac_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)

                            if "1.8" in javac_version:
                                java_installed = True
                            else:
                                print("We couldn't to update Java")
                        break
            else:
                print("Is empty")
        else:
            java_installed = True

    except Exception as e:
        if isUbuntu == True:
            while 1:
                answer = input("Java is not installed. Do you want to install it? [Y/N]: ");
                if ( answer == 'Y' or answer == 'N' or answer == 'y' or answer == 'n'):
                    if (answer == 'Y' or answer == 'y') :
                        os.system('sudo add-apt-repository ppa:webupd8team/java')
                        os.system('sudo apt update; sudo apt install oracle-java8-installer');
                        out = os.system('java -version');
                        if out == 0:
                            java_installed = True
                        else:
                            print("We couldn't to install Java")
                    break
        else:
            print("Java is not installed. Java can be downloaded in the next link:")
            print(linkJava)

    linkPip3 = "https://pip.pypa.io/en/stable/installing/"
    # Verifying if pip3 is installed
    try:
        pip_version = subprocess.check_output(['pip3', '--version'], stderr=subprocess.STDOUT)
        pip_installed = True
    except:
        if isUbuntu == True:
            while 1:
                answer =  input("Pip3 is not installed. Do you want to install it? [Y/N]: ")
                if ( answer == 'Y' or answer == 'N' or answer == 'y' or answer == 'n'):
                    if (answer == 'Y' or answer == 'y') :
                        os.system('sudo apt install python3-pip')
                        out = os.system('pip3 --version')
                        if out == 0:
                            pip_installed = True
                        else:
                            print("We couldn't to install Pip3")
                    break
        else:
            print("Pip3 is not installed. Pip3 can be downloaded in the next link:")
            print(linkPip3)


    linkRequests = "https://docs.python.org/3/installing/index.html"
    #Verify if the request module is installed
    if pip_installed:
        import pip
        reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
        installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
        if 'requests' in installed_packages:
            requests_installed = True
        else:
            if isUbuntu == True:
                while 1:
                    answer =  input("Pip3 is not installed. Do you want to install it? [Y/N]: ")
                    if ( answer == 'Y' or answer == 'N' or answer == 'y' or answer == 'n'):
                        if (answer == 'Y' or answer == 'y') :
                            os.system('sudo pip install requests')
                            out = os.system('pip3 --version')
                            if out == 0:
                                requests_installed = True
                            else:
                                print("We couldn't to install Pip3")
                        break
            else:
                print("Request Package is not installed. To know how to download it, go to the next link:")
                print(linkRequests)


    return java_installed and pip_installed and requests_installed


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
