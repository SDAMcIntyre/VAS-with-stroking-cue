from psychopy import visual, event, core
import os

class DataFileCollection():
    def __init__(self,foldername,filename,headers,dlgInput):
        self.folder = './'+foldername+'/'
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.fileprefix = self.folder + filename
        
        self.infoFile = open(self.fileprefix+'_info.csv', 'w') 
        for k,v in dlgInput.items(): self.infoFile.write(k + ',' + str(v) + '\n')
        self.infoFile.close()
        
        self.dataFile = open(self.fileprefix+'_data.csv', 'w')
        self.writeTrialData(headers)
        
        self.logFile = open(self.fileprefix+'_log.csv', 'w')
        self.logFile.write('time,event\n')
    
    def logEvent(self,time,event):
        self.logFile.write('{},{}\n' .format(time,event))
        print('LOG: {} {}' .format(time, event))
    
    def closeFiles(self):
        self.dataFile.close()
        self.logFile.close()
    
    def logAbort(self,time):
        self.logEvent(time,'experiment aborted')
        self.closeFiles()
    
    def writeTrialData(self,trialData):
        lineFormatting = ','.join(['{}']*len(trialData))+'\n'
        self.dataFile.write(lineFormatting.format(*trialData))

class DisplayInterface:
    def __init__(self,fullscr,screen,size,message):
        self.textColour = [-1,-1,-1]
        
        self.win = visual.Window(fullscr = fullscr, 
                                    allowGUI = True, 
                                    screen = screen,
                                    size = size)
        
        self.message = visual.TextStim(self.win,
                                        text = message,
                                        height = 0.12,
                                        color = self.textColour,
                                        units = 'norm',
                                        pos = (0,-0))
        
        self.timerDisplay = visual.TextStim(self.win,
                                        text = '',
                                        height = 0.12,
                                        color = self.textColour,
                                        units = 'norm',
                                        pos = (0.8,-0.8))
    def updateMessage(self,message):
        self.message.text = message
        self.win.flip()
    
    def startScreen(self,message):
        self.message.text = message
        self.message.autoDraw = True
        event.clearEvents()
        self.win.flip()
    
    def updateTimerDisplay(self,timer):
        self.timerDisplay.text = str(int(math.ceil(timer)))
        self.timerDisplay.autoDraw = True
        self.win.flip()
    
    def hideTimerDisplay(self):
        self.timerDisplay.text = ''
        self.timerDisplay.autoDraw = False
        self.win.flip()

class VASInterface(DisplayInterface):
    def __init__(self,fullscr,screen,size,message,question,minLabel,maxLabel):
        DisplayInterface.__init__(self,fullscr,screen,size,message)
        
        self.mouse = event.Mouse(True,None,self.win)
        
        barMarker = visual.TextStim(self.win, text='|', units='norm')
        
        self.VAS = visual.RatingScale(self.win, low=-10, high=10, precision=10, 
            showValue=False, marker=barMarker, scale = question,
            tickHeight=1, stretch=1.5, size = 0.8, 
            labels=[minLabel, maxLabel],
            tickMarks=[-10,10], mouseOnly = True, pos=(0,0))
    
    def getVASrating(self,clock):
        event.clearEvents()
        self.VAS.reset()
        resetTime = clock.getTime()
        aborted = False
        while self.VAS.noResponse and not aborted:
            self.VAS.draw()
            self.win.flip()
            for (key,t) in event.getKeys(['escape'], timeStamped=clock):
                response = -99
                rTime = t
                aborted = True
        if not aborted:
            response = self.VAS.getRating()
            rTime = self.VAS.getRT() + resetTime
        self.win.flip()
        return(response,rTime)


if __name__ == "__main__":
    participant = VASInterface(fullscr = False, screen = 1, size = [1920,1200],
                                message = 'please wait',
                                question = 'how pleasant?',
                                minLabel = 'very unpleasant',
                                maxLabel = 'very pleasant')
    
    clock=core.Clock()
    clock.reset()
    (rating, rTime) = participant.getVASrating(clock)
    print(rating)
    participant.win.close()
    