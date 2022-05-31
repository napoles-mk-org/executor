
import os
import json
from bs4 import BeautifulSoup
import traceback
import logging

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
SELECT_ELEMENT_INCORRECT_VALUE = 14
SELECTOR_BUILD_FROM_ATTRIBUTES = 15

CLASSIC_SELECTOR    = 0
DYMANIC_SELECTOR    = 1
CUSTOM_CSS_SELECTOR = 2
XPATH_SELECTOR      = 3

SELECTORS_ARRAY =  [CLASSIC_SELECTOR, DYMANIC_SELECTOR, CUSTOM_CSS_SELECTOR ]
SELECTORS_ARRAY_NAMES =  ["CLASSIC_SELECTOR", "DYMANIC_SELECTOR", "CUSTOM_CSS_SELECTOR" ]

logger = logging.getLogger(__name__)

# Description:
#   This method will be called to handle the result of filter (by value, text,etc) operation done  
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
def processResults(selector, htmlElements, expectedIndex, expectedValue, elementsFoundWithValue, indexesFound, attribute):
   jsonObject = {}
   elements = []

   if(elementsFoundWithValue == 0):
      # No selectors were found with the expected value
      if(expectedIndex <= len(htmlElements)):
         element = {}
         element["index"] = expectedIndex
         element["selector"] = selector
         returnCode = NO_SELECTOR_FOUND_WITH_SPECIFIC_VALUE
      else:
         element = {}
         element["index"] = "-1"
         element["selector"] = ""
         returnCode = STEP_INDEX_GREATER_THAN_NUMBER_OF_SELECTORS_FOUND   
   elif(elementsFoundWithValue == 1):
      if(expectedIndex in indexesFound):
        # The expected selector was found and it is the only selector.
         element = {}
         element["index"] = expectedIndex
         element["selector"] = selector
         if(attribute == "text"):
            element["value"] = htmlElements[expectedIndex].text
         else:   
            element["value"] = htmlElements[expectedIndex][attribute]
         returnCode = SELECTOR_FOUND_WITH_CORRECT_INDEX
      else:
         # The incorrect selector was found and this is the only selector with the expected value        
         element = {}
         element["index"] = indexesFound[elementsFoundWithValue -1]
         element["selector"] = selector
         if(attribute == "text"):
            element["value"] = htmlElements[indexesFound[elementsFoundWithValue -1]].text
         else:   
            element["value"] = htmlElements[indexesFound[elementsFoundWithValue -1]][attribute]
         returnCode = SELECTOR_FOUND_WITH_INCORRECT_INDEX
   elif(elementsFoundWithValue > 1):
      # Several selectors were found with same value
      if(expectedIndex in indexesFound):
         # The expected element was found on the selectors
         element = {}
         element["index"] = expectedIndex
         element["selector"] = selector
         if(attribute == "text"):
            element["value"] = htmlElements[expectedIndex].text
         else:   
            element["value"] = htmlElements[expectedIndex][attribute]
         elements.append(element) 
         returnCode = MULTIPLE_SELECTORS_FOUND_WITH_EXPECTED_VALUE_CORRECT_INDEX
      else:
         # The expected element was NOT found on the selector
         element = {}
         element["index"] = str(indexesFound)   
         element["selector"] = selector
         if(attribute == "text"):
            element["value"] = expectedValue
         else:   
            element["value"] = expectedValue
         returnCode = MULTIPLE_SELECTORS_FOUND_WITH_EXPECTED_VALUE_INCORRECT_INDEX

   jsonObject["numberOfElementsFoundWithSelectorAndValue"] = elementsFoundWithValue   
   jsonObject["selectors"] = element
   jsonObject["rc"] = returnCode

   return jsonObject

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the text value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters: 
#    selector: selector string
#    htmlElements: Array of htmlElements found with the same selector.
#    searchInfo: Object containing infromation related to the DOM analysis (value to find, element type, etc.).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseTextSelector(selector, htmlElements, searchInfo, expectedIndex, tag):
   jsonObject = {}
   indexesFound = []
   index = 0
   numberElementsFoundWithValue = 0
   expectedValue = searchInfo["value"]

   if(expectedValue == ""):
     element = {}
     element["index"] = expectedIndex
     element["selector"] = selector
     jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0   
     jsonObject["selectors"] = element
     jsonObject["rc"] = NO_VALUE_PROVIDED_BY_BE
     return jsonObject

   for htmlElment in htmlElements:
      selectorText = htmlElment.text.replace("'", "")
      if(selectorText.strip() == expectedValue.strip()):
         numberElementsFoundWithValue += 1
         indexesFound.append(index)
      index+=1   
   
   return processResults(selector, htmlElements, expectedIndex, expectedValue, numberElementsFoundWithValue, indexesFound, "text")

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the src value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters: 
#    selector: selector string
#    htmlElements: Array of htmlElements found with the same selector.
#    searchInfo: Object containing infromation related to the DOM analysis (value to find, element type, etc.).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseImageSelector(selector, htmlElements, searchInfo, expectedIndex, tag):
   indexesFound = []
   index = 0
   numberElementsFoundWithValue = 0
   expectedValue = searchInfo["value"]

   for selector in htmlElements:
      if(selector['src'] == expectedValue ):
         numberElementsFoundWithValue += 1
         indexesFound.append(index)
      index+=1   

   return processResults(selector, htmlElements, expectedIndex, expectedValue, numberElementsFoundWithValue, indexesFound, "src")

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the href value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters:
#    selector: selector string 
#    htmlElements: Array of htmlElements found with the same selector.
#    searchInfo: Object containing infromation related to the DOM analysis (value to find, element type, etc.).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseHypertextSelector(selector, htmlElements, searchInfo, expectedIndex, tag):
   jsonObject = {}
   indexesFound = []
   filteredIndexes = []
   index = 0
   numberElementsFoundWithValue = 0
   expectedValue = searchInfo["value"]
   if hasattr(searchInfo, 'text'):   
      expectedText = searchInfo["text"]
   else:
      expectedText = "" 

   if(expectedValue == ""):
     element = {}
     element["index"] = expectedIndex
     element["selector"] = selector
     jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0   
     jsonObject["selectors"] = element
     jsonObject["rc"] = NO_VALUE_PROVIDED_BY_BE
     return jsonObject

   for element in htmlElements:
      if(element and element.has_attr('href')):
         if(element['href'] == expectedValue):
            numberElementsFoundWithValue += 1
            indexesFound.append(index)
      index+=1   
   
   # If more than 1 element was found using the same value, lest's filter now by text and update
   # the indexesFound with the new indexes (hopefully only one!).
   if(numberElementsFoundWithValue > 1 and expectedText != ""):
     for i in indexesFound:
        if(str(htmlElements[i].string) == expectedText):
           filteredIndexes.append(i)
     if(len(filteredIndexes) > 0 ):
      indexesFound = []
      numberElementsFoundWithValue = len(filteredIndexes)
      for index in filteredIndexes:
         indexesFound.append(index)

   return processResults(selector, htmlElements, expectedIndex, expectedValue, numberElementsFoundWithValue, indexesFound, "href")

