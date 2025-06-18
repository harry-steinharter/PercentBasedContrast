# %% Imports
import sys
from psychopy import core, visual, data, event, monitors, logging
from psychopy.tools.filetools import fromFile, toFile
import pylab
from importlib import reload
import functions as F
reload(F)

testing = False
sub_id = str(F.SubNumber("subNum.txt"))

# %% Setup EyeLink
eye = F.xPyLink(sub_id, doTracking=True)
eye.startTracker()

# %% Setup Window
mywin = visual.Window(fullscr=True, monitor="Flanders", units="deg",colorSpace='rgb',color = [0,0,0],bpc=(10,10,10),depthBits=10)
xWindow = F.xWindow(mywin)

# %% Do Baseline
n_up = 1
n_down = 1
nTrials = 120
if testing:
    nTrials = 30
    
baselineCondition = [
    {'label':'baseline','startVal':0.1,'maxVal':0.1,'minVal':0.0,
        'stepSizes':0.1,'stepType':'log','nReversals':1,
        'nUp':n_up,'nDown':n_down}]

xWindow.hello()

redo = True 
# Allows to redo baseline determination if an impossible value occurs 
# Impossibe values are < 0 (negative contrast) or greater than 0.1 (maximum tested value)
while redo == True:
    baseline = F.experiment(myXwin=xWindow,
                        myConds=baselineCondition,
                        nTrials=nTrials,
                        subject_id=sub_id,
                        eyeTracker=eye)
    file = baseline.openDataFile(block='baseline')
    baseline.baseline(dataFile=file) # Do base experiment
    baseThreshold = baseline.getThresholdFromBase() # math
    redo = baseline.reDoBase(baseThreshold) # Does visual countdown and returns logical
    if redo == True:
        xWindow.countdown()

# %% Do Experiment
if testing:
    if baseThreshold < 0 or baseThreshold > 0.1:
        baseThreshold = 0.0175517727257755
nBlocks = 7
nTrials //= 5 # floor divide for int. Divide by len(experimentConditions)
experimentConditions = [
    {'label':'100','startVal':0.1,'maxVal':0.1,'minVal':0.0,
        'stepSizes':0.1,'stepType':'log','nReversals':1,
        'nUp':n_up,'nDown':n_down,'FC':baseThreshold},
    {'label':'200','startVal':0.1,'maxVal':0.1,'minVal':0.0,
        'stepSizes':0.1,'stepType':'log','nReversals':1,
        'nUp':n_up,'nDown':n_down,'FC':baseThreshold*2},
    {'label':'400','startVal':0.1,'maxVal':0.1,'minVal':0.0,
        'stepSizes':0.1,'stepType':'log','nReversals':1,
        'nUp':n_up,'nDown':n_down,'FC':baseThreshold*4},
    {'label':'800','startVal':0.1,'maxVal':0.1,'minVal':0.0,
        'stepSizes':0.1,'stepType':'log','nReversals':1,
        'nUp':n_up,'nDown':n_down,'FC':baseThreshold*8},
    {'label':'000','startVal':0.1,'maxVal':0.1,'minVal':0.0,
        'stepSizes':0.1,'stepType':'log','nReversals':1,
        'nUp':n_up,'nDown':n_down,'FC':0}]

testing = F.experiment(myXwin=xWindow,
                       myConds=experimentConditions,
                       nTrials=nTrials*nBlocks,
                       subject_id=sub_id,
                       eyeTracker=eye,
                       nBlocks=nBlocks)

xWindow.midway(nBlocks)

file = testing.openDataFile(block='test')

testing.testing(file)

testing.end()
