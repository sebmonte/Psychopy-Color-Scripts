from psychopy import visual, event, core, event, gui
from colour import CIECAM02_to_XYZ, sd_to_XYZ, CAM_Specification_CIECAM02, SpectralShape, XYZ_to_xy, normalised_primary_matrix, VIEWING_CONDITIONS_CIECAM02, XYZ_to_RGB
import glob
import random as rd
import pandas as pd
import numpy as np
import sys
from Generatetarget import *
from angle_to_rgb import *

sys.path.insert(0, 'C:/Users/meglab/EExperiments/Lina/colour_geometry/local_functions')
from angles_to_rgb import ciecam02_to_rgb
path_to_gamutmeasurement = 'data_init_avg.pkl' 

totalRuns = 1


# this is for the button box in the MEG -- cable has to go towards the participant (blue button on the left)
left_key = '1'
right_key = '3'

#How many targets we want
totalTargets = 5

#How many targets we want per session
targets = 1

sessionLength = int(totalTargets/targets)
#List of targets to use for this participant. UPDATE WHEN NEW PARTICIPANT USING GENERATETARGET.PY
targetList = [278.0, 242.0, 269.0, 116.0, 170.0]
stim1Distances = [0, 3, 5, 8, 10, 13, 15, 20, 25, 30, 35, 45, 55, 65, 75, 85, 100, 120, 140, 160, 180]
#How many pairs there are for each target
presentations = 87

#Fullscreen display 0 or 1
isFull = 0

windowSize = (800, 600)
# winColor = [192, 192, 192]
winColor = .5
#Time for each trial in frames
trialTime = 7.0
waitTime = 0
feedbackTime = 0.3


view_dist = 78.5
screen_width = 42
circle_deg = 5
feedback_circle_deg = 7
distance_deg = 2
linHeightDeg = .25
linWidthDeg = 15

#Set up dialogue box that records participant number
expName = u'targetExp' 
expInfo = {u'participant': u'test',u'session': u'1'}

dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel

#Create window
if isFull:
    win = visual.Window(screen = 0,fullscr = isFull, color = winColor, colorSpace = 'rgb1')
    
else:
    win = visual.Window(size=windowSize, screen = 0,fullscr = isFull, color = winColor, colorSpace = 'rgb1')

def deg_to_pix(dva,win,screen_width,view_dist):
    size_cm = view_dist*np.tan(np.deg2rad(dva/2))*2
    pix_per_cm = win.size[0]/screen_width
    size_pix = size_cm*pix_per_cm
    return int(np.round(size_pix))

#Size of the circle in pixels
circleSize = deg_to_pix(circle_deg, win,screen_width,view_dist)
feedbackcircleSize = deg_to_pix(feedback_circle_deg, win,screen_width,view_dist)
distanceCircles = deg_to_pix(distance_deg, win,screen_width,view_dist)

#Look up where on circle position calculation starts from ie. if it's bottom left add half of the size of the circle
#Try things like holding button pressing two see how it might break, check output
#Positions the two circles should be in
circlePos = [(0, int(circleSize)), (circleSize + int(distanceCircles/2), -int(circleSize)), (-circleSize - int(distanceCircles/2), -int(circleSize))]
circlePos2 = [(0, int(circleSize)), (-circleSize - int(distanceCircles/2), -int(circleSize)),(circleSize + int(distanceCircles/2), -int(circleSize))]

#Line variables (settings for the black line separating the circles)
linePos = (0, 0)
lineColor = (0, 0, 0)
linHeight = deg_to_pix(linHeightDeg, win,screen_width,view_dist)
linWidth = deg_to_pix(linWidthDeg, win,screen_width,view_dist)

#Empty lists where responses and response times will be collected
responses = []
responseTimes = []