# Description:
#   This method will be called when two or more selectors were found with
#   the same ntagselector value. This method will use the value attribute  
#   to filter the selctors and try to find the one that was used by the test.
#
# Parameters: 
#    selector: selector string
#    htmlElements: Array of htmlElements found with the selector.
#    searchInfo: Object containing infromation related to the DOM analysis (value to find, element type, etc.).
#    expectedIndex: The index that is expected to contain the expected value. 
# 
# Returns:
#    jsonObject with the number of selectors found, the selctors and the return code. 
def parseValueSelector(selector, htmlElements, searchInfo, expectedIndex, tag):
   indexesFound = []
   index = 0
   numberElementsFoundWithValue = 0
   expectedValue = searchInfo["value"] if ('value' in searchInfo) else ""
   expectedText = searchInfo["text"] if ('text' in searchInfo) else ""

   for element in htmlElements:
      if(('value' in element) and element['value'] == expectedValue ):
         numberElementsFoundWithValue += 1
         indexesFound.append(index)
      index+=1   

   # If we have text information available and this is a select element, let's try to
   # find the correct value using the text
   if(numberElementsFoundWithValue == 0 and expectedText != "" and tag == "select"):
      return handleSelectElement(selector, htmlElements, expectedText, expectedIndex, indexesFound, tag)
   
   return processResults(selector, htmlElements, expectedIndex, expectedValue, numberElementsFoundWithValue, indexesFound, "value")

def handleSelectElement(selector, htmlElements, expectedText, expectedIndex, selectorIndexes, tag):
   jsonObject = {}
   value = ""
   # Let's first verify the selector with the expected index
   selectElement = htmlElements[expectedIndex]
   options = selectElement.find_all("option")
   for option in options:
      if(option.text.strip() == expectedText.strip()):
         value = option.get("value")
         break
   
   element = {}
   element["index"] = expectedIndex
   element["value"] = value
   element["selector"] = selector

   jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 1   
   jsonObject["selectors"] = element
   jsonObject["rc"] = SELECT_ELEMENT_INCORRECT_VALUE

   return jsonObject


