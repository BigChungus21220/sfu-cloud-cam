# Handles all the data collection and processing

from PIL import Image
import requests
from io import BytesIO
import time
from datetime import datetime as dt

updatePeriod = 300 #seconds

time_format = "%H:%M"

assets_folder = "./assets"
masks_folder = "./masks"
output_folder = "./output"

class Camera:
    def __init__(self,name,url,shorthand,hueRange,satRange,valRange):
        self.name = name
        self.url = url
        self.shorthand = shorthand
        self.hueRange = hueRange
        self.satRange = satRange
        self.valRange = valRange
    
    # returns the image for this camera at the current time
    def getImage(self):
        response = requests.get(self.url)
        return Image.open(BytesIO(response.content)).convert('RGBA')
    
    # returns the mask image for this camera at the current time
    def getMask(self):
        return Image.open(masks_folder + "/" + self.shorthand + ".png").convert('RGBA')
    
    # returns the coverage for this camera at the current time
    def getCoverage(self):
        imagefile = self.getImage()
        mask = self.getMask()
        maskedimg = Image.alpha_composite(imagefile,mask).convert('HSV')
        width, height = maskedimg.size
            
        skyPixels = 0
        denomPixels = 0
        for x in range(width):
            for y in range(height):
                hue, sat, val = maskedimg.getpixel((x,y))
                if val > 0.1:
                    satValPoint = (sat*(100/255),val*(100/255))
                    inTri = satValPoint[1] >= (self.satRange[1] - self.valRange[0])/(self.satRange[0] - self.valRange[1])*(satValPoint[0]-self.valRange[1]) + self.valRange[0]
                    if self.hueRange[0] <= hue*(360/255) <= self.hueRange[1] and inTri:
                        skyPixels += 1
                        maskedimg.putpixel((x, y), (170,252,119))
                    else:
                        maskedimg.putpixel((x, y), (0,0,255))
                    denomPixels += 1
        imagefile.save(assets_folder + "/" + self.shorthand + ".png")
        maskedimg.convert("RGBA").save(assets_folder + "/" + self.shorthand + "_masked.png")
        return 1 - skyPixels/denomPixels

cameras = [
Camera("libraryWestCam", "http://ns-webcams.its.sfu.ca/public/images/udn-current.jpg", "libWest", (160,250), (0,100), (0,100)),
Camera("towerSouthCam", "http://ns-webcams.its.sfu.ca/public/images/towers-current.jpg", "towSouth", (160,250), (0,100), (0,100)),
Camera("towerNorthCam", "http://ns-webcams.its.sfu.ca/public/images/towern-current.jpg", "towNorth", (160,250), (0,100), (0,100)),
Camera("aqSouthEastCam", "http://ns-webcams.its.sfu.ca/public/images/aqse-current.jpg", "aqSouthEast", (160,250), (0,100), (0,100))
]

# returns the coverage given by the API
def getTrueCoverage():
    response = requests.get("https://api.lib.sfu.ca/api/weather/current")
    return response.json()["clouds"]["all"]/100.0

# collects a datapoint for all cameras + api
def updateCoverage(queue):
    timestamp = dt.now()
    print(timestamp.strftime(time_format))
    for camera in cameras:
        try:
            coverage = camera.getCoverage()
            print(camera.name + ": " + str(coverage))
            with open(output_folder + "/" + camera.shorthand + "/" + timestamp.strftime("%Y-%m-%d") + ".csv", "a") as file:
                file.write(timestamp.strftime(time_format) + "," + str(coverage) + "\n")
            queue.put({ "name": camera.name, "point": (timestamp.strftime(time_format), coverage)})
        except Exception as error:
            print(camera.name + ": connection failed")
            print(error)
    try:
        coverage = getTrueCoverage()
        print("Sfu Api: " + str(coverage))
        with open("./output/apiOutput/" + timestamp.strftime("%Y-%m-%d") + ".csv", "a") as file:
            file.write(timestamp.strftime(time_format) + "," + str(coverage) + "\n")
        queue.put({ "name": "Sfu Api", "point": (timestamp.strftime(time_format), coverage)})
    except:
        print("Sfu Api: connection failed")
    print("")

# runs every 5 minutes (ie when mod(minutes since midnight, 5) == 0)
def start(queue):
    while True:
        updateCoverage(queue)
        time.sleep(updatePeriod - time.monotonic() % updatePeriod)