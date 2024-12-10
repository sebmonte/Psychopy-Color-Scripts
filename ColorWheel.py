import math
import numpy as np
import random as rd
from psychopy import visual, event, core, event, gui
from angles_to_rgb import ciecam02_to_rgb
import pandas as pd



#Check if file already exists in gui where you put in session + participant number,
#Ask if sure you want this

path_to_gamutmeasurement = 'data_init_avg.pkl' 

#Fullscreen display 0 or 1
isFull = 0
#If not fullscreen, windowed size
windowSize = (800, 600)
# winColor = [192, 192, 192]
winColor = .5 #call ciecam02 to rgb function

waitFrames = 15 #half second

colorWheelCircle_deg = .5
selector_deg = .6
feedback_circle_deg = 3

view_dist = 78.5
screen_width = 42


#Sets the windowscreen as full or if not sets the dimensions of the windowed screen
if isFull:
    win = visual.Window(screen = 0,fullscr = isFull, color = winColor, colorSpace = 'rgb1')
else:
    win = visual.Window(size=windowSize, screen = 0,fullscr = isFull, color = winColor, colorSpace = 'rgb1')

def deg_to_pix(dva,win,screen_width,view_dist):
    size_cm = view_dist*np.tan(np.deg2rad(dva/2))*2
    pix_per_cm = win.size[0]/screen_width
    size_pix = size_cm*pix_per_cm
    return int(np.round(size_pix))

circleSize = deg_to_pix(colorWheelCircle_deg, win, screen_width, view_dist)
feedbackSize = deg_to_pix(feedback_circle_deg, win, screen_width, view_dist)
feedbackPos = (int(feedbackSize*3), int(feedbackSize*2.5))
selectorSize = deg_to_pix(selector_deg, win, screen_width, view_dist)


#Converts angles to radial, returns two lists of x and y coordinates
def angleToRad(ncolors = 360, radius  = 150):
    theta = np.linspace(0,359,ncolors)

    # Converting theta from degree to radian
    theta = [t * math.pi/180.0 for t in theta]

    # Converting polar to cartesian coordinates
    x = [radius * math.cos(t) for t in theta]
    y = [radius * math.sin(t) for t in theta]

    return(x, y)



#Takes in two lists, returns one list that takes one value from each, turns them into a sublist,
#then appends the sublist to a master list that is ultimately returned
def intertwinedList(deg1, deg2):
    angles = []

    for i, element in enumerate(deg1):
        angles.append([element, deg2[i]])
    return angles

#Returns a list of angles between 0 and 359
def ColorAngles():
    return np.linspace(0, 360, 360, dtype=int, endpoint = False)

#Converts color angles to RGB values and returns them with one sublist per RGB triplet
def anglesToRgb():
    #Defines the list of color angles to be converted
    colors = ColorAngles()
    RGBs = []
    for i in colors:
        rgb, _, _, _ = ciecam02_to_rgb(path_to_gamutmeasurement, h = i) #Run with J as 0 to get grey
        RGBs.append(rgb)
    return RGBs

#Creates the list of color objects for the colored circle
def createColors(rgbs, coordinates, win):
    colors = []
    for i, element in enumerate(rgbs):
        element2 = element.tolist()
        colors.append(visual.Circle(win = win, fillColor = element2, lineWidth= 0, size = circleSize, units = 'pix', pos = coordinates[i], colorSpace = 'rgb255'))
    return colors

#Create the list of rgb values for the color wheel
rgbList = anglesToRgb()
#Creates the x and y coordinates for the color wheel
x, y = angleToRad()

#Creates the list of angles (length of 360) for each rgb value
angleList2 = intertwinedList(x, y)

#Creates a list of color values for the wheel
colorList = createColors(rgbList, angleList2, win)


#Turns the selector circle left along the wheel a specified number of angle steps, returns the new position of the circle
def turnLeft(currentPos, moveAmount = 3):
    newPos = currentPos + moveAmount
    if newPos > 359:
        newPos = 0
    selector.pos = angleList2[newPos]
    return newPos