#Creates a dictionary mapping the distances of the first offset from the target to the possible distances the second offset might have from that first offset.
#For instance, {0: [3, 5, 8, 10, 25], 3: [5, 8, 10, 13, 30]}
def shuffleStim():
    firstDict = {}
    for stim, p in enumerate(stim1Distances):
        stimSubList = stim1Distances[stim+1:stim+5:1]
        try:
                stimSubList = stimSubList + [stim1Distances[stim+8]]
        except:
                stimSubList = stimSubList
        rd.shuffle(stimSubList)
        firstDict [p] = stimSubList

    shuffled = list(firstDict.items())
    rd.shuffle(shuffled)    
    return dict(shuffled)

#Takes a dictionary generated in shufflestim and turns it into two lists, one with the distance values for the first stimulus from the target, and one with the
#Distance values for the second stimulus from the target
def createDistances(stimDict):
    stimList1 = []
    stimList2 = []
    for i in stimDict.keys():
        multiplier = len(stimDict[i])
        stimList1.extend([i] * multiplier)
        stimList2.extend(stimDict[i])
    return stimList1, stimList2


#Takes in the amount of targets, and for each target generates the corresponding distances from the stimuli the target will be in two lists
#Ultimately generates the rows in the dataframe for each distance measure, one row for each presentation
def multiplyDistances():
    masterStim1 = []
    masterStim2 = []
    for i in range(targets):
        dict1 = {}
        stimList1 = []
        stimList2 = []
        dict1 = shuffleStim()
        stimList1, stimList2 = createDistances(dict1)
        masterStim1.extend(stimList1)
        masterStim2.extend(stimList2)
    print(len(masterStim1))
    return masterStim1, masterStim2


#Looks at the current session for the participant, and then pulls out a set of stimuli to use from the total target list for that participant
def sampleTarget():
    session = int(expInfo['session'])
    firstList = targetList
    return firstList[session - 1::sessionLength]
    

#Takes the list of targets, duplicates it the amount of times needed for the experiment. 
#'Presentations' is equal to the amount of pairs that there are for each target
def generateTarget2(presentations):
    firstList = sampleTarget()
    secondList = []
    for i in firstList:
        secondList.extend([i]* presentations)
    
    return secondList


#Takes three lists and returns a list that alternates between each element ie, takes the first from the first, second from second, third from third, fourth from first...
#Used to combine the three lists of degree angles for the color (target, stim1 and stim2)
def intertwinedList(deg1, deg2, deg3):
    result = [None]*(len(deg1)+len(deg2) + len(deg3))
    result[::3] = deg1
    result[1::3] = deg2
    result[2::3] = deg3
    return result

#Takes list of color degrees, turns it into a list of tupled RGB values
def createRGBList(degreeList):
    rgbValues = []
    subList = []
    i = 0
    for p in degreeList:
        prgb, _, _, _ = ciecam02_to_rgb(path_to_gamutmeasurement, h = p)
        prgb2 = tuple(prgb/255)
        subList.append(prgb2) #ask lina if this is right
        print(subList)
        i += 1
        if i == 3:
            rgbValues.append(subList)
            subList = []
            i = 0
    return rgbValues


### MAKE SPIRALS
def mkR(size, exponent=1):
    origin = ((size[0]+1)/2., (size[1]+1)/2.)

    xramp, yramp = np.meshgrid(np.arange(1, size[1]+1)-origin[1],
                               np.arange(1, size[0]+1)-origin[0])
    res = (xramp ** 2 + yramp ** 2) ** (exponent / 2.0)
    return res

def mkAngle(size, phase=0):
    origin = ((size[0]+1)/2., (size[1]+1)/2.)
    xramp, yramp = np.meshgrid(np.arange(1, size[1]+1)-origin[1],
                               np.arange(1, size[0]+1)-origin[0])
    xramp = np.array(xramp)
    yramp = np.array(yramp)
    res = np.arctan2(yramp, xramp)
    return ((res+(np.pi-phase)) % (2*np.pi)) - np.pi

