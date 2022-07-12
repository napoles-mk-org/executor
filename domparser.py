
import os
import json
import pprint
from bs4 import BeautifulSoup
from CSSAnalyzer import obtainCSSFeedbackFromDOM
from XPATHAnalyzer import obtainXPATHFeedbackFromDOM
import traceback
import logging
import shutil
import pathlib


CLASSIC_SELECTOR    = 0
DYMANIC_SELECTOR    = 1
CUSTOM_CSS_SELECTOR = 2
XPATH_SELECTOR      = 3

SELECTORS_ARRAY =  [CLASSIC_SELECTOR, DYMANIC_SELECTOR, CUSTOM_CSS_SELECTOR, XPATH_SELECTOR ]
LOG_FILE_NAME = "DOMParser.log"

logging.basicConfig(filename = LOG_FILE_NAME,
                    filemode = "w",
                    format = "%(levelname)s %(asctime)s - %(message)s", 
                    level = logging.INFO)
logger = logging.getLogger(__name__)


# Description:
#   This method will be call to execuete the Muuk Report analysis.  
#   for the test to find the selectors for this step. If more than one selector is found,  
#   this method makes another search on the DOM using the value to filter the 
#   selectors found. 
#
# Returns:
#    jsonObject with the number of selector information. 
def createMuukReport(classname, browserName):
   logging.info("Starting parsing analysis")
   path = 'build/reports/'
   filename = path + classname + ".json"
   muukReport = {}
   steps = []
   if(os.path.exists(filename)):
      try:
        jsonFile = open(filename, 'r')
        elements = json.load(jsonFile)
        for element in elements['stepsFeedback']:
         type = element.get("type")
         if(type == "step"):
            element["feedback"] = []
            selectors =  json.loads(element.get("selectors").replace('\$', '\\\$'))
            selectorToUse = element.get("selectorToUse")
            
            try: 
               valueInfo = json.loads(element.get("value"))
            except Exception as ex:
               valueInfo = {"value":"","":"href","":""}

            try: 
               attributes = json.loads(element.get("attributes"))
            except Exception as ex:
               attributes = {"id":"false","name":"undef","text":"","type":"undef"}

            attributes['value'] = valueInfo['value']

            for i in SELECTORS_ARRAY:
               
               if(i < len(selectors)):
                 selector = selectors[i]['selector']
                 if(selector == ""):
                    selector = None
                 index = selectors[i]['index']
               else:
                 selector = None
                 index = None
               
               if(i < 3):
                  domInfo = obtainCSSFeedbackFromDOM(classname, element.get("id"), 
                                             selector, 
                                                index,
                                                element.get("tag"),
                                                element.get("objectType"), element.get("action"), 
                                                valueInfo,
                                                browserName,
                                                attributes,
                                                SELECTORS_ARRAY[i])
               else:
                  if(selector != None):
                    # XPATH library is case sensitive and MuukTest creates the tag as upper case, we need to fix this. 
                    selector = selector.replace(element.get("tag").upper(), element.get("tag"), 1)
                  domInfo = obtainXPATHFeedbackFromDOM(classname, element.get("id"), 
                                                selector, 
                                                index,
                                                element.get("tag"),
                                                element.get("objectType"), element.get("action"), 
                                                valueInfo,
                                                browserName,
                                                attributes,
                                                SELECTORS_ARRAY[i])                               
               

               try:
                  logging.info("Object  = " + json.dumps(domInfo,sort_keys=True, indent=4))
               except Exception as ex: 
                  logging.error("Invalid domInfo generated") 

               if(domInfo):                                
                  element["feedback"].append(domInfo)
            steps.append(element)  

            # Now that we have the 4 selector arrays, let's define which one we should use
            selectorToUse = findBetterSelectorToUse(element["feedback"], attributes)
            element["feebackSelectorToUse"] = selectorToUse

         else:
            steps.append(element)     

      except Exception as ex:
          logging.error("Exception found during DOM parsing. Exception = ")
          logging.error(ex) 
          logging.error(traceback.format_exc())    
      
      # Closing file
      jsonFile.close()
   else:
      logging.error("Muuk Report was not found!")   
   
   # Let's validate the data we generated is a valid json
   try:
     json.loads(json.dumps(steps)) 
     muukReport["steps"] = steps
   except Exception as ex: 
     logging.error("Invalid JSON format was found, will not send feedback to BE")
     logging.error(ex) 
     logging.error(traceback.format_exc())    
     muukReport["steps"] = {}

   # Print report if touch file exists 
   if(os.path.exists("TOUCH_TRACE_REPORT")):
     pprint.pprint((muukReport["steps"]))

   logging.info("Final Feedback Object:")
   logging.info(json.dumps(muukReport["steps"],sort_keys=True, indent=4))

   # Last step is to copy the log file to build folder
   try:
      source = str(pathlib.Path(__file__).parent.resolve()) + "/" + LOG_FILE_NAME
      destination = str(pathlib.Path(__file__).parent.resolve()) + "/build/" +LOG_FILE_NAME; 
      shutil.copyfile(source, destination)
   except Exception as ex: 
      print(ex) 

   return muukReport

#  if the Object has text, we will use XPATH selector. 
#  else if Object has the next attributes ['id', 'name', 'type', 'role', 'title'], use custom CSS
#  else if ntagselector has dynamic classes, use dynamic selector
#  else use clasic selector.
def findBetterSelectorToUse(selectors, attributes):

   selectorToUse = -1
   classic = selectors[0] if len(selectors) > 0 else []
   dynamic = selectors[1] if len(selectors) > 1 else []
   customeCSS = selectors[2] if len(selectors) > 2 else []
   xpath = selectors[3] if len(selectors) > 3 else []
   
   if(xpath and xpath["numberOfElementsFoundWithSelectorAndValue"] > 0 and attributes["text"] != "undef" and 
      ("contains" in xpath["selectors"]["selector"] or "normalize-space" in xpath["selectors"]["selector"] )):
      selectorToUse = 3
   elif(customeCSS and (attributes["id"] != "undef" or attributes["name"]  != "undef" or attributes["type"]  != "undef" ) and customeCSS["numberOfElementsFoundWithSelectorAndValue"] > 0):
      selectorToUse = 2
   elif(classic and classic["numberOfElementsFoundWithSelectorAndValue"] > 0):
      selectorToUse = 0   
   elif(dynamic and dynamic["numberOfElementsFoundWithSelectorAndValue"] > 0):
      selectorToUse = 1   

   # If we were not able to choose a selector with values, check if we have one that return any element at least.
   if(selectorToUse == -1):
      if(classic and classic["numberOfElementsFoundWithSelector"] > 0):
         selectorToUse = 0
      elif(dynamic and dynamic["numberOfElementsFoundWithSelectorAndValue"] > 0):
         selectorToUse = 1

   return selectorToUse
   
