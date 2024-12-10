
import pandas as pd
import random as rd
totalRuns = 1

#set no. of targets
targets = 1

stim1Distances = [0, 3, 5, 8, 10, 13, 15, 20, 25, 30, 35, 45, 55, 65, 75, 85, 100, 120, 140, 160, 180]

presentations = 87

def generateTarget():
    fullList = []

    #Repeat process of generating random list
    for i in range(totalRuns):
    #Start at a random value on the color wheel
        start = rd.randint(0, 360)
        startcopy = start
    #Figure out how long each step across the color wheel needs to be
        interval =  360/targets

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


#Takes the list of targets, duplicates it the amount of times needed for the experiment. 
#'Presentations' is equal to the amount of pairs that there are for each target
def generateTarget2(presentations):
    firstList = generateTarget()
    secondList = []
    for i in firstList:
        secondList.extend([i]* presentations)
    return secondList


def generateStim(target, dist1):
    stim1 = []
    for i, p in enumerate(target):
        if p + dist1[i] > 360:
            reset = (p + dist1[i]) - 360
            stim1.append(0 + reset)
        else:
            stim1.append(p + dist1[i])
    return stim1

#Takes in the amount of targets, and for each target generates the corresponding distances from the stimuli the target will be in two lists
#Ultimately generates the rows in the dataframe for each distance measure, one row for each presentation
def multiplyDistances(targetLength):
    masterStim1 = []
    masterStim2 = []
    for i in range(targetLength):
        dict1 = {}
        stimList1 = []
        stimList2 = []
        dict1 = shuffleStim()
        stimList1, stimList2 = createDistances(dict1)
        masterStim1.extend(stimList1)
        masterStim2.extend(stimList2)
    return masterStim1, masterStim2


test = generateTarget2(presentations)
test2, test3 = multiplyDistances(targets)


trialmat = pd.DataFrame(columns=['target', 'dist1', 'dist2', 'stim1', 'stim2'])
trialmat['dist1'], trialmat['dist2'] = test2, test3
trialmat['target'] = test
trialmat['stim1'] = generateStim(test, test2)
trialmat['stim2'] = generateStim(test, test3)

trialmat.to_csv('test3')