def log_polar_grating(size, w_r=0, w_a=0, phi=0, ampl=1, color=[1,0,0], bgr_color = [0,0,0],theta=0):
    size = (size, size)
    origin = ((size[0]+1)/2., (size[1]+1)/2.)
    rad = mkR(size)
    if 0 in rad:
        rad += 1e-12
    lrad = np.log2(rad**2)
    theta = mkAngle(size,theta)
    grating = ampl * np.cos(((w_r * np.log(2))/2) * lrad + w_a * theta + phi)
    grating = np.clip(np.repeat(grating[:,:,np.newaxis],3,axis=2),0,1)

    # hard edges
    grating[grating>0] = 1
    # add color
    grating = grating*color
    grating[np.sum(grating,axis=2)==0]=bgr_color

    # add circular mask
    masked_img = grating.copy()
    
    # use the smallest distance between the center and image walls
    radius = min(origin[0], origin[1], size[0]-origin[0], size[1]-origin[1])
    Y, X = np.ogrid[:size[0], :size[1]]
    dist_from_center = np.sqrt((X - origin[0])**2 + (Y-origin[1])**2)
    mask = dist_from_center <= radius
    masked_img[~mask] = bgr_color

    return masked_img


def createColors(rgbValues, win, lftrgt):
    circles = []
    LftRgtCounter = 0
    for n, color in enumerate(rgbValues):
        a = []
        if lftrgt[LftRgtCounter] == 1:
            for i, pos in enumerate(circlePos):
                grating = log_polar_grating(circleSize, w_r=15, w_a=8, phi=0, ampl=1, color=color[i], bgr_color=win.color, theta=0)
                a.append(visual.ImageStim(win,image=grating,size=(grating.shape[0],grating.shape[1]),units='pix',colorSpace='rgb1',pos=pos))


                # a.append(visual.Circle(win = win, fillColor = color[i], lineWidth= 0, size = circleSize, units = 'pix', pos = pos, colorSpace = 'rgb255'))
            circles.append(tuple(a))
        else:
            for i, pos in enumerate(circlePos2):
                grating = log_polar_grating(circleSize, w_r=15, w_a=8, phi=0, ampl=1, color=color[i], bgr_color=win.color, theta=0)
                a.append(visual.ImageStim(win,image=grating,size=(grating.shape[0],grating.shape[1]),units='pix',colorSpace='rgb1',pos=pos))

                #a.append(visual.Circle(win = win, fillColor = color[i], lineWidth= 0, size = circleSize, units = 'pix', pos = pos, colorSpace = 'rgb255'))
            circles.append(tuple(a))
        LftRgtCounter += 1
    return circles

def generateStim(target, dist1):
    stim1 = []
    for i, p in enumerate(target):
        if p + dist1[i] > 360:
            reset = (p + dist1[i]) - 360
            stim1.append(0 + reset)
        else:
            stim1.append(p + dist1[i])
    return stim1


#Randomizes whether the trials occur with the right answer on the left or the right
def leftorright(presentations, target):
    dataFrameRows = presentations*target
    if target%2 == 0:
        onesandzeros = [0] * int(dataFrameRows/2) + [1] * int(dataFrameRows/2) 
    else: 
        onesandzeros = [0] * int(dataFrameRows/2) + [1] * int(dataFrameRows/2) + [0]
    rd.shuffle(onesandzeros)
    return onesandzeros

def recordKey(trialmat,trial,response,responsetime):
    trialmat.loc[trial,'response'] = response
    trialmat.loc[trial,'rt'] = responsetime
    return trialmat


#End experiment if q is pressed
def abort_key(win,trialmat):
    keys = event.getKeys(keyList = 'q')
    if keys:
        if(keys[-1]) == 'q':
            save_data(trialmat)
            win.mouseVisible = True
            win.close()
            core.quit()

