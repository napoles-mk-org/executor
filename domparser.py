
import os
import json
import pprint
from bs4 import BeautifulSoup

UNKNOWN_ERROR = 1 
NO_TAG_PROVIDED_BY_BE = 2
NO_VALUE_PROVIDED_BY_BE = 3
NO_SEARCH_TYPE_PROVIDED_BY_BE = 4
ACTION_NOT_VALID_FOR_ANALYSIS = 5
STEP_INDEX_GREATER_THAN_NUMBER_OF_SELECTORS_FOUND = 6
ONE_SELECTOR_FOUND_FOR_NTAGSELECTOR = 7
NO_SELECTOR_FOUND_WITH_SPECIFIC_VALUE = 8  
SELECTOR_FOUND_WITH_CORRECT_INDEX = 9
SELECTOR_FOUND_WITH_INCORRECT_INDEX = 10  
MULTIPLE_SELECTORS_FOUND_WITH_EXPECTED_VALUE_CORRECT_INDEX = 11 
MULTIPLE_SELECTORS_FOUND_WITH_EXPECTED_VALUE_INCORRECT_INDEX = 12


def processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, attribute):
   jsonObject = {}
   elements = []

   # After we filter the selectors we have 3 options:
   # 1) No selectors were found having the value we are expecting. On this case,
   #    information returned will be the element with the index that was expected.
   #
   # 2) We found only one selector, we have two options here:
   #    a) Found the correct selector: Return the original element.
   #    b) Found the incorrect selector. Return two elements, one with the original index and other with the found index.
   # 
   # 3) We found two or more selectors with the same src. We have two options here:
   #    a) The correct selector was found. Return the original element. 
   #    b) The correct selector was not found. Return two elements, one with the original index and other with all the indexes found.
   #    
   if(selectorsFound == 0):
      print("No selectors were found with the expected src!!!")
      element = {}
      element["index"] = expectedIndex
      if(attribute == "text"):
         element["value"] = selectors[expectedIndex].text
      else:   
         element["value"] = selectors[expectedIndex][attribute]
      element["selector"] = "found"
      elements.append(element) 
      returnCode = NO_SELECTOR_FOUND_WITH_SPECIFIC_VALUE
   elif(selectorsFound == 1):
      if(expectedIndex in selectorIndexes):
         print("The expected selector was found and it is the only selector.")
         element = {}
         element["index"] = expectedIndex
         if(attribute == "text"):
            element["value"] = selectors[expectedIndex].text
         else:   
            element["value"] = selectors[expectedIndex][attribute]
         element["selector"] = "original"
         elements.append(element) 
         returnCode = SELECTOR_FOUND_WITH_CORRECT_INDEX
      else:
         # The expected selector was not found, we need to return the original selector (using expected index)
         #  and the found selector.
         print("The incorrect selector was found and this is the only selector with the expected src")
         element = {}
         element["index"] = expectedIndex
         if(attribute == "text"):
            element["value"] = selectors[expectedIndex].text
         else:   
            element["value"] = selectors[expectedIndex][attribute]
         element["selector"] = "original"
         elements.append(element) 

         element = {}
         element["index"] = selectorIndexes[selectorsFound -1]
         if(attribute == "text"):
            element["value"] = selectors[selectorIndexes[selectorsFound -1]].text
         else:   
            element["value"] = selectors[selectorIndexes[selectorsFound -1]][attribute]
         element["selector"] = "found"
         elements.append(element) 
         returnCode = SELECTOR_FOUND_WITH_INCORRECT_INDEX
   elif(selectorsFound > 1):
      print("Several selectors were found with same src " + str(selectorIndexes)) 
      if(expectedIndex in selectorIndexes):
         print("The expected element " + str(expectedIndex) + " was found on the selectors")
         element = {}
         element["index"] = expectedIndex
         if(attribute == "text"):
            element["value"] = selectors[expectedIndex].text
         else:   
            element["value"] = selectors[expectedIndex][attribute]
         element["selector"] = "original"
         elements.append(element) 
         returnCode = MULTIPLE_SELECTORS_FOUND_WITH_EXPECTED_VALUE_CORRECT_INDEX
      else:
         print("The expected element " + str(expectedIndex) + " was NOT found on the selectors")
         element = {}
         if(attribute == "text"):
            element["value"] = selectors[expectedIndex].text
         else:   
            element["value"] = selectors[expectedIndex][attribute]
         element["index"] = expectedIndex
         element["selector"] = "original"
         elements.append(element) 

         element = {}
         if(attribute == "text"):
            element["value"] = expectedValue
         else:   
            element["value"] = expectedValue
         element["index"] = str(selectorIndexes)   
         element["selector"] = "found"
         elements.append(element) 
         returnCode = MULTIPLE_SELECTORS_FOUND_WITH_EXPECTED_VALUE_INCORRECT_INDEX

   jsonObject["numberOfElementsWithSameSelectorAndValue"] = selectorsFound   
   jsonObject["selectors"] = elements
   jsonObject["rc"] = returnCode

   return jsonObject

