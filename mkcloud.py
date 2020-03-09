from PIL import Image
import os

def resizeImages(browserName):
  try:
    path = 'build/reports/geb/'+browserName
    for filename in os.listdir(path):
      if filename.endswith('.png'):
        im = Image.open(path+"/"+filename)
        size =im.size   # get the size of the input image
        ratio = 0.60  # reduced the size to 60% of the input image
        reduced_size = int(size[0] * ratio), int(size[1] * ratio)

        im_resized = im.resize(reduced_size, Image.ANTIALIAS)
        im_resized.save(path+"/"+filename, "PNG")
  except Exception as e:
    print("There was an error during resize ")
    print(e)
  return('complete')

def gatherScreenshots(browserName):
  final = {}
  try:
    path = 'build/reports/geb/'+browserName
    fileNames = []
    files = []
    for filename in os.listdir(path):
      if filename.endswith('.png'):
        files.append(open(path + '/' + filename, 'rb'))
        fileNames.append('file')
    final = zip(fileNames, files)
  except Exception as e:
    print("There was an error gathering screenshots ")
    print(e)
    final = {}
  return(final)
