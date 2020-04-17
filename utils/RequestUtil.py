import requests
import urllib
from urllib import request
import ssl
from .Common import Common

class RequestUtil:

  def __init__(self):
    conf = Common.getConfig() 
    self.env = conf["env"]
    if self.env == "prod": 
      self.route = conf["prod"]["route"] 
      self.supportRoute = conf["prod"]["supportRoute"]
    else: 
      self.route = conf["dev"]["route"] 
      self.supportRoute = conf["dev"]["supportRoute"]
  
  def urllibRequest(self,url=None,path=None, headers=None,values=None,  json=None,token=None):
    context=None
    requestParams={}
    rUrl=""
    if self.env!="prod": context=ssl._create_unverified_context()
    if headers: requestParams["headers"]=headers
    if json: requestParams["json"]=json
    #If we receive a path, we would use the already defined route, 
    #but it can be overrided if receive a full rout on url param
    if path: rUrl=self.route+path
    if url: rUrl=url
    
    data = urllib.parse.urlencode(values, doseq=True).encode('UTF-8')
    auth_request = request.Request(rUrl,**requestParams , data=data)
    auth_request.add_header('Authorization', 'Bearer '+token)
    response = request.urlopen(auth_request, context=context)
    return response

  def httpRequest(self,path=None,url=None, json=None,headers=None,data=None,files=None,support=False,requestType="get"):
    print("Starting request")
    requestParams={}
    if headers: requestParams["headers"]=headers
    if json: requestParams["json"]=json
    if data: requestParams["data"]=data

    #If we receive a path, we will use the already defined route, 
    #but it can be overrided if receive a full route on url param
    if path: 
      if(support):
        requestParams["url"]=self.supportRoute+path
      else:
        requestParams["url"]=self.route+path
    if url: requestParams["url"]=url

    if self.env!="prod": requestParams["verify"]=False
    if files: requestParams["files"]=files
    result = None
    if(requestType=="get"):
      result = requests.get(**requestParams)
    if(requestType=="post"):
      result = requests.post(**requestParams)
    print("Request finished ",result)
    return result

  


