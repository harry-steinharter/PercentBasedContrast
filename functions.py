import os
from psychopy.visual import TextStim
from psychopy.event import waitKeys
from psychopy import data, core, visual, event
import pandas as pd
import pylab
import math
import numpy as np
from typing import Literal
import pylink

def SubNumber(filename):
    with open(filename, 'r', encoding='utf-8-sig') as file:
        content = int(file.read().strip())

    content_int = int(content)
    new_content = (content_int + 1)
    
    with open(filename, 'w') as file:
        file.write(str(new_content))
    return new_content


class xWindow:
    def __init__(self, mywin):
        self.mywin = mywin

        self.line_top = visual.Line(win=mywin, start=(0,.75), end=(0,1.25),  lineWidth=4.2, pos=(0,0),  colorSpace='rgb', color = -1)
        self.line_target = visual.Line(win=mywin, start=(0,-0.25), end=(0,0.25),  lineWidth=4.2, pos=(0,0),  colorSpace='rgb', color = -1)
        self.line_bottom = visual.Line(win=mywin, start=(0,-.75), end=(0,-1.25), lineWidth=4.2, pos=(0,0), colorSpace='rgb', color = -1)

        self.fixation = visual.GratingStim(win = mywin, color=-1, colorSpace='rgb',tex=None, mask='circle', size=0.1)
        self.blank = visual.TextStim(win = mywin, text="You should not see this", color=mywin.color, colorSpace='rgb')

        self.diode = visual.GratingStim(win = mywin,color='black',colorSpace='rgb',tex=None,mask='circle',units='pix',size=80,pos=[-780,-440],autoDraw=True)

    def drawOrder(self, stimuli):
        if not isinstance(stimuli, (list,tuple)):
            stimuli.draw()
        elif isinstance(stimuli, (list,tuple)):
            for stimulus in stimuli:
                stimulus.draw()
        else:
            raise ValueError("Impossible instance of `stimuli` argument.")
        self.mywin.flip()
        return

    def countdown(self, duration=3):
        t = core.CountdownTimer(int(duration))
        while t.getTime() >= 0:
            cd = TextStim(self.mywin, color = 'black', text = f"Experiment will continue in {math.ceil(t.getTime())}...")
            self.drawOrder(cd)

    def hello(self):
        m_hello = visual.TextStim(self.mywin, color='black', wrapWidth=20,
                                  text = "Welcome to the experiment.\nYou will see a black dot that is quickly replaced by verticle line.\nThe line will only appear briefly.\nAfter it disappears, please respond to indicate whether you saw the line.\nPress [LEFT] for NO, or press [RIGHT] for YES.\nYou should respond as quickly as possible.\nPlease always look at the center of the screen.\nPress [RIGHT] when you are ready to begin.")
        self.drawOrder(m_hello)
        event.waitKeys(keyList=['right','num_6'])
        self.countdown()
        
    def midway(self,nBlocks):
        m_midway = visual.TextStim(self.mywin, color='black', wrapWidth=20,
                                   text = f"The next portion will be the first of {nBlocks} blocks.\nYou will now also see additional lines.\nThere will sometimes be a line ABOVE and a line BELOW the target.\nYou should only respond based on the line in the MIDDLE.\nThe procedure will be the same.\nPress [RIGHT] to continue.")
        
        self.drawOrder(m_midway)
        event.waitKeys(keyList=['right','num_6'])
        self.countdown()
        

class experiment:
    def __init__(self, myXwin, myConds, nTrials, 
                 subject_id, eyeTracker,
                 nullOdds = .1, t_fixation = .3, 
                 t_stim = .2, t_response = 1.3,
                 t_break = 10, nBlocks = 1):
        
        if not isinstance(myConds, list):
            raise ValueError("`myConds` should be a list of dicts")
        self.mywin = myXwin
        self.myConds = myConds
        self.nTrials = nTrials
        self.nBlocks = nBlocks
        self.nullOdds = nullOdds
        self.id = subject_id
        self.t_stim = t_stim
        self.t_fixation = t_fixation
        self.t_response = t_response
        self.t_break = t_break
        self.eyeTracker = eyeTracker
        self.stairs = data.MultiStairHandler(stairType='simple',
                                             method='random',
                                             nTrials=self.nTrials,
                                             conditions=self.myConds)
        
    def end(self):
        m_end = visual.TextStim(self.mywin.mywin, color='black', wrapWidth=20,
                                  text = "Thanks for Participating!\nIt's finally over!\n:)""")
        self.mywin.drawOrder(m_end)
        self.eyeTracker.closeTracker()
        core.wait(5)
        
    def getBreaks(self):
        totalTrials = int(len(self.myConds) * self.nTrials)
        breakTrials = np.linspace(start=0,stop=totalTrials, num=self.nBlocks,
                                  endpoint=False,dtype=int)[1:]
        return breakTrials, totalTrials

    def openDataFile(self,block:Literal['baseline', 'test']):
        if block == 'baseline':
            basePath = "Baselines"
            baseName = f"{self.id}_baseline.csv"
        elif block == 'test':
            basePath = "Experiment_Outputs"
            baseName = f"{self.id}_testing.csv"
        else:
            raise ValueError("`block` should be one of ['baseline' or 'test']")
        
        # Ensure directory exists
        os.makedirs(basePath, exist_ok=True)

        # Handle file collision
        fileName = os.path.join(basePath, baseName)
        count = 1
        while os.path.exists(fileName):
            name, ext = os.path.splitext(baseName)
            fileName = os.path.join(basePath, f"{name}_{count}{ext}")
            count += 1

        dataFile = open(fileName, 'w', buffering=1)
        dataFile.write("id,trial,label,FC,TC,response,RT\n")
        return dataFile
    
    def baseline(self,dataFile):
        stairs = self.stairs
        trialClock = core.Clock()
        totalTrials = self.nTrials * len(self.myConds)
        thisTrial = 0

        for trial, condition in stairs:
            thisIntensity = stairs.currentStaircase.intensity
            thisLabel = condition['label']

            # Random _null chance
            if np.random.random() <= self.nullOdds:
                thisIntensity = 0
                thisLabel += '_null'
            self.mywin.line_target.contrast = -thisIntensity

            self.mywin.drawOrder(self.mywin.fixation)
            core.wait(self.t_fixation)

            self.mywin.drawOrder(self.mywin.line_target)
            core.wait(self.t_stim)

            trialClock.reset()
            self.mywin.drawOrder(self.mywin.blank)
            allKeys = event.waitKeys(maxWait=self.t_response,
                        keyList=['left','num_4',
                            'right','num_6',
                            'q','escape'])
            
            thisRT = trialClock.getTime()
            if thisRT < self.t_response:
                core.wait(self.t_response - thisRT)

            if allKeys:
                for key in allKeys:
                    if key in ['left','num_4']:
                        thisResp = 0
                    elif key in ['right','num_6']:
                        thisResp = 1
                    elif key in ['q','escape']:
                        self.eyeTracker.closeTracker()
                        core.quit()
                    else:
                        raise ValueError(f"Unexpected key: {key}")
            else:
                thisResp = 0
                thisRT = 99

            dataFile.write(f"{self.id},{thisTrial},{thisLabel},{000},{stairs.currentStaircase.intensity},{thisResp},{thisRT}\n")
            if not thisLabel.endswith("_null"): 
                stairs.addResponse(thisResp)
            # Don't adjust the staircase for a null trial

            thisTrial += 1

        stairs.saveAsPickle(f'Baselines/{self.id}')

    def doBreak(self,b):
        m_break = visual.TextStim(self.mywin.mywin, color='black', wrapWidth=20,
                                  text=f"You have finished block {b+1}.\nTime for a break. \nYou can stretch your legs or get some water.\nWait a bit before continuing.")
        m_continue = visual.TextStim(self.mywin.mywin, color='black', wrapWidth=20,
                                  text=f"You have finished block {b+1}.\nYou can continue when ready.\nPress [RIGHT] to continue.\n")
        self.mywin.drawOrder(m_break)
        core.wait(self.t_break)
        self.mywin.drawOrder(m_continue)
        event.waitKeys(keyList=['right','num_6'])
        self.mywin.countdown()

    def testing(self,dataFile):
        lines = [self.mywin.line_target, self.mywin.line_top, self.mywin.line_bottom]
        breaks, totalTrials = self.getBreaks()

        stairs = self.stairs

        trialClock = core.Clock()
        thisTrial = 0

        for trial, condition in stairs:
            if thisTrial in breaks:
                self.doBreak(b = np.where(breaks == thisTrial)[0][0])

            if self.eyeTracker.doTracking:
                self.eyeTracker.tracker.startRecording(1,1,1,1)
            thisIntensity = stairs.currentStaircase.intensity
            thisLabel = condition['label']

            # Random _null chance
            if np.random.random() <= self.nullOdds:
                thisIntensity = 0
                thisLabel += '_null'

            self.mywin.line_target.contrast = -thisIntensity
            self.mywin.line_top.contrast = -condition['FC']
            self.mywin.line_bottom.contrast = -condition['FC']

            # Draw fixation
            self.mywin.diode.color *= -1 # white -- button on
            self.mywin.drawOrder(self.mywin.fixation)
            core.wait(self.t_fixation)
            self.blinkDiode() # black -- button off

            # Draw stmiulus
            self.eyeTracker.stimOnset(thisTrial,thisLabel,thisIntensity)
            self.mywin.diode.color *= -1 # white -- button on
            self.mywin.drawOrder(lines)
            core.wait(self.t_stim)
            self.blinkDiode() # black -- button off

            trialClock.reset()
            self.mywin.drawOrder(self.mywin.blank)
            allKeys = event.waitKeys(maxWait=self.t_response,
                        keyList=['left','num_4',
                            'right','num_6',
                            'q','escape'])
            
            thisRT = trialClock.getTime()
            if thisRT < self.t_response:
                core.wait(self.t_response - thisRT)

            if allKeys:
                for key in allKeys:
                    if key in ['left','num_4']:
                        thisResp = 0
                    elif key in ['right','num_6']:
                        thisResp = 1
                    else:# key in ['q','escape']:
                        self.eyeTracker.closeTracker()
                        core.quit()
#                    else:
#                        raise ValueError(f"Unexpected key: {key}")
            else:
                thisResp = 0
                thisRT = 99

            self.eyeTracker.logResponse(thisResp,thisRT)
            dataFile.write(f"{self.id},{thisTrial},{thisLabel},{condition['FC']},{stairs.currentStaircase.intensity},{thisResp},{thisRT}\n")
            if not thisLabel.endswith("_null"): 
                stairs.addResponse(thisResp)
            # Don't adjust the staircase for a null trial

            thisTrial += 1
            if self.eyeTracker.doTracking:
                self.eyeTracker.tracker.stopRecording()

        stairs.saveAsPickle(f'Experiment_outputs/{self.id}')
    
    def getThresholdFromBase(self, id = None):
        threshVal = 0.5 # set to 0.5 for Yes/No (or PSE). Set to 0.8 for a 2AFC threshold
        expectedMin = 0.0 # set to zero for Yes/No (or PSE). Set to 0.5 for 2AFC
        if id is None:
            id = self.id

        thisFileName = f'Baselines/{id}_baseline.csv'
        thisDat = pd.read_csv(thisFileName)
        thisDat = thisDat[~thisDat['label'].str.endswith('_null')]

        allIntensities = thisDat['TC'].tolist()
        allResponses = thisDat['response'].tolist()

        i, r, n = data.functionFromStaircase(allIntensities, allResponses, bins='unique')
        combinedInten, combinedResp, combinedN = i, r, n
        combinedN = pylab.array(combinedN)  # convert to array so we can do maths
        fit = data.FitLogistic(combinedInten, combinedResp, 
                               expectedMin = expectedMin, 
                               sems = 1.0 / combinedN,
                               optimize_kws={'maxfev':int(1e6)})
        thresh = fit.inverse(threshVal)
        print(f'-----------Threshold for [{id}, Baseline] is: {thresh}-----------')
        return(thresh)

    def reDoBase(self,thresh):
        m_redo = visual.TextStim(self.mywin.mywin, color='black', wrapWidth=20,
                                 text = f"Please wait for the experimenter.\nParticipant {self.id} baseline detection threshold:\n{thresh}\nThreshold outside of expected range.\nTry again [y / n]?")
        m_good = visual.TextStim(self.mywin.mywin, color='black', wrapWidth=20,
                                 text = f"Please wait for the experimenter.\nParticipant {self.id} baseline detection threshold:\n{thresh}\nThreshold inside of expected range.\\Go again [y / n]?")
        if thresh > 0.1 or thresh <= 0:
            self.mywin.drawOrder(m_redo)
            keys = event.waitKeys(keyList=['y','n'])
            if keys:
                for key in keys:
                    if key == 'y':
                        return True
                    else:
                        return False
        else:
            self.mywin.drawOrder(m_good)
            event.waitKeys(keyList=['y','n'])
            return False

    def blinkDiode(self,t=2/60):
        # Defaults to two frames blink (at 60fps)
        # Blinks the diode to indicate the offset of a stimulus
        # Does not draw any new stimuli, flips the window with existing stuff
        self.mywin.diode.color *= -1
        self.mywin.mywin.flip()
        core.wait(t) # 2 frames

class xPyLink:
    def __init__(self,id,
                 ip = "100.1.1.2:255.255.255.0",
                 doTracking = True):
        self.id = id
        self.ip = ip
        self.doTracking = doTracking
        self.eyeHostFile = str(self.id)+'.edf'
        self.eyeLocalFile = "EyeLink/"+self.eyeHostFile

    def startTracker(self):
        if not self.doTracking:
            return
        self.tracker = pylink.EyeLink(self.ip)
        self.tracker.openDataFile(self.eyeHostFile)
        self.tracker.sendCommand("screen_pixel_coords = 0 0 1919 1079")
        pylink.openGraphics()
        self.tracker.doTrackerSetup()
        pylink.closeGraphics()

    def closeTracker(self):
        if not self.doTracking:
            return
        self.tracker.closeDataFile()
        self.tracker.receiveDataFile(self.eyeHostFile, self.eyeLocalFile) # Takes closed data file from 'src' on host PC and copies it to 'dest' at Stimulus PC
        self.tracker.close()

    def stimOnset(self,trial_id,condition,contrast):
        if not self.doTracking:
            return
        self.tracker.sendMessage(f"TRIAL_START {trial_id} CONTRAST {contrast} CONDITION {condition}")

    def logResponse(self,response,rt):
        if not self.doTracking:
            return
        self.tracker.sendMessage(f"RESPONSE {response} RT {rt}")
