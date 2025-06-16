# import os
import sys
# from psychopy.hardware import keyboard
from psychopy import core, visual, data, event, monitors, logging
from psychopy.tools.filetools import fromFile, toFile
import pylab

sys.path.append('/Users/visionlab/Documents/Project_Harry_S/7LineSegments')
sys.path.append('/Users/harrysteinharter/Documents/MSc/Timo Internship/7LineSegments')
# import otherFunctions as OF 
mywin = visual.Window(fullscr=True, monitor="Flanders", units="deg",colorSpace='rgb',color = [0,0,0],bpc=(10,10,10),depthBits=10)
# Define the condition
def SubNumber(filename):
#    os.chdir("/Users/harrysteinharter/Documents/Programming/Timo Internship")
    with open(filename, 'r', encoding='utf-8-sig') as file:
        content = int(file.read().strip())

    content_int = int(content)
    new_content = (content_int + 1)
    
    with open(filename, 'w') as file:
        file.write(str(new_content))
    return new_content
def drawOrder(stim, win = mywin):
    if not isinstance(stim, (list,tuple)):
        stim = [stim]
    for i in stim:
        i.draw()
    mywin.flip()
    

X = str(SubNumber("subNum.txt"))
fileName = f"Baselines/{X}_baseline.csv"
dataFile = open(fileName, 'w')
dataFile.write("id,trial,TC,response,RT\n")

#### Define Visuals ####
line_target = visual.Line(win=mywin, start=(0,-0.25), end=(0,0.25),  lineWidth=4.2, pos=(0,0),  colorSpace='rgb', color = 'black')
fixation = visual.GratingStim(win = mywin, color=-1, colorSpace='rgb',tex=None, mask='circle', size=0.1)
blank = visual.TextStim(win=mywin, text="You should not see this", color=mywin.color, colorSpace='rgb')

#### Define Timing ####
t_fixation = .3 # pre-stim fixation period duration
t_stim = .2 # stimulus duration (0.2)
t_response = 1.3 # max time to respond

n_up = 1
n_down = 1
nTrials = 20 # 120
stairs = data.StairHandler(startVal = 0.1, minVal = 0, maxVal = 0.1,
                           stepSizes = 0.1, stepType = 'log', nReversals=1,
                           nUp = n_up, nDown = n_down, nTrials = nTrials)
# Clocks
trialClock = core.Clock()

for trial in stairs:
    thisIntensity = stairs.intensity
    line_target.contrast = thisIntensity

    drawOrder(fixation)
    core.wait(t_fixation)

    drawOrder(line_target)
    core.wait(t_stim)

    trialClock.reset()
    drawOrder(blank)
    allKeys = event.waitKeys(maxWait=t_response,
                   keyList=['left','num_4',
                            'right','num_6',
                            'q','escape'])
    
    thisRT = trialClock.getTime()
    if thisRT < t_response:
        core.wait(t_response - thisRT)

    if allKeys:
        for key in allKeys:
            if key in ['left','num_4']:
                thisResp = 0
            elif key in ['right','num_6']:
                thisResp = 1
            elif key in ['q','escape']:
                core.quit()
            else:
                raise ValueError(f"Unexpected key: {key}")
    else:
        thisResp = 0
        thisRT = 99
    
    dataFile.write(f"{X},{stairs.thisTrialN},{thisIntensity},{thisResp},{thisRT}\n")
    stairs.addResponse(thisResp)

stairs.saveAsPickle(f'Baselines/{X}')

#### Now get threshold ####
threshVal = 0.5 # set to 0.5 for Yes/No (or PSE). Set to 0.8 for a 2AFC threshold
expectedMin = 0.0 # set to zero for Yes/No (or PSE). Set to 0.5 for 2AFC

allIntensities, allResponses = [], []
thisFileName = f'Baselines/{X}.psydat'
thisDat = fromFile(thisFileName)
assert isinstance(thisDat, data.StairHandler)
allIntensities.append(thisDat.intensities)
allResponses.append(thisDat.data)

i, r, n = data.functionFromStaircase(allIntensities, allResponses, bins='unique')
combinedInten, combinedResp, combinedN = i, r, n
combinedN = pylab.array(combinedN)  # convert to array so we can do maths
fit = data.FitLogistic(combinedInten, combinedResp, expectedMin = expectedMin, sems=1.0 / combinedN)
thresh = fit.inverse(threshVal)
print(f'-----------Threshold is: {thresh}-----------')