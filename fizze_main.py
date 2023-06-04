import sys
import json
import math
import numpy as np
import matplotlib.pyplot as plt

REPLAY_JSON = None
VEL_CHECK_TIME = float(0.05)

def LoadReplay(file):
    global REPLAY_JSON
    with open(file) as f:
        replay = f.readlines()
        
    REPLAY_JSON = json.loads(replay[0])
    
def TwoPointMag(vec1, vec2):
    pass

def VecMag(vec):
    pass

def DevideVec2(vec, num):
    
    num0 = vec[0] / num
    num1 = vec[1] / num
    
    return [num0, num1]

def main(file):
    global REPLAY_JSON
    global VEL_CHECK_TIME
    
    LoadReplay(file=file)
    
    j = 0
    # looping over all the players
    while (j < len(REPLAY_JSON["players"])):
        i = 0
        # all the velocitys we calaculate bellow
        velocity = []
        
        velocityIndex = 0
        velocityHistory = [[0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0]]
        denomalizedVelocityAverage = [0, 0]
        velocityHistorySize = 9
        
        # the last velocity
        previousVector2 = None
        # The time system just trust cuz i forgor how it works.
        time = 0
        
        #logging
        stateWasOne = 0
        stateWasTwo = 0
        stateWasNone = 0
        timesTested = 0
        valueWasNone = 0
        valueWasValue = 0
        while (i < len(REPLAY_JSON["playerDatas"][j]["movementData"]["headPositions"])):
            
            headPositions = REPLAY_JSON["playerDatas"][j]["movementData"]["headPositions"]
            Vector2 = [headPositions[i], headPositions[i+2]]
            
            if previousVector2 != None:
                timesTested += 1
                magnitude = math.sqrt(((Vector2[0] - previousVector2[0]) ** 2) + ((Vector2[1] - previousVector2[1]) ** 2))
                
                value = None
                k = 0
                
                tagTimeOffset = 0
                
                l = 0
                while (l < len(REPLAY_JSON["players"])):
                    if (REPLAY_JSON["players"][l]["actornumber"] == REPLAY_JSON["playerDatas"][j]["actorNumber"]):
                        tagTimeOffset = int(REPLAY_JSON["players"][l]["JoinTimes"][0])
                        #print("Mane", tagTimeOffset)
                        v = 0
                        while (v < len(REPLAY_JSON["players"][l]["LeaveTimes"])):
                            if (REPLAY_JSON["players"][l]["LeaveTimes"][v] < time):
                                try:
                                    tagTimeOffset = REPLAY_JSON["players"][l]["JoinTimes"][v+1]
                                except:
                                    pass
                            v += 1
                    l += 1
                            
                # if (tagTimeOffset > 0):
                #     print(tagTimeOffset)
                
                firstFind = False
                while (k < len(REPLAY_JSON["playerDatas"][j]["tagstimes"])):
                    #print ("-------------------------------")
                    #print(str(REPLAY_JSON["playerDatas"][j]["tagstimes"][k]/100) + " | " + str(time))

                    if ((REPLAY_JSON["playerDatas"][j]["tagstimes"][k] - int(tagTimeOffset))/100 < time):
                        value = k
                        firstFind = True
                        #print("Time found", k)
                    k += 2
            
                state = None
                if (value != None):
                    state = int(REPLAY_JSON["playerDatas"][j]["tagstimes"][value - 1])
                    #print("state: " + str(state))
                
                if (state == 0):
                    stateWasOne += 1
                elif (state == 1):
                    stateWasTwo += 1
                elif (state == None):
                    stateWasNone += 1
                    
                if (value == None): 
                    valueWasNone += 1
                else:
                    valueWasValue += 1
                
                if (state == 0):
                    
                    velocityIndex = int((velocityIndex + 1) % velocityHistorySize) 
                    oldestVelocity = velocityHistory[velocityIndex]
                    currentVelocity = DevideVec2([Vector2[0] - previousVector2[0], Vector2[1] - previousVector2[1]], VEL_CHECK_TIME)
                    denomalizedVelocityAverage[0] += DevideVec2([currentVelocity[0] - oldestVelocity[0], currentVelocity[1] - oldestVelocity[1]], velocityHistorySize)[0]
                    denomalizedVelocityAverage[1] += DevideVec2([currentVelocity[0] - oldestVelocity[0], currentVelocity[1] - oldestVelocity[1]], velocityHistorySize)[1]
                    velocityHistory[velocityIndex] = currentVelocity
                    
                    denMag = math.sqrt((denomalizedVelocityAverage[0] ** 2) + (denomalizedVelocityAverage[1] ** 2))
                    
                    velocity.append(denMag)
                    #print(denMag)
                    
                previousVector2 = Vector2
            
            else:
                previousVector2 = Vector2
            
            time += VEL_CHECK_TIME
            
            incFloat = VEL_CHECK_TIME * 60
            #print(incFloat)
            i += int(incFloat)
            
        cleanedVel = []
        
        print("The number of times tested:", timesTested)
        print("The number of data points:", len(velocity))
        print("The number of state was one:", stateWasOne)
        print("The number of state was two:", stateWasTwo)
        print("The number of state was None:", stateWasNone)
        print("The Value was None:", valueWasNone)
        print("The Value was Value:", valueWasValue)
    
        tagsCount = 0
        while (tagsCount < len(REPLAY_JSON["playerDatas"][j]["tagstimes"])):
            print("Tag Time:",REPLAY_JSON["playerDatas"][j]["tagstimes"][tagsCount]/100)
            tagsCount += 2
        
        for x in velocity:
            if (0 < x < 11):
                cleanedVel.append(x)
        
        GenGraph(cleanedVel, REPLAY_JSON["players"][j]["Name"])
        
        j += 1
    
def GenGraph(velocitys, Names):
    
    print(velocitys)
    
    def pdf(x):
        mean = np.mean(x)
        std = np.std(x)
        y_out = 1/(std * np.sqrt(2 * np.pi)) * np.exp( - (x - mean)**2 / (2 * std**2))
        return y_out
    
    # To generate an array of x-values
    x = velocitys
    
    # To generate an array of
    # y-values using corresponding x-values
    y = pdf(x)
    
    # Plotting the bell-shaped curve
    plt.style.use('seaborn')
    plt.figure(figsize = (21, 9))
    # plt.plot(x, y, color = 'black',
    #         linestyle = 'dashed')
    
    plt.scatter( x, y, marker = 'o', s = 25, color = 'red')
    save = input("Save figure? (y/n): ")
    if save == "y":
        plt.savefig(f"./AutoGraphs/{Names}.png")
    plt.show()

if __name__ == "__main__":
    file = "replay_files\PRETSOD3-8-2023+9-16-42+PM+-+Copy.txt"
    main(file)
