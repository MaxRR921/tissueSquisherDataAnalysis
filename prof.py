import gui
import cProfile

""""
plan for profiling/testing:
NEED TO MAKE THIS THING MUCH FASTER THAN IT IS RIGHT NOW. Need to identify slow points and attack. To do this we need to get a sense
of exactly what is happening through the following steps:

1. Documentation for all functions and what they do, go through each function, see what it does, give it and its class comments
two difficult components:
2. Pytest: Testing for correctness (shouldn't need actual devices in person.)
    - create mock devices and data
3. cProfile: testing speed (need actual devices?)
    - run each function and see how long they all take 


Structure of GUI class: what it actually DOES:

    initializes everything

    moves micrometer down (maybe put that in the micrometer __init__)

    Initializes plots - fine

    starts updatePlotsFromData()
        this could be bad because we are constantly doing try catch statements to update plots that don't exist yet. Busy waiting. Also except is bad
        when we know it's gonna happen constantly because on every except the program has to:
        1. Unwind the call stack.
        2. Search for an appropriate exception handler.
        3. Create an exception object and propagate it
    
    starts powermeter theread - adds another busy wait during time where we don't even need to be collecting data LOOK INTO why we don't hit 
    run should probably only be set to true and threads should only start when we actually want to start collecting data, stopped when we 
    are not collecting any data.
    
    all other stuff is just creating buttons except

    startExecuteThread. There's a lot of logic here to break down so that we can get an understanding of how to test this. Let's start 
    by going over each step that it performs and how that affects other classes:

    1. def startExecuteThread(self, moveList):
        for plot in self.plotList:
            plot.resetPlot()
        self.executeThread = Thread(target=self.__collect, args=[moveList])
        self.executeThread.start()

    this method takes in a moveList why? idk. it should just use self. movelist instead of feeding it in for some reason.
    for plot in self.plotList():
        plot.resetPlot()
    I think this is fine. It's just resetting every plot in our list of plots that are there.

    
    this next function is where the bulk of the logic is:

    def __collect(self, moveList): - again, could just use self.movelist
        print("LETS GO")
        if not self.updatingPlots:  - if plots aren't already updating???? they shouldn't be updating at this point. should be able to just be set to true
            self.updatingPlots = True
            self.root.after(10, self.updatePlotsFromData)
        try:                        - HERE instead of a try except we should just have an if. We know the two cases. Either it's there or it isn't.
            self.polarimeter.run = True
            self.__startPolarimeterThread()
        except:
            print("failed to start polarimeter thread.")

        for i in range(self.numExecutions):
            for move in moveList:
                if not self.stopExecution:
                    move.execute()
                else:
                    break
        try:
            self.polarimeter.run = False
        except:
            print("No polarimeter")
        self.strain, self.phase  = dataAnalysisVmaster.analyzeData(self.polarimeter.s1List, self.polarimeter.s2List, self.polarimeter.s3List, self.polarimeter.timeList)
        print("PHASE:")  
        print(self.phase)
        print("STRAIN")
        print(self.strain)
        print(len(self.phase))
        print(len(self.strain))
        if self.powerPlot is not None:
            self.powerPlot.generateCsvFromPlot("pow.csv")
        else:
            print("no power plot open")
       
        self.executed = True
        print("DONE")
    




    All the buttons in gui and what they do:


"""