# Description:
#   This function will be called when the selector string returns 0 elements. It means the selector that we have is not working and we need to 
#   build a new one. This function will will verify the object's attributes and validate an HTML element
#   exists using this attribute before adding it to the selector string.
#
# Parameters: 
#    tag: HTML tag of the element 
#    attributes: Object's attributes (name, id, type, etc)
#    soup: (BeautifulSoup object to query HTML DOM)
# Returns:
#    CSS selector
#
def buildSelectorFromAttributes(tag, attributes, soup):
   jsonObject = {}

   # Start building the CSS selector
   selector = tag
   if(attributes["id"] != "false" and attributes["id"] != "undef"):
      if(len(soup.select(tag + "[id='"+attributes["id"]+"']")) > 0):
         selector = selector + "[id='"+attributes["id"]+"']"
   if(attributes["name"] != "undef"):
      if(len(soup.select(tag + "[name='"+attributes["name"]+"']")) > 0):
         selector = selector + "[name='"+attributes["name"]+"']"   
   if(attributes["type"] != "undef"):
      if(len(soup.select(tag + "[type='"+attributes["type"]+"']")) > 0):
         selector = selector + "[type='"+attributes["type"]+"']" 
   
   selectorsFound = soup.select(selector)
   numberSelectorsFound = len(selectorsFound)
   index = 0
   selectorsWithTextIndex = 0

   bFoundWithText = False
   if(numberSelectorsFound > 1 and attributes["text"] != "undef"):
     for sel in selectorsFound:
         if(sel.string == attributes['text']):
               selectorsWithTextIndex = index
               bFoundWithText = True
               break
         index += 1       

   if(numberSelectorsFound == 0 ):
      element = {}
      element["selector"] = selector
      element["index"] = index
      jsonObject["selectors"] = element
      jsonObject["numberOfElementsFoundWithSelector"] = 0
      jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0
      jsonObject["rc"] = NO_SELECTOR_FOUND_WITH_NTAGSELECTOR        
   elif(numberSelectorsFound == 1 or bFoundWithText ):
      element = {}
      element["selector"] = selector
      element["index"] = selectorsWithTextIndex
      jsonObject["selectors"] = element
      jsonObject["rc"] = SELECTOR_BUILD_FROM_ATTRIBUTES
      jsonObject["numberOfElementsFoundWithSelector"] = 0
      jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 1

   return jsonObject


# Description:
#   This function will be called when we have more than one element as a result of the selector query and we DO NOT have
#   a value to try to filter the attributes and find the correct one. So, using the object's attributes we will try to find the 
#   correct selector.
#
# Parameters: 
#    tag: HTML tag of the element 
#    attributes: Object's attributes (name, id, type, etc)
#    soup: (BeautifulSoup object to query HTML DOM)
# Returns:
#    CSS selector
#
def findIndexFromAttributes(selector, tag, attributes, soup):
   jsonObject = {}
   idFound = False
   if(attributes["id"] != "false" and attributes["id"] != "undef"):
     objectID = attributes["id"]
   if(attributes["name"] != "undef"):
     objectName = attributes["name"]
   if(attributes["type"] != "undef"):
     objectType = attributes["type"]

   htmlElementsFound = soup.select(selector)
   numberElementsFound = len(htmlElementsFound)
   if(numberElementsFound > 1 ):
     newIndex = 0 
     for element in htmlElementsFound:
        if(element.has_attr('id') and element['id'] == objectID and 
        element.has_attr('name') and element['name'] == objectName and
        element.has_attr('type') and element['type'] == objectType):
           idFound = True
           break
        newIndex = newIndex + 1

   if(idFound):
      element = {}
      element["selector"] = selector
      element["index"] = newIndex
      jsonObject["selectors"] = element
      jsonObject["rc"] = SELECTOR_BUILD_FROM_ATTRIBUTES
      jsonObject["numberOfElementsFoundWithSelector"] = 0
      jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 1
   else:
      element = {}
      element["selector"] = selector
      element["index"] = 0
      jsonObject["selectors"] = element
      jsonObject["numberOfElementsFoundWithSelector"] = 0
      jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0
      jsonObject["rc"] = NO_SELECTOR_FOUND_WITH_NTAGSELECTOR  

   return jsonObject   

# Description:
#   This function will be called when the object DOES NOT HAVE a selector string, so we need to build it from scratch. 
#   This function will verify the object's attributes and validate an HTML element
#   exists using this attribute before adding it to the selector string.
#
# Parameters: 
#    tag: HTML tag of the element 
#    attributes: Object's attributes (name, id, type, etc)
#    soup: (BeautifulSoup object to query HTML DOM)
# Returns:
#    CSS selector
#
def buildCSSSelector(tag, attributes, searchInfo, index,  soup):
   jsonObject = {}
   cssSelector = tag
   searchType = searchInfo["searchType"]
   value = searchInfo["value"]
   
   if(attributes["id"] != "false" and attributes["id"] != "undef"):
      if(len(soup.select(tag + "[id='"+attributes["id"]+"']")) > 0):
         cssSelector = cssSelector + "[id = '" + attributes["id"] + "']"
   if(attributes["name"] != "undef"):
      if(len(soup.select(tag + "[name='"+attributes["name"]+"']")) > 0):
         cssSelector = cssSelector + "[name = '" + attributes["name"] + "']"
   if(attributes["type"] != "undef"):
      if(len(soup.select(tag + "[type='"+attributes["type"]+"']")) > 0):
         cssSelector = cssSelector + "[type = '" + attributes["type"] + "']"

   # now that we have a selector, let's va;idate it returns elements.
   htmlElementsFound = soup.select(cssSelector)
   numberElementsFound = len(htmlElementsFound)
   logger.info("buildCSSSelector - Found " + str(numberElementsFound) + " with selector " + cssSelector)

   if(numberElementsFound == 1):
      element = {}
      element["selector"] = cssSelector
      element["index"] = 0
      jsonObject["selectors"] = element
      jsonObject["rc"] = SELECTOR_BUILD_FROM_ATTRIBUTES
      jsonObject["numberOfElementsFoundWithSelector"] = 1
      jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 1
   elif(numberElementsFound > 1):  
      if(searchType == "value"):
         jsonObject = parseValueSelector(cssSelector, htmlElementsFound, searchInfo, index, tag)
      elif(searchType == "href"):
         jsonObject = parseHypertextSelector(cssSelector, htmlElementsFound, searchInfo, index, tag)
      elif(searchType == "text"):
         jsonObject = parseTextSelector(cssSelector, htmlElementsFound, searchInfo, index, tag)
      elif(searchType == "imgsrc"):
         jsonObject = parseImageSelector(cssSelector, htmlElementsFound, searchInfo, index, tag)
      else:
         # Backend sent an undef searchType, we will return no info
         element = {}   
         element["selector"] = cssSelector
         element["index"] = index        
         jsonObject["selectors"] = element
         jsonObject["rc"] = NO_SEARCH_TYPE_PROVIDED_BY_BE
         jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0
   else:
      element = {}
      element["selector"] = ""
      element["index"] = 0
      jsonObject["selectors"] = element
      jsonObject["rc"] = SELECTOR_BUILD_FROM_ATTRIBUTES
      jsonObject["numberOfElementsFoundWithSelector"] = 0
      jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0

   return jsonObject    


