from psychopy import visual, event, core, event, gui
from colour import CIECAM02_to_XYZ, sd_to_XYZ, CAM_Specification_CIECAM02, SpectralShape, XYZ_to_xy, normalised_primary_matrix, VIEWING_CONDITIONS_CIECAM02, XYZ_to_RGB
import glob
import pandas as pd
import numpy as np
import random as rd
from helperfuncs import *



#Parameters
#Distances that the two stimuli can be from each other
distancesOrdered = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 120, 150, 180]
#The length of distanced ordered. Changing this will change the amount of rows per each run in the experiment
distanceLength = 14
#Fullscreen display 0 or 1
isFull = 0
windowSize = (800, 600)
winColor = [192, 192, 192]
#Changes the amount of times that each run is repeated. For instance, at 7, there are 14 distances x 7 runs = 98 columns in the dataframe.
totalRuns = 10
#Time for each trial in frames
trialTime = 7.0
waitTime = 0.5

view_dist = 75
screen_width = 42
circle_deg = 5
distance_deg = 2
circWidth_deg = 0


#Set up dialogue box that records participant number
expName = u'targetExp' 
expInfo = {u'participant': u''}


dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel


#Create window
win = visual.Window(size=windowSize, screen = 0,fullscr = isFull, color = winColor, colorSpace = 'rgb255')


def deg_to_pix(dva,win,screen_width,view_dist):
    size_cm = view_dist*np.tan(np.deg2rad(dva/2))*2
    pix_per_cm = win.size[0]/screen_width
    size_pix = size_cm*pix_per_cm
    return int(np.round(size_pix))

#Size of the circle in pixels
circleSize = deg_to_pix(circle_deg, win,screen_width,view_dist)
distanceCircles = deg_to_pix(distance_deg, win,screen_width,view_dist)
#Positions the two circles should be in
circlePos = [(circleSize + int(distanceCircles/2), int(circleSize/2)), (-circleSize - int(distanceCircles/2), int(circleSize/2))]
#Width of the circle line in pixels
circleWidth = deg_to_pix(circWidth_deg, win,screen_width,view_dist)

#Empty lists where responses and response times will be collected
responses = []
responseTimes = []

#Angle to RGB


#Randomizes a list, and adds it to a bigger list totalRuns specified times
def listRandomizer(inputList):
    fullList = []
    for i in range(totalRuns):
        fullList.append(rd.sample(inputList, len(inputList)))
    return [item for list in fullList for item in list]

#Generate first stimuli by choosing a random element on the color wheel
#And then finding even intervals around the rest of the wheel
def generatestim1():
    fullList = []

    #Repeat process of generating random list
    for i in range(totalRuns):
    #Start at a random value on the color wheel
        start = rd.randint(0, 360)
        startcopy = start
    #Figure out how long each step across the color wheel needs to be
        interval =  360/distanceLength

        #Move up to 360 until you move past it, appending degree values to a list
        stimList = []
        while startcopy < 360:
            startcopy += interval
            if startcopy < 360:
                stimList.append(startcopy)


        #Now reset back to 0 and move up to the starting value
        begin = interval - (interval - (startcopy - 360))
        interval - (startcopy - 360)
        stimList.append(begin)
        while begin < start:
            begin += interval
            stimList.append(begin)

        #Shuffle the list and append it to the master list
        rd.shuffle(stimList)
        fullList.append(stimList)
    return [item for list in fullList for item in list]

#Takes list of RGB degrees, turns it into a list of tupled RGB values
def createRGBList(degreeList):
    rgbValues = []
    subList = []
    i = 0
    for p in degreeList:
        subList.append(tuple((angle_to_rgb(p)*255)))
        i += 1
        if i == 2:
            rgbValues.append(subList)
            subList = []
            i = 0
    return rgbValues

#Put the circle objects themselves into a list of tuples, 1 tuple for each presentation (2 shapes in each tuple)
def createColors(rgbValues, win):
    circles = []
    for n, color in enumerate(rgbValues):
        a = []
        for i, pos in enumerate(circlePos):
            a.append(visual.Circle(win = win, fillColor = color[i], lineWidth= circleWidth, size = circleSize, units = 'pix', pos = pos, colorSpace = 'rgb255'))
        circles.append(tuple(a))
    return circles


#End experiment if q is pressed
def abort_key(win):
    keys = event.getKeys(keyList = 'q')
    if keys:
        if(keys[-1]) == 'q':
            win.close()
            core.quit()


#Collects the response and response time for each stimulus, stores this in the dataframe
def collectResponses():
    responses.append(ratingScale.getRating())
    responseTimes.append(ratingScale.getRT())

#Takes two lists and creates a third list that alternates between the elements of the list
#Used to combine the lists for stim1 and stim2 so they are in the correct order of presentation
def intertwinedList(deg1, deg2):
    result = [None]*(len(deg1)+len(deg2))
    result[::2] = deg1
    result[1::2] = deg2
    return result

def setRun():
    runs = []
    runNumber = 1
    for i in range(totalRuns):
        for i in range(distanceLength):
            runs.append(runNumber)
        runNumber += 1
    return runs


def drawExp(win, ratingScale):
    while ratingScale.noResponse:
        for i in im:
            i.draw()
        ratingScale.draw()
        win.flip()
        abort_key(win)
    collectResponses()
    ratingScale.reset()
    abort_key(win)




#Set up values in trial matrix
trialmat = pd.DataFrame(columns=['participant','run','stim1Deg', 'distanceDeg', 'stim2Deg', 'response', 'RT'])
trialmat['distanceDeg'] = listRandomizer(distancesOrdered)
trialmat['stim1Deg'] = generatestim1()
trialmat['stim2Deg'] = abs(trialmat['stim1Deg'] - trialmat['distanceDeg'])
intertwinedList = intertwinedList(trialmat['stim1Deg'], trialmat['stim2Deg'])
rgbList = createRGBList(intertwinedList)
trialmat['run'] = setRun()


#Create shape objects
rgbs = createColors(rgbList, win)
ratingScale = visual.RatingScale(win, low = 1, high = 7, markerStart = 4, leftKeys = 'left', rightKeys = 'right', acceptKeys = 'z', marker = 'triangle', markerColor = 'black', scale = '1 = Disimilar, 7 = Similar', textColor = 'black')


trialmat['participant'] = expInfo['participant']

#Get frame rate
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

#Get trial frames
trialFrames = int(trialTime/frameDur)
waitFrames = int(waitTime/frameDur)



for trial, im in enumerate(rgbs):
    for frame in range(waitFrames):
        win.flip()
    #Turn this into a function
    drawExp(win, ratingScale)


trialmat['response'] = responses
trialmat['RT'] = responseTimes

trialmat.to_csv('test')




