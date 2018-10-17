import argparse
import shutil
import os
import subprocess
from urllib import request
import requests
import json

def run(args):
  #Gets the value from the flags
  field = args.field
  value = args.value
  route = 'src/test/groovy'

  allowed_fields = ['tag','name']
  if field in allowed_fields:
    #Delete the old files 
    if os.path.exists("example.rar"):
      os.remove('example.rar')
    shutil.rmtree(route, ignore_errors=True)
    if not os.path.exists(route):
      os.makedirs(route)

    # We get the id
    r = requests.post(url = 'http://localhost:8081/get_test_id_from_property/', data = {'property': field, 'value': value})
    resp = r.json()
    id = ''
    success = False
    message = ''
    for key, value in resp.items():
      if key == 'id':
        id = value
      if key == 'success':
        success = value
      if key == 'message':
        message = value

    if success:
      # Download the file
      url = "http://localhost:8081/download_script_bytest/"+id  
      response = request.urlopen(url)
      file = response.read()
      fileobj = open('example.rar',"wb")
      fileobj.write(file)
      fileobj.close()

      # Unzip the file
      shutil.unpack_archive('example.rar', extract_dir=route, format='zip')

      #Executes the test
      os.system('gradlew clean test')
    else:
      print(message)
  else:
    print(field+': is not an allowed property')

 


def main():
	parser=argparse.ArgumentParser(description="Convert a fastA file to a FastQ file")
	parser.add_argument("-p",help="property to search the test for" ,dest="field", type=str, required=True)
	parser.add_argument("-t",help="value of the test field" ,dest="value", type=str, required=True)
	parser.set_defaults(func=run)
	args=parser.parse_args()
	args.func(args)

if __name__=="__main__":
	main()

