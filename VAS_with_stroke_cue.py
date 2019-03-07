from psychopy import gui, data, core
from experiment_helpers import *
import pygame

# -- GET INPUT FROM THE EXPERIMENTER --

exptInfo = {'01. Participant Code':'00', 
            '02. Experiment name':'', 
            '03. Number of repeats':5, 
            '04. Speeds (cm/sec)':'1,3,30',
            '05. Stimuli':'soft brush, rough brush, hand',
            '06. Stimulation site':'dorsal left hand',
            '08. Participant language':('en'), ## ('en','sv')
            '09. Folder for saving data':'data'}

dlg = gui.DlgFromDict(exptInfo, title='Experiment details')
if dlg.OK:
    exptInfo['10. Date and time']= data.getDateStr(format='%Y-%m-%d_%H-%M-%S') ##add the current time and continue
else:
    core.quit() ## the user hit cancel so exit

# --

# -- DISPLAY TEXT --

displayTextDictionary = {
            'en': {'waitMessage':'Please wait.',
                    'interStimMessage':'...',
                    'finishedMessage':'Session finished.',
                    'strokeQuestion':'How pleasant was the last stimulus on your skin?',
                    'strokeMin':'very unpleasant',
                    'strokeMax':'very pleasant'},
                    
#            'sv': {'waitMessage':'Please wait.',
#                    'interStimMessage':'...',
#                    'finishedMessage':'Session finished.',
#                    'strokeQuestion':'How pleasant was the last stimulus on your skin?',
#                    'strokeMin':'unpleasant',
#                    'strokeMax':'pleasant'} 
            }

## select dictionary according to participant language
displayText = displayTextDictionary[exptInfo['08. Participant language']]

# --

# -- SETUP STIMULUS RANDOMISATION AND CONTROL --
speeds = [int(i) for i in exptInfo['04. Speeds (cm/sec)'].split(',')]
stimuli = exptInfo['05. Stimuli'].split(',')

stimList = []
for stimulus in stimuli: 
    for speed in speeds:
        stimList.append({'stimulus':stimulus,
                        'speed':speed,
                        'stimCueSound':'./sounds/stim {}cms {}.wav' .format(speed,stimulus),
                        'timingCueSound':'./sounds/timing {}cm-sec.wav' .format(speed)})
trials = data.TrialHandler(stimList, exptInfo['03. Number of repeats'])

# ----


# -- MAKE FOLDER/FILES TO SAVE DATA --

saveFiles = DataFileCollection(foldername = exptInfo['09. Folder for saving data'],
                filename = exptInfo['02. Experiment name'] + '_' + exptInfo['10. Date and time'] +'_P' + exptInfo['01. Participant Code'],
                headers = ['trial','stimulus','speed','rating'],
                dlgInput = exptInfo)

# ----


# -- SETUP VISUAL INTERFACE INCLUDING VAS --

participant = VASInterface(fullscr = False, screen = 1, size = [1920,1200],
                            message = displayText['waitMessage'],
                            question = displayText['strokeQuestion'],
                            minLabel = displayText['strokeMin'],
                            maxLabel = displayText['strokeMax'])

# -----


# -- SETUP  AUDIO --

pygame.mixer.pre_init() 
pygame.mixer.init()
trialNumberSounds = [pygame.mixer.Sound('./sounds/' + str(i).zfill(2) + '.wav') for i in range(1,21)]

# ----


# -- RUN THE EXPERIMENT --

# start experiment clock
exptClock=core.Clock()
exptClock.reset()
waitCountdown = core.CountdownTimer(0)
# display starting screens
participant.startScreen(displayText['waitMessage'])

# wait for start trigger (space)
for (key,keyTime) in event.waitKeys(keyList=['space','escape'], timeStamped=exptClock):
    if key in ['escape']:
        saveFiles.logAbort(keyTime)
        core.quit()
    if key in ['space']:
        exptClock.add(keyTime)
        saveFiles.logEvent(0,'experiment started')


# start the main experiment loop
for thisTrial in trials:
    
    # load audio files for this trial
    stimCueSound = pygame.mixer.Sound(thisTrial['stimCueSound'])
    timingCueSound = pygame.mixer.Sound(thisTrial['timingCueSound'])
    trialNoSound = trialNumberSounds[trials.thisN]
    
    # tell experimenter which trial number we're up to
    soundCh = trialNoSound.play()
    
    # display stimulus message to participant
    participant.updateMessage(displayText['interStimMessage'])
    
    # wait for the audio to finish
    while soundCh.get_busy():
        for (key,keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            saveFiles.logAbort(keyTime)
            core.quit()
    
    # tell experimenter which stimulus is coming up
    soundCh = stimCueSound.play()
    saveFiles.logEvent(exptClock.getTime(),'stimulus cued {} {}cms/sec' .format(thisTrial['stimulus'], thisTrial['speed']))
    
    # wait for the audio to finish
    while soundCh.get_busy():
        for (key,keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            saveFiles.logAbort(keyTime)
            core.quit()
    
    # give experimenter a 2 second pause to prepare stimulus
    waitCountdown.reset(2)
    while waitCountdown.getTime() > 0:
        for (key,keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            saveFiles.logAbort(keyTime)
            core.quit()
    
    # play timing cue for experimenter to deliver stimulus
    soundCh = timingCueSound.play()
    saveFiles.logEvent(exptClock.getTime(),'touch stimulus started')
    
    # wait for the audio to finish
    while soundCh.get_busy():
        for (key,keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            saveFiles.logAbort(keyTime)
            core.quit()
    
    # show VAS to participant and get rating
    participant.updateMessage('') ## hide message
    (rating,rTime) = participant.getVASrating(exptClock)
    if rating == -99:
        saveFiles.logAbort(rTime)
        core.quit()
    saveFiles.logEvent(rTime,'Pleasantness rating (-10","10) = {}' .format(rating))
    
    saveFiles.writeTrialData([trials.thisN+1,
                            thisTrial['stimulus'],
                            thisTrial['speed'],
                            rating])
    
    saveFiles.logEvent(exptClock.getTime(),'{} of {} complete' .format(trials.thisN+1, trials.nTotal))
    

# prompt at the end of the experiment
event.clearEvents()
participant.updateMessage(displayText['finishedMessage'])

finishedSound = pygame.mixer.Sound('./sounds/finished.wav')
soundCh = finishedSound.play()
saveFiles.logEvent(exptClock.getTime(),'experiment finished')

while soundCh.get_busy():
    pass
saveFiles.closeFiles()
core.wait(2)
participant.win.close()
core.quit()