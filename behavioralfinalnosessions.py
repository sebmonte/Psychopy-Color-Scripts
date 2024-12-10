from psychopy import visual, event, core, event, gui
from colour import CIECAM02_to_XYZ, sd_to_XYZ, CAM_Specification_CIECAM02, SpectralShape, XYZ_to_xy, normalised_primary_matrix, VIEWING_CONDITIONS_CIECAM02, XYZ_to_RGB
import time
import random as rd
import pandas as pd
import numpy as np
import sys
import os

#Fullscreen display 0 or 1
isFull =0


#How many times we duplicate all targets, always 1 for this expq
totalRuns = 1

test = pd.read_csv('testdistances.csv')

stim_folder = '../stimuli'

# this is for the button box in the MEG -- cable has to go towards the participant (blue button on the left)
left_key = '1'
right_key = '3'

#How many targets we want
totalTargets = 45

#How many targets we want per session
targets = 45

#sessionLength = int(totalTargets/targets)
sessionLength = totalTargets

#Set up dialogue box that records participant number
expName = u'targetExp' 
expInfo = {u'participant': u'test',u'session': u'1'}

dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel


#Check if a file path with participant number and session already exists,
#if it does warn and ask if ok
if not os.path.exists('./results'):
        os.makedirs('./results')
if os.path.exists(f"./results/P{expInfo['participant']}_S{expInfo['session']}.csv"):
    dlgQ = gui.Dlg(title="File already exists. Proceed?")
    proceed = dlgQ.show()
    if dlgQ.OK == False:
        core.quit()


#Function to generate targets, returns list of specified number of targets 
def generateTarget(totalRuns, totalTargets):
    fullList = []

    #Repeat process of generating random list
    for i in range(totalRuns):
    #Start at a random value on the color wheel
        start = rd.randint(0, 360)
        startcopy = start
    #Figure out how long each step across the color wheel needs to be
        interval =  360/totalTargets

        #Move up to 360 until you move past it, appending degree values to a list
        stimList = []
        while startcopy <= 360:
            startcopy += interval
            if startcopy <= 360:
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


#If first session, generate a new set of targets, or else use already existing file
targetList = []
with open('targetfile.text', 'r') as filehandle:
    for line in filehandle:
        place = line[:-1]
        targetList.append(float(place))
            
                        
                             
#How many pairs there are for each target
presentations = int(len(test['s1_dist']))

windowSize = (800, 600)
winColor= pd.read_csv('../stimuli/background_grey.csv').loc[:,'0'].to_numpy()

#Time for each trial in frames
trialTime = 7.0
firstwaitTime = 1
waitTime = .5
isiTime = .3
itiTime = .3
feedbackTime = 0.2
spiralTime = 0.4



#Create window
if isFull:
    win = visual.Window(screen = 0,fullscr = isFull, color = winColor, colorSpace = 'rgb255')
else:
    win = visual.Window(size=windowSize, screen = 0,fullscr = isFull, color = winColor, colorSpace = 'rgb255')


#Empty lists where responses and response times will be collected
responses = []
responseTimes = []

#Looks at the current session for the participant, and then pulls out a set of stimuli to use from the total target list for that participant
def sampleTarget():
    session = int(expInfo['session'])
    firstList = targetList
    return firstList[session - 1::sessionLength]
    

#Takes the list of targets, duplicates it the amount of times needed for the experiment. 
#'Presentations' is equal to the amount of pairs that there are for each target
def generateTarget2(presentations):
    #firstList = sampleTarget()
    firstList = targetList
    secondList = []
    for i in firstList:
        secondList.extend([i]* presentations)
    
    print(len(secondList))
    return secondList



#Multiplies the file containing the dist1 and dist2 values times the amount of trials we need per target
def generateDist():
    masterStim1 = []
    masterStim2 = []
    for i in range(targets):
        stimList1 = []
        stimList2 = []
        stimList1, stimList2 = test['s1_dist'], test['s2_dist']
        masterStim1.extend(stimList1)
        masterStim2.extend(stimList2)
    return masterStim1, masterStim2


def generateStim(target, dist1):
    stim1 = []
    for i, p in enumerate(target):
        if p + dist1[i] >= 360:
            reset = (p + dist1[i]) - 360
            stim1.append(0 + reset)
        elif p + dist1[i] < 0:
            reset = 360 + (p + dist1[i])
            stim1.append(reset)
        else:
            stim1.append(p + dist1[i])
    assert 360 not in stim1
    return stim1


#Randomizes whether the trials occur with the right answer on the left or the right
def leftorright(presentations, target):
    dataFrameRows = presentations*target
    if dataFrameRows%2 == 0:
        onesandzeros = [0] * int(dataFrameRows/2) + [1] * int(dataFrameRows/2) 
    else: 
        onesandzeros = [0] * int(dataFrameRows/2) + [1] * int(dataFrameRows/2) + [0]
    rd.shuffle(onesandzeros)
    return onesandzeros



#End experiment if q is pressed
def abort_key(win,trialmat):
    keys = event.getKeys(keyList = 'q')
    if keys:
        if(keys[-1]) == 'q':
            save_data(trialmat)
            win.mouseVisible = True
            win.close()
            core.quit()



def create_result_column(df):
    df['result'] = df.apply(lambda row: 'correct' if row['correctAns'] == 0 and row['response'] == left_key 
                            or row['correctAns'] == 1 and row['response'] == right_key else 'incorrect', axis=1)
    return df

