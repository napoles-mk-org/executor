import requests
import urllib
from urllib import request
import ssl

class RequestUtil:
  prodRoute = 'https://portal.muuktest.com:8081/'
  prodSupportRoute = 'https://testing.muuktest.com:8082/'
  devRoute = 'https://localhost:8081/'
  devSupportRoute = 'https://localhost:8082/'

  def __init__(self, env):
    self.env = env
    if env == "prod": 
      self.route = self.prodRoute 
      self.supportRoute = self.prodSupportRoute 
    else: 
      self.route = self.devRoute
      self.supportRoute = self.devSupportRoute 
  
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

  


