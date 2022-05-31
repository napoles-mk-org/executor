
from logging import root
import os
import json
import pprint
import lxml.etree
import lxml.html
from xml.sax import saxutils
from lxml import html
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

logger = logging.getLogger(__name__)

# Description:
#   This method returns the inner HTML of the element received as a parameter. 
#
# Parameters: 
#    element: HTML element 
#
# Returns:
#    inner HTML (string) 
#
def inner_html(element):
    return (saxutils.escape(element.text) if element.text else '') + \
        ''.join([html.tostring(child, encoding=str) for child in element.iterchildren()])

# Description:
#   This function build an XPATH selector string. It will verify the object's attributes and validate an HTML element
#   exists using this attribute before adding it to the selector string.
#
# Parameters: 
#    tag: HTML tag of the element 
#    attributes: Object's attributes (name, id, type, etc)
#    root: (LXML object to query HTML DOM)
# Returns:
#    XPATH selector
#
def buildXPATHSelector(tag, attributes, root):
   logger.info("buildXPATHSelector - attributes = " + str(attributes))
   jsonObject = {}
   elements = []  
   textUsedOnSelector = False 

   selector = "//" + tag
   if(attributes["id"] != "false" and attributes["id"] != "undef"):
      if(len(root.xpath("//" + tag + "[@id='"+attributes["id"]+"']")) > 0):
          selector = selector + "[@id='"+attributes["id"]+"']"

   if(attributes["name"] != "undef"):
      if(len(root.xpath("//" + tag + "[@name='"+attributes["name"]+"']")) > 0):
         selector = selector + "[@name='"+attributes["name"]+"']"   
   
   if(attributes["type"] != "undef"):
      if(len(root.xpath("//" + tag + "[@type='"+attributes["type"]+"']")) > 0):
         selector = selector + "[@type='"+attributes["type"]+"']" 

   if( attributes["text"] and len(attributes["text"]) > 0 and attributes["text"] != "undef" ):
      textUsedOnSelector =  True
      text = attributes["text"]
      innerHTMLText = ""

      # As MuukTest sends the text that is obtained from innerText it does not contain any <html> tag that the DOM will contian when searching 
      # for a XPATH expression. So, we will query all the tag elements and get the innerText so we can compare and then build the xpath
      elements = root.xpath("//" + tag)
      elementIndex = -1
      for element in elements:
       if(element.text_content() == text):
          elementIndex = elementIndex + 1
          text = element.text_content()
          innerHTMLText = inner_html(element)

      splittedText = text.split("\n")
      if(len(splittedText) > 1 or (innerHTMLText != "" and innerHTMLText != text ) ):
         # if we are using normalize-space we need to use the complete text but we need to escape invalid characters.

         text = text.replace("\n", " ")
         text = text.replace("'", "\'")
         text = text.replace("$", '\\$')
         text = text.strip()

         selector = selector +  "[normalize-space() = \""+text+"\"]"
         try:
           htmlElementsFound = root.xpath(selector)
         except Exception as ex:
           # if we failed to obtain selectors, lets use only the tag and the index
           selector = "//" + tag
           element = {}
           element["selector"] = selector
           element["index"] = elementIndex
           jsonObject["selectors"] = element
           jsonObject["numberOfElementsFoundWithSelector"] = 1
           jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 1
           jsonObject["rc"] = NO_SELECTOR_FOUND_WITH_NTAGSELECTOR
           return  jsonObject      


      else:
         if(len(attributes["text"]) > 40):
            text = attributes["text"][0:40]

         # Some characters will cause problems on the XPATH expression when using contains, we need to escape the next 
         # characters: 
         #logging.info(repr(text))
         #text = text.replace("$", '\$') // no need to escape
         text = text.replace("'", "\'")
         text = text.strip()

         selector = selector +  "[contains(text(),\""+text+"\")]"

         try:
           htmlElementsFound = root.xpath(selector)
         except Exception as ex:
           selector = "//" + tag
           element = {}
           element["selector"] = selector
           element["index"] = elementIndex
           jsonObject["selectors"] = element
           jsonObject["numberOfElementsFoundWithSelector"] = 1
           jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 1
           jsonObject["rc"] = NO_SELECTOR_FOUND_WITH_NTAGSELECTOR
           return  jsonObject      

   logger.info("buildXPATHSelector - Selector build from attributes = " + str(selector))
   htmlElementsFound = root.xpath(selector)
   numberhtmlElementsFound = len(htmlElementsFound)
   logger.info("buildXPATHSelector - numberhtmlElementsFound = " + str(numberhtmlElementsFound))
   
   if(numberhtmlElementsFound == 0 ):
      element = {}
      element["selector"] = selector
      element["index"] = 0
      jsonObject["selectors"] = element
      jsonObject["numberOfElementsFoundWithSelector"] = 0
      jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0
      jsonObject["rc"] = NO_SELECTOR_FOUND_WITH_NTAGSELECTOR        
   elif(numberhtmlElementsFound == 1 ):
      element = {}
      element["selector"] = selector
      element["index"] = 0
      jsonObject["selectors"] = element
      jsonObject["rc"] = SELECTOR_BUILD_FROM_ATTRIBUTES
      jsonObject["numberOfElementsFoundWithSelector"] = 1
      jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 1
   elif(numberhtmlElementsFound > 1 or textUsedOnSelector):
      element = {}
      element["selector"] = selector
      element["index"] = 0
      jsonObject["selectors"] = element
      jsonObject["rc"] = SELECTOR_BUILD_FROM_ATTRIBUTES
      jsonObject["numberOfElementsFoundWithSelector"] = numberhtmlElementsFound
      jsonObject["numberOfElementsFoundWithSelectorAndValue"] = numberhtmlElementsFound 


   return jsonObject