# Description:
#   This method will be call for each step and will parse the DOM files generated  
#   for the test to find the selectors for this step. If more than one selector is found,  
#   this method makes another search on the DOM using the value to filter the 
#   selectors found. 
#
# Returns:
#    jsonObject with the number of selector information. 
def obtainCSSFeedbackFromDOM(classname, stepId, selector, index, tag, type, action, searchInfo, browserName, attributes, selector_type):
   logging.info("Starting CSS analysis for "+ SELECTORS_ARRAY_NAMES[selector_type] + " selector " + str(selector) + " witn index " + str(index) + " on step " + str(stepId))
   jsonObject = {}  
   path = 'build/reports/geb/' + browserName + '/'
   filename = path + classname + "_" + str(stepId) + ".html"
   if os.path.exists(filename):
      try:
         searchType = searchInfo["searchType"]
         value = searchInfo["value"]
         text = open(filename, 'r').read()
         soup = BeautifulSoup(text, 'html.parser')
         if(selector is None):
            if(selector_type == CUSTOM_CSS_SELECTOR):
               logging.info("NO CSS Selector, need to build it")
               return buildCSSSelector(tag, attributes, searchInfo, 0, soup)
         else:
            selectorsFound = soup.select(selector)
            numberSelectorsFound = len(selectorsFound)

            if(action == "mouseover"):
               element = {}   
               element["selector"] = selector   
               element["index"] = index   
               jsonObject["selectors"] = element
               jsonObject["rc"] = ACTION_NOT_VALID_FOR_ANALYSIS
               jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0
            else:  
               if(numberSelectorsFound == 0):
                  if(len(attributes) > 0 and selector_type == CUSTOM_CSS_SELECTOR ):
                     return buildSelectorFromAttributes(tag, attributes, soup)
                  else:
                     element = {}
                     element["selector"] = selector
                     element["index"] = index
                     jsonObject["selectors"] = element
                     jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0
                     jsonObject["rc"] = NO_SELECTOR_FOUND_WITH_NTAGSELECTOR   

               elif(numberSelectorsFound == 1 ):
                  element = {}   
                  element["selector"] = selector  
                  if(searchType == "value" and selectorsFound[0].has_attr('value')):
                     element["value"] = selectorsFound[0]["value"]
                  elif(searchType == "href" and selectorsFound[0].has_attr('href')): 
                     element["value"] = selectorsFound[0]["href"]
                  elif(searchType == "text" and selectorsFound[0].has_attr('text')):
                     element["value"] = selectorsFound[0].text
                  elif(searchType == "imgsrc" and selectorsFound[0].has_attr('src')):
                     element["value"] = selectorsFound[0]["src"]
                  else:
                     element["value"] = searchInfo["value"]        
                  if(index > 0):
                     element["index"] = 0
                     if(searchType == "value" and selectorsFound[0].has_attr('value')):
                        element["value"] = selectorsFound[0]["value"]
                     elif(searchType == "href" and selectorsFound[0].has_attr('href')):   
                        element["value"] = selectorsFound[0]["href"]
                     elif(searchType == "text" and selectorsFound[0].has_attr('text')):
                        element["value"] = selectorsFound[0].text
                     elif(searchType == "imgsrc" and selectorsFound[0].has_attr('src')):
                        element["value"] = selectorsFound[0]["src"]
                     else:
                        element["value"] = searchInfo["value"]
                     returnCode = SELECTOR_FOUND_WITH_INCORRECT_INDEX
                  else:
                     element["index"] = index
                     returnCode = ONE_SELECTOR_FOUND_FOR_NTAGSELECTOR

                  jsonObject["selectors"] = element
                  jsonObject["numberOfElementsFoundWithSelectorAndValue"] = numberSelectorsFound
                  jsonObject["rc"] = returnCode

               elif(numberSelectorsFound > 1 ):
                  if(value != "undef"):
                     if(searchType == "value"):
                        jsonObject = parseValueSelector(selector, selectorsFound, searchInfo, index, tag)
                     elif(searchType == "href"):
                        jsonObject = parseHypertextSelector(selector, selectorsFound, searchInfo, index, tag)
                     elif(searchType == "text"):
                        jsonObject = parseTextSelector(selector, selectorsFound, searchInfo, index, tag)
                     elif(searchType == "imgsrc"):
                        jsonObject = parseImageSelector(selector, selectorsFound, searchInfo, index, tag)
                     else:
                        # Backend sent an undef searchType, we will return no info
                        element = {}   
                        element["selector"] = selector
                        element["index"] = index        
                        jsonObject["selectors"] = element
                        jsonObject["rc"] = NO_SEARCH_TYPE_PROVIDED_BY_BE
                        jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0
                  else:
                     # We do not have a value to try to identify the element, let's use the attributes
                     if(len(attributes) > 0 and selector_type == CUSTOM_CSS_SELECTOR ):
                        logging.info("Found "+ str(numberSelectorsFound) + " selectors and no value to filter, let's build from attributes")
                        return findIndexFromAttributes(selector, tag, attributes, soup) 
                     else:
                        element = {}   
                        element["selector"] = selector
                        element["index"] = index        
                        jsonObject["selectors"] = element
                        jsonObject["rc"] = NO_SEARCH_TYPE_PROVIDED_BY_BE
                        jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0

            jsonObject["numberOfElementsFoundWithSelector"] = numberSelectorsFound

      except Exception as ex:
         logging.error (ex)

   # Let's validate the data we generated is a valid json for this step
   try:
     json.loads(json.dumps(jsonObject)) 
   except Exception as ex: 
     logging.error("Invalid JSON format for step " + str(stepId) +"  found, will not send feedback to BE")
     logging.error(ex) 
     logging.error(traceback.format_exc())    
     jsonObject = {}

   return jsonObject
