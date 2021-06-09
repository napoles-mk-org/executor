
import os
import json
import pprint
from bs4 import BeautifulSoup

def parseImageSelector(selectors, expectedValue, expectedIndex):
   jsonObject = {}
   elements = []
   index = 0
   for selector in selectors:
      if(selector['src'] == expectedValue and expectedIndex == index):
         element = {}
         element["index"] = index
         element["value"] = selector['src']
         element["expectedSelector"] = "true"
         elements.append(element)
      index+=1   

   # If the correct selector was not found, we need to return the selector that we think was selected
   # using the index from the object. 
   if(len(elements) == 0 and expectedIndex <= len(selectors)):
      selector = selectors[expectedIndex]
      if(selector):
         element = {}
         element["index"] = expectedIndex
         element["value"] = selector['src']
         element["expectedSelector"] = "false"
         elements.append(element)
         
   jsonObject["selectors"] = elements
   return jsonObject

def parseHypertextSelector(selectors, expectedValue, expectedIndex):
   
   jsonObject = {}
   elements = []
   index = 0
   for selector in selectors:
      if(selector and ("href" in selector)):
         if(selector['href'] == expectedValue and expectedIndex == index):
            element = {}
            element["index"] = index
            element["value"] = selector['href']
            element["expectedSelector"] = "true"
            elements.append(element)   
      index+=1   

   # If the correct selector was not found, we need to return the selector that we think was selected
   # using the index from the object. 
      # If the correct selector was not found, we need to return the selector that we think was selected
   # using the index from the object. 
   if(len(elements) == 0 and expectedIndex <= len(selectors)):
      selector = selectors[expectedIndex]
      if(selector):
         element = {}
         element["index"] = expectedIndex
         if("href" in selector):
            element["value"] = selector['href']
            element["expectedSelector"] = "false"
         else:
            element["value"] = expectedValue 
            element["expectedSelector"] = "true" 
         elements.append(element) 
      
   jsonObject["selectors"] = elements
   return jsonObject

def parseTextSelector(selectors, expectedValue, expectedIndex):
   jsonObject = {}
   elements = []
   index = 0
   for selector in selectors:
      if((selector.text).strip() == expectedValue.strip() and expectedIndex == index ):
         element = {}
         element["index"] = index
         element["value"] = selector.text
         element["expectedSelector"] = "true"
         elements.append(element)
      index+=1   
   
   # If the correct selector was not found, we need to return the selector that we think was selected
   # using the index from the object. 
   if(len(elements) == 0 and expectedIndex <= len(selectors)):
      selector = selectors[expectedIndex]
      if(selector):
         element = {}
         element["index"] = expectedIndex
         element["value"] = selector.text
         element["expectedSelector"] = "false"
         elements.append(element) 

   jsonObject["selectors"] = elements
   return jsonObject

def parseValueSelector(selectors, expectedValue, expectedIndex, type):
   jsonObject = {}
   elements = []
   index = 0

   for selector in selectors:
      if(selector['value'] == expectedValue and expectedIndex <= len(selectors)):
         element = {}
         element["index"] = index
         element["value"] = expectedValue
         element["expectedSelector"] = "true"
         elements.append(element)
      index+=1   

   # If the correct selector was not found, we need to return the selector that we think was selected
   # using the index from the object. 
   if(len(elements) == 0 and expectedIndex <= len(selectors)):
      selector = selectors[expectedIndex]
      if(selector):
         element = {}
         element["index"] = expectedIndex
         element["value"] = expectedValue
         element["expectedSelector"] = "false"
         elements.append(element) 

   jsonObject["selectors"] = elements
   return jsonObject

def obtainFeedbackFromDOM(classname, stepId, ntagselector, value, index, tag, type, action, searchType):
   jsonObject = {}
   elements = []    
   path = 'build/reports/geb/firefoxTest/'
   filename = path + classname + "_" + str(stepId) + ".html"
   if os.path.exists(filename):
      try:
         print("\n============= Step " + str(stepId) + "=============")
         print("Tag " + tag)
         print("Search by " + searchType)
         print("index " + str(index))
         print("action " + str(action))
         
         if(action == "assignment" or action == "mouseover"):
            jsonObject["selectors"] = []
            numberSelectorsFound = 0
         else:  
            text = open(filename, 'r').read()
            soup = BeautifulSoup(text, 'html.parser')
            selectorsFound = soup.select(ntagselector)
            numberSelectorsFound = len(selectorsFound)
            print("Selectors found: " + str(numberSelectorsFound))
            if(numberSelectorsFound == 0 ):
               jsonObject["selectors"] = []
            elif(numberSelectorsFound > 1 ):
               if(searchType == "value"):
                  jsonObject = parseValueSelector(selectorsFound, value, index, type)
               elif(searchType == "href"):
                  jsonObject = parseHypertextSelector(selectorsFound, value, index)
               elif(searchType == "text"):
                  jsonObject = parseTextSelector(selectorsFound, value, index)
               elif(searchType == "imgsrc"):
                  jsonObject = parseImageSelector(selectorsFound, value, index)
               else:
                  # Backend sent an undef searchType, we will return no info
                  jsonObject["selectors"] = []
                  numberSelectorsFound = 0
            elif(numberSelectorsFound == 1 ):
               element = {}
               element["index"] = index
               element["value"] = value
               element["expectedSelector"] = "true"
               elements.append(element)
               jsonObject["selectors"] = elements

         jsonObject["numberOfElementsWithSameSelector"] = len(jsonObject["selectors"])
         pprint.pprint(jsonObject)
         print("==============================================")  
      except Exception as ex:
         print("Failed to open file " + ex)
         print (ex)
   
   return jsonObject


def createMuukReport(classname):
   print("createMuukReport")
   path = 'build/reports/'
   filename = path + classname + ".json"
   muukReport = {}
   steps = []
   if(os.path.exists(filename)):
      try:
        jsonFile = open(filename, 'r')
        elements = json.load(jsonFile)
        index = 0
        for element in elements['stepsFeedback']:
          valueData = json.loads(element.get("value"))
          domInfo = obtainFeedbackFromDOM(classname, element.get("id"), 
                                          element.get("selector"), valueData["value"], 
                                          element.get("index"), element.get("tag"),
                                          element.get("objectType"),
                                          element.get("action"),
                                          valueData["searchType"])
          if(domInfo):                                
            element["numberOfElementsWithSameSelector"] = domInfo["numberOfElementsWithSameSelector"]
            element["selectors"] = domInfo["selectors"]
            steps.append(element)

      except Exception as ex:
          print("Exception found during DOM parsing. Exception = " + str(ex))     
      
      # Closing file
      jsonFile.close()

   muukReport["steps"] = steps
   print("createMuukReport - exit ")
   pprint.pprint(steps)

   return muukReport

#createMuukReport("muuktestElorusCom593c0d63") 