def parseTextSelector(selectors, expectedValue, expectedIndex):
   jsonObject = {}
   selectorIndexes = []
   counter = 0
   selectorsFound = 0

   if(expectedValue == ""):
     jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0   
     jsonObject["selectors"] = []
     jsonObject["rc"] = NO_VALUE_PROVIDED_BY_BE
     return jsonObject

   for selector in selectors:
      if((selector.text).strip() == expectedValue.strip()):
         selectorsFound += 1
         selectorIndexes.append(counter)
      counter+=1   
   
   return processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "text")


def parseImageSelector(selectors, expectedValue, expectedIndex):
   selectorIndexes = []
   counter = 0
   selectorsFound = 0
   for selector in selectors:
      if(selector['src'] == expectedValue ):
         selectorsFound += 1
         selectorIndexes.append(counter)
      counter+=1   

   return processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "src")

#
# This method will be called when two or more selectors are found with . 
# the same ntagselector value. This method will use the expected value (href) 
# to filter the selctors and try to find the one that was used by the test.
# 
def parseHypertextSelector(selectors, expectedValue, expectedIndex):
   jsonObject = {}
   selectorIndexes = []
   counter = 0
   selectorsFound = 0

   if(expectedValue == ""):
     jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0   
     jsonObject["selectors"] = []
     jsonObject["rc"] = NO_VALUE_PROVIDED_BY_BE
     return jsonObject

   for selector in selectors:
      if(selector and selector.has_attr('href')):
         if(selector['href'] == expectedValue):
            selectorsFound += 1
            selectorIndexes.append(counter)
      counter+=1   
   
   return processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "href")


def parseValueSelector(selectors, expectedValue, expectedIndex, type):
   jsonObject = {}
   selectorIndexes = []
   counter = 0
   selectorsFound = 0

   for selector in selectors:
      if(selector['value'] == expectedValue ):
         selectorsFound += 1
         selectorIndexes.append(counter)
      counter+=1   
   
   jsonObject = processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "value")

   return jsonObject



def obtainFeedbackFromDOM(classname, stepId, ntagselector, value, index, tag, type, action, searchType):
   jsonObject = {}
   elements = []    
   path = 'build/reports/geb/firefoxTest/'
   filename = path + classname + "_" + str(stepId) + ".html"

   if os.path.exists(filename):
      try:
         print("\n============= Step " + str(stepId) + "=============")

         if(stepId == 6):
          index = 2 

         print("Tag " + tag)
         print("Search by " + searchType)
         print("index " + str(index))
         print("action " + str(action))

         text = open(filename, 'r').read()
         soup = BeautifulSoup(text, 'html.parser')
         selectorsFound = soup.select(ntagselector)
         #print("Selectors: " + str(selectorsFound))
         numberSelectorsFound = len(selectorsFound)
         print("Selectors found: " + str(numberSelectorsFound))

         if(index > numberSelectorsFound):
            jsonObject["selectors"] = []
            jsonObject["rc"] = STEP_INDEX_GREATER_THAN_NUMBER_OF_SELECTORS_FOUND  
            jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0
         elif(action == "assignment" or action == "mouseover"):
            jsonObject["selectors"] = []
            jsonObject["rc"] = ACTION_NOT_VALID_FOR_ANALYSIS
            jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0
         else:  
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
                  jsonObject["rc"] = NO_SEARCH_TYPE_PROVIDED_BY_BE
                  jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0
                  
            elif(numberSelectorsFound == 1 ):
               element = {}
               element["index"] = index
               element["value"] = value
               element["selector"] = "original"
               elements.append(element)
               jsonObject["selectors"] = elements
               jsonObject["numberOfElementsWithSameSelectorAndValue"] = numberSelectorsFound
               jsonObject["rc"] = ONE_SELECTOR_FOUND_FOR_NTAGSELECTOR

         jsonObject["numberOfElementsWithSameSelector"] = numberSelectorsFound
         pprint.pprint(jsonObject)
         print("==============================================")  
      except Exception as ex:
         print("Failed to open file " + ex)
         print (ex)
   
   return jsonObject


def createMuukReport(classname):
   path = 'build/reports/'
   filename = path + classname + ".json"
   muukReport = {}
   steps = []
   if(os.path.exists(filename)):
      try:
        jsonFile = open(filename, 'r')
        elements = json.load(jsonFile)
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
            element["numberOfElementsWithSameSelectorAndValue"] = domInfo["numberOfElementsWithSameSelectorAndValue"]
            element["rc"] = domInfo["rc"]
            element["selectors"] = domInfo["selectors"]
            steps.append(element)

      except Exception as ex:
          print("Exception found during DOM parsing. Exception = " + str(ex))     
      
      # Closing file
   jsonFile.close()

   muukReport["steps"] = steps
   pprint.pprint(steps)

   return muukReport

createMuukReport("devFushosoftCom86e660e3") 