def drawExp(win, line,trialmat):
    for i in im:
        i.draw()
        line.draw()
    fliptime = win.flip()
    resp = event.waitKeys(keyList = [left_key, right_key],timeStamped=True)

    response = resp[0][0]
    responsetime = resp[0][1]-fliptime

    trialmat = recordKey(trialmat,trial,response,responsetime)
    abort_key(win,trialmat)

    return trialmat

def create_result_column(df):
    df['result'] = df.apply(lambda row: 'correct' if row['correctAns'] == 0 and row['response'] == left_key or row['correctAns'] == 1 and row['response'] == right_key else 'incorrect', axis=1)
    return df

def generate_trialmat():
    trialmat = pd.DataFrame(columns=['target', 'dist1', 'dist2', 'stim1', 'stim2','response','rt'])
    trialmat['dist1'], trialmat['dist2'] = multiplyDistances()
    trialmat['target'] = generateTarget2(presentations)
    trialmat['stim1'] = generateStim(trialmat['target'], trialmat['dist1'])
    trialmat['stim2'] = generateStim(trialmat['target'], trialmat['dist2'])
    trialmat['choicesDist'] = trialmat['dist2'] - trialmat['dist1']
    trialmat['correctAns'] = leftorright(presentations, targets)
    trialmat = trialmat.sample(frac = 1).reset_index(drop=True)
    trialmat['participant'] = expInfo['participant']
    trialmat['session'] = expInfo['session']
    return trialmat

trialmat = generate_trialmat()


#Creates a circle around the color that the participant selected
def show_color_clicked(trial,feedback_frames,trialmat):
    feedback_circle = visual.Circle(win = win, fillColor = None, lineColor='black',lineWidth= 5, size = feedbackcircleSize, units = 'pix', pos = (0,0), colorSpace = 'rgb1')
    if trialmat.loc[trial,'response'] == left_key:
        feedback_circle.pos = (-circleSize - int(distanceCircles/2), -int(circleSize))
    else:
        feedback_circle.pos = (circleSize + int(distanceCircles/2), -int(circleSize))

    for _ in range(feedback_frames):
        for i in im:
            i.draw()
        line.draw()
        feedback_circle.draw()

        win.flip()

def save_data(trialmat):
    trialmat = create_result_column(trialmat)
    trialmat.to_csv(f"./results/P{trialmat.loc[0,'participant']}_S{trialmat.loc[0,'session']}.csv")



#Create a long list that contains all of the RGB values for the colors that will be shown, in order of presentation
intertwinedList = intertwinedList(trialmat['target'], trialmat['stim1'], trialmat['stim2'])
rgbList = createRGBList(intertwinedList)

#Create shape objects
rgbs = createColors(rgbList, win, trialmat['correctAns'])
line = visual.Rect(win, width = linWidth, height=linHeight, units='pix', lineWidth=linWidth, lineColor=None, 
    fillColor=lineColor, pos=linePos, colorSpace='rgb1')


#Get frame rate
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

#Get trial frames
trialFrames = int(trialTime/frameDur)
waitFrames = int(waitTime/frameDur)
feedback_frames = int(feedbackTime/frameDur)

win.mouseVisible = False

for trial, im in enumerate(rgbs):
    for frame in range(waitFrames):
        win.flip()
    #Draw colors on the screen
    trialmat = drawExp(win, line,trialmat)

    # show which colour was clicked
    show_color_clicked(trial,feedback_frames,trialmat)

    #Draw break screens every 87 presentations
    if (trial + 1)%87 == 0:
        waitScreen = visual.TextStim(win, text = 'you just finished trial ' + str(int((trial + 1)/87)) + ' of ' + str(targets) + '. take a break! Press any button to continue.', pos=(0.0, 0.0))
        waitScreen.draw()
        win.flip()
        waitResp = event.waitKeys(keyList = None,timeStamped=True)


win.mouseVisible = True
save_data(trialmat)