# Description:
#   This method will be call for each step and will parse the DOM files generated  
#   for the test to find the selectors for this step. If more than one selector is found,  
#   this method makes another search on the DOM using the value to filter the 
#   selectors found. 
#
# Returns:
#    jsonObject with the number of selector information. 
def obtainXPATHFeedbackFromDOM(classname, stepId, selector, index, tag, type, action, searchInfo, browserName, attributes, selector_type):
   logging.info("Starting XPATH analysis for selector " + str(selector) + " witn index " + str(index) + " on step " + str(stepId))
   jsonObject = {}    
   path = 'build/reports/geb/' + browserName + '/'
   filename = path + classname + "_" + str(stepId) + ".html"
   if os.path.exists(filename):
      try:
         searchType = searchInfo["searchType"]
         value = searchInfo["value"]
         text = open(filename, 'r').read()
         root = lxml.html.fromstring(text)
         if(selector is None):
            logging.info("No XPATH selector found, let's build from attributes")
            return buildXPATHSelector(tag, attributes, root)
         else:
            htmlElementsFound = root.xpath(selector)
            numberSelectorsFound = len(htmlElementsFound)

            if(action == "mouseover"):
               element = {}   
               element["selector"] = selector   
               element["index"] = index   
               jsonObject["selectors"] = element
               jsonObject["rc"] = ACTION_NOT_VALID_FOR_ANALYSIS
               jsonObject["numberOfElementsFoundWithSelectorAndValue"] = 0
            else:  
               if(numberSelectorsFound == 0):
                  logging.info("Found "+ str(numberSelectorsFound) + " selectors and no value to filter, let's build from attributes")
                  return buildXPATHSelector(tag, attributes, root)

               elif(numberSelectorsFound == 1 ):
                  element = {}   
                  element["selector"] = selector      
                  if(index > 0):
                     element["index"] = 0
                     returnCode = SELECTOR_FOUND_WITH_INCORRECT_INDEX
                  else:
                     element["index"] = index
                     returnCode = ONE_SELECTOR_FOUND_FOR_NTAGSELECTOR

                  jsonObject["selectors"] = element
                  jsonObject["numberOfElementsFoundWithSelectorAndValue"] = numberSelectorsFound
                  jsonObject["rc"] = returnCode
   

               elif(numberSelectorsFound > 1 ):
                  element = {}   
                  element["selector"] = selector      
                  element["index"] = index
                  returnCode = ONE_SELECTOR_FOUND_FOR_NTAGSELECTOR

                  jsonObject["selectors"] = element
                  jsonObject["numberOfElementsFoundWithSelectorAndValue"] = numberSelectorsFound
                  jsonObject["rc"] = returnCode  

            jsonObject["numberOfElementsFoundWithSelector"] = numberSelectorsFound

      except Exception as ex:
         logging.error(ex)

   # Let's validate the data we generated is a valid json for this step
   try:
     json.loads(json.dumps(jsonObject)) 
   except Exception as ex: 
     logging.error("Invalid JSON format for step " + str(stepId) +"  found, will not send feedback to BE")
     logging.error(ex) 
     logging.error(traceback.format_exc())    
     jsonObject = {}

   return jsonObject