from PIL import Image
import os

def resizeImages(browserName):
  path = 'build/reports/geb/'+browserName
  for filename in os.listdir(path):
    if filename.endswith('.png'):
      im = Image.open(path+"/"+filename)
      size =im.size   # get the size of the input image
      ratio = 0.4  # reduced the size to 40% of the input image
      reduced_size = int(size[0] * ratio), int(size[1] * ratio)

      im_resized = im.resize(reduced_size, Image.ANTIALIAS)
      im_resized.save(path+"/"+filename, "PNG")
  return('complete')

def gatherScreenshots(browserName):
  path = 'build/reports/geb/'+browserName
  fileNames = []
  files = []
  for filename in os.listdir(path):
    if filename.endswith('.png'):
      files.append(open(path + '/' + filename, 'rb'))
      fileNames.append('file')
  # files.append(open('video.mp4'))
  final = zip(fileNames, files)
  return(final)

def getCloudKey():
  return('lkussv97qginpidrtoey-1ec3r3678pe7n0wulh1v9k-zthz8er1ukl59ux1k0epop-mioxpeadsu5iegbjhd4j4')