#Same but left
def turnRight(currentPos, moveAmount = 3):
    newPos = currentPos - moveAmount
    if newPos < 0:
        newPos = 359
    selector.pos = angleList2[newPos]
    return newPos

#Ends the experiment if q is pressed
def abort_key(win, targets, choices):
    keys = event.getKeys(keyList = 'q')
    if keys:
        if(keys[-1]) == 'q':
            trialmat = generateTrialmat(targets, choices)
            save_data(trialmat)
            #win.mouseVisible = True
            win.close()
            core.quit()

#Creates a list of numerical values for the stimuli choices (represented as color angles) and shuffles them
def create_stimuli_choices():
    #Defines what color angles to choose for stimuli
    colors = ColorAngles()
    rd.shuffle(colors)
    return colors
    
def generateTrialmat(targets, choices):
    trialmat = pd.DataFrame(columns=['targetList', 'chosenStimuli'])
    trialmat['targetList'] = targets
    chosen_stimuli = pd.Series(choices[:len(trialmat['targetList'])])
    chosen_stimuli = chosen_stimuli.append(pd.Series([pd.np.nan] * (len(trialmat['targetList']) - len(chosen_stimuli))), ignore_index=True)

# add the 'chosenStimuli' column to the data frame
    trialmat['chosenStimuli'] = chosen_stimuli
    return trialmat


def getKeys(currentPos, endPoint):
    if event.getKeys(keyList = '1'):
        currentPos = turnRight(currentPos)
        print( 'correct pos is' + str(currentPos))
        return currentPos, endPoint
    elif event.getKeys(keyList = '2'):
        currentPos = turnLeft(currentPos)
        print( 'correct pos is' + str(currentPos))
        return currentPos, endPoint
    elif event.getKeys(keyList = '3'):
        chosenStimuli.append(currentPos)
        endPoint = True
        return currentPos, endPoint
    return currentPos, endPoint

def drawStimuli(colorList, selector, currentCircle, targetCircle, currentPos):
    for j in range(len(colorList)):
        colorList[j].draw()
    selector.draw()
    currentCircle.setColor(rgbList[currentPos])
    currentCircle.draw()
    targetCircle.draw()

#Needs updating. Format to save the trialmat
def save_data(trialmat):
    participant = 'test'
    session = 'test'
    trialmat.to_csv(f"./results2/P{participant}_S{session}.csv")



#Start the selector at a randompoint on the circle
currentPos = rd.randint(0, 359)

#Selector is the shape around the chosen circle, currentCircle displays the currently selected circle
#targetCircle displays the target circle
selector = visual.Circle(win = win, fillColor = None, lineColor='black',lineWidth= 5, size = selectorSize, units = 'pix', pos = angleList2[currentPos], colorSpace = 'rgb255', opacity = .25)
currentCircle = visual.Circle(win = win, fillColor = rgbList[currentPos], lineWidth= 0, size = feedbackSize, units = 'pix', pos = feedbackPos, colorSpace = 'rgb255')
targetCircle = visual.Circle(win = win, fillColor = rgbList[currentPos], lineWidth= 0, size = feedbackSize, units = 'pix', pos = (0, 0), colorSpace = 'rgb255')

#Created a randmonly ordered list of targets, initalize the list where the choices will be recorded
targetList = create_stimuli_choices()
chosenStimuli = []

#Go through the list of targets, set the color of the displayed target circle
for i in targetList:
    targetCircle.setColor(rgbList[i])
    endPoint = False
    #Continue to draw the stimuli and look for key responses until a circle is selected, then go to the next target
    #in the outer loop
    while endPoint == False:
        drawStimuli(colorList, selector, currentCircle, targetCircle, currentPos)
        currentPos, endPoint = getKeys(currentPos, endPoint)
        abort_key(win, targetList, chosenStimuli)
        win.flip()
    for frame in range(waitFrames):
        win.flip()

trialmat = generateTrialmat(targetList, chosenStimuli)
save_data(trialmat)
win.close()
core.quit()