def generate_trialmat():
    trialmat = pd.DataFrame(columns=['target', 'dist1', 'dist2', 'stim1', 'stim2','response','rt'])
    trialmat['target'] = generateTarget2(presentations)
    print(len(trialmat['target']))
    trialmat['dist1'], trialmat['dist2'] = generateDist()
    trialmat['stim1'] = generateStim(trialmat['target'], trialmat['dist1'])
    trialmat['stim2'] = generateStim(trialmat['target'], trialmat['dist2'])
    trialmat['choicesDist'] = abs(trialmat['dist2'] - trialmat['dist1'])
    ## TODO: consider making correctAns to be "left/right" and response as well! 
    trialmat['correctAns'] = leftorright(presentations, targets)
    trialmat = trialmat.sample(frac = 1).reset_index(drop=True)
    trialmat['participant'] = expInfo['participant']
    trialmat['session'] = expInfo['session']
    trialmat['accuracy'] = 0
    trialmat['response'] = 0
    trialmat['responseKey'] = 0

    trialmat['target_im'] = [f'{stim_folder}/stim_spiral_H{i}_J40.png' for i in trialmat.target.astype(int).to_numpy()]
    trialmat['stim1_im'] = [f'{stim_folder}/stim_spiral_H{i}_J40.png' for i in trialmat.stim1.astype(int).to_numpy()]
    trialmat['stim2_im'] = [f'{stim_folder}/stim_spiral_H{i}_J40.png' for i in trialmat.stim2.astype(int).to_numpy()]
    return trialmat

trialmat = generate_trialmat()

def save_data(trialmat):
    trialmat = create_result_column(trialmat)
    

    trialmat.to_csv(f"./results/P{trialmat.loc[0,'participant']}_S{trialmat.loc[0,'session']}.csv")




#Get frame rate
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

#Get trial frames
isiFrames = int(isiTime/frameDur)
itiFrames = int(itiTime/frameDur)
feedback_frames = int(feedbackTime/frameDur)
spiral_frames = int(spiralTime/frameDur)

win.mouseVisible = False


introScreen = visual.TextStim(win, text = 'Reminder: In this experiment, you will view a center spiral for a short time and then decide whether the left or right choice is more similar in color to that center spiral. Press any button to begin',pos=(0.0, 0.0))
introScreen.draw()
win.flip()
introResp = event.waitKeys(keyList = None,timeStamped=True)


## create visual stimuli 
from PIL import Image


im = trialmat.loc[0,'target_im']
image = Image.open(im)
stim_size = image.size


target = visual.ImageStim(win,image=im,units='pix',size=stim_size)
stim_left = visual.ImageStim(win,image=im,units='pix',pos=(-stim_size[0],0),size=stim_size)
stim_right = visual.ImageStim(win,image=im,units='pix',pos=(stim_size[0],0),size=stim_size)

choice_circle = visual.Circle(win,size=(int(stim_size[0]*1.2),int(stim_size[1]*1.2)),units='pix',lineColor='black',lineWidth = 5, fillColor=None, opacity=0.8)

trialmatLen = len(trialmat)
init = time.time()
for trial in range(len(trialmat)):
    if trial == 629:
        t_630trials = time.time() - init
    target.image = trialmat.loc[trial,'target_im']
    if trialmat.loc[trial,'correctAns'] == 1:
        stim_right.image = trialmat.loc[trial,'stim1_im']
        stim_left.image = trialmat.loc[trial,'stim2_im']
    else:
        stim_right.image = trialmat.loc[trial,'stim2_im']
        stim_left.image = trialmat.loc[trial,'stim1_im']

    # ITI
    for frame in range(itiFrames):
        win.flip()

    # target presentation
    for _ in range(spiral_frames):
        target.draw()
        win.flip()

    # ISI
    for _ in range(isiFrames):
        win.flip()


    # options presentation
    stim_right.draw()
    stim_left.draw()
    fliptime = win.flip()

    resp = event.waitKeys(keyList = [left_key, right_key],timeStamped=True)
    trialmat.loc[trial,'response'] = resp[0][0]
    trialmat.loc[trial,'rt'] = resp[0][1]-fliptime

    
    if (trialmat.loc[trial,'response'] == left_key):
        trialmat.loc[trial,'responseKey'] = 'left'
    if (trialmat.loc[trial,'response'] == right_key):
        trialmat.loc[trial,'responseKey'] = 'right'


    if (trialmat.loc[trial,'response'] == left_key) and (trialmat.loc[trial,'correctAns'] == 0):
        trialmat.loc[trial,'accuracy'] = 1
    if (trialmat.loc[trial,'response'] == right_key) and (trialmat.loc[trial,'correctAns'] == 1):
        trialmat.loc[trial,'accuracy'] = 1

    abort_key(win,trialmat)


    # show feedback (i.e., what was clicked)
    if (trialmat.loc[trial,'response'] == left_key):
        choice_circle.pos = stim_left.pos
    elif (trialmat.loc[trial,'response'] == right_key):
        choice_circle.pos = stim_right.pos

    for _ in range(feedback_frames):
        stim_right.draw()
        stim_left.draw()
        choice_circle.draw()
        win.flip()
    if trial > 3:
        if trial%(len(trialmat)/targets) == 0:
            temp = int((trial/len(trialmat))*100)
            waitScreen = visual.TextStim(win, text = 'you are ' + str(temp) +  '% through the experiment. Take a break! Press any button to continue.', pos=(0.0, 0.0))
            waitScreen.draw()
            win.flip()
            waitResp = event.waitKeys(keyList = None,timeStamped=True)
            save_data(trialmat)



t_720trials = time.time() - init

print(t_630trials)
print(t_720trials)


win.mouseVisible = True
save_data(trialmat)