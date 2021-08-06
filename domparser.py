
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
NO_SELECTOR_FOUND_WITH_NTAGSELECTOR = 13


# Description:
#   This method will be called to handle the result of filter operation done  
#   on the selectors found.
#   
#   There are 3 options for the result:
#    1) No selectors were found having the value we are expecting. On this case,
#       information returned will be the element with the index that was expected.
#
#    2) We found only one selector, we have two options here:
#       a) Found the correct selector: Return the original element.
#       b) Found the incorrect selector. Return two elements, one with the original index and other with the found index.
# 
#    3) We found two or more selectors with the same src. We have two options here:
#       a) The correct selector was found. Return the original element. 
#       b) The correct selector was not found. Return two elements, one with the original index and other with all the indexes found.
#   
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
#
def processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, attribute):
   jsonObject = {}
   elements = []

   if(selectorsFound == 0):
      # No selectors were found with the expected value
      if(expectedIndex <= selectorsFound):
         element = {}
         element["index"] = expectedIndex
         if(attribute == "text"):
            element["value"] = selectors[expectedIndex].text
         else:   
            element["value"] = selectors[expectedIndex][attribute]
         element["selector"] = "found"
         elements.append(element) 
         returnCode = NO_SELECTOR_FOUND_WITH_SPECIFIC_VALUE
      else:
         returnCode = STEP_INDEX_GREATER_THAN_NUMBER_OF_SELECTORS_FOUND   
   elif(selectorsFound == 1):
      if(expectedIndex in selectorIndexes):
        # The expected selector was found and it is the only selector.
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
         # The incorrect selector was found and this is the only selector with the expected value
         if(expectedIndex <= selectorsFound):
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
      # Several selectors were found with same value
      if(expectedIndex in selectorIndexes):
         # The expected element was found on the selectors
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
         # The expected element was NOT found on the selectors
         if(expectedIndex <= selectorsFound):
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

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the text value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters: 
#    selectors: Array of selectors found with the same ntagselector.
#    expectedValue: The value that is expected to be found (value captured by the extension).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseTextSelector(selectors, expectedValue, expectedIndex):
   jsonObject = {}
   selectorIndexes = []
   selectorIndex = 0
   selectorsFound = 0

   if(expectedValue == ""):
     jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0   
     jsonObject["selectors"] = []
     jsonObject["rc"] = NO_VALUE_PROVIDED_BY_BE
     return jsonObject

   for selector in selectors:
      if((selector.text).strip() == expectedValue.strip()):
         selectorsFound += 1
         selectorIndexes.append(selectorIndex)
      selectorIndex+=1   
   
   return processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "text")

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the src value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters: 
#    selectors: Array of selectors found with the same ntagselector.
#    expectedValue: The value that is expected to be found (value captured by the extension).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseImageSelector(selectors, expectedValue, expectedIndex):
   selectorIndexes = []
   selectorIndex = 0
   selectorsFound = 0
   for selector in selectors:
      if(selector['src'] == expectedValue ):
         selectorsFound += 1
         selectorIndexes.append(selectorIndex)
      selectorIndex+=1   

   return processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "src")

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the href value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters: 
#    selectors: Array of selectors found with the same ntagselector.
#    expectedValue: The value that is expected to be found (value captured by the extension).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseHypertextSelector(selectors, expectedValue, expectedIndex):
   jsonObject = {}
   selectorIndexes = []
   selectorIndex = 0
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
            selectorIndexes.append(selectorIndex)
      selectorIndex+=1   
   
   return processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "href")

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters: 
#    selectors: Array of selectors found with the same ntagselector.
#    expectedValue: The value that is expected to be found (value captured by the extension).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseValueSelector(selectors, expectedValue, expectedIndex, type):
   selectorIndexes = []
   selectorIndex = 0
   selectorsFound = 0

   for selector in selectors:
      if(selector['value'] == expectedValue ):
         selectorsFound += 1
         selectorIndexes.append(selectorIndex)
      selectorIndex+=1   

   return processResults(selectors, expectedIndex, expectedValue, selectorsFound, selectorIndexes, "value")

# Description:
#   This method will be call for each step and will parse the DOM files generated  
#   for the test to find the selectors for this step. If more than one selector is found,  
#   this method makes another search on the DOM using the value to filter the 
#   selectors found. 
#
# Returns:
#    jsonObject with the number of selector information. 
def obtainFeedbackFromDOM(classname, stepId, ntagselector, value, index, tag, type, action, searchType, browserName):
   jsonObject = {}
   elements = []    
   path = 'build/reports/geb/' + browserName + '/'
   filename = path + classname + "_" + str(stepId) + ".html"

   if os.path.exists(filename):
      try:
         text = open(filename, 'r').read()
         soup = BeautifulSoup(text, 'html.parser')
         selectorsFound = soup.select(ntagselector)
         numberSelectorsFound = len(selectorsFound)

         if(action == "assignment" or action == "mouseover"):
            jsonObject["selectors"] = []
            jsonObject["rc"] = ACTION_NOT_VALID_FOR_ANALYSIS
            jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0
         else:  
            if(numberSelectorsFound == 0 ):
               jsonObject["selectors"] = []
               jsonObject["numberOfElementsWithSameSelectorAndValue"] = 0
               jsonObject["rc"] = NO_SELECTOR_FOUND_WITH_NTAGSELECTOR
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
               if(searchType == "value"):
                  element["value"] = selectorsFound[0]["value"]
               elif(searchType == "href"):   
                  element["value"] = selectorsFound[0]["href"]
               elif(searchType == "text"):
                  element["value"] = selectorsFound[0].text
               elif(searchType == "imgsrc"):
                  element["value"] = selectorsFound[0]["src"]
               elements.append(element)
               returnCode = ONE_SELECTOR_FOUND_FOR_NTAGSELECTOR

               if(index > 0):
                  element = {}
                  element["index"] = 0
                  element["selector"] = "found"
                  if(searchType == "value"):
                     element["value"] = selectorsFound[0]["value"]
                  elif(searchType == "href"):   
                     element["value"] = selectorsFound[0]["href"]
                  elif(searchType == "text"):
                     element["value"] = selectorsFound[0].text
                  elif(searchType == "imgsrc"):
                     element["value"] = selectorsFound[0]["src"]
                  elements.append(element)
                  returnCode = SELECTOR_FOUND_WITH_INCORRECT_INDEX

               jsonObject["selectors"] = elements
               jsonObject["numberOfElementsWithSameSelectorAndValue"] = numberSelectorsFound
               jsonObject["rc"] = returnCode

         jsonObject["numberOfElementsWithSameSelector"] = numberSelectorsFound

      except Exception as ex:
         print("Failed to open file " + ex)
         print (ex)
   
   return jsonObject


# Description:
#   This method will be call to execuete the Muuk Report analysis.  
#   for the test to find the selectors for this step. If more than one selector is found,  
#   this method makes another search on the DOM using the value to filter the 
#   selectors found. 
#
# Returns:
#    jsonObject with the number of selector information. 
def createMuukReport(classname, browserName):
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
            valueData = json.loads(element.get("value"))
            domInfo = obtainFeedbackFromDOM(classname, element.get("id"), 
                                             element.get("selector"), valueData["value"], 
                                             element.get("index"), element.get("tag"),
                                             element.get("objectType"), element.get("action"), 
                                             valueData["searchType"],
                                             browserName)
            if(domInfo):                                
               element["numberOfElementsWithSameSelector"] = domInfo["numberOfElementsWithSameSelector"]
               element["numberOfElementsWithSameSelectorAndValue"] = domInfo["numberOfElementsWithSameSelectorAndValue"]
               element["rc"] = domInfo["rc"]
               element["selectors"] = domInfo["selectors"]
               steps.append(element)
          else:
            steps.append(element)     

      except Exception as ex:
          print("Exception found during DOM parsing. Exception = " + str(ex))     
      
      # Closing file
      jsonFile.close()
   else:
      print("Muuk Report was not found!")   

   muukReport["steps"] = steps

   # Print report if touch file exists
   if(os.path.exists("TOUCH_TRACE_REPORT")):
     pprint.pprint(steps)

   return muukReport