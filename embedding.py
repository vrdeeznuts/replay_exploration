from sklearn.manifold import TSNE
import seaborn as sns
import pandas as pd
import numpy as np
import json


f = open("tttvscc_replay.txt", "r")
text = f.read()
replayData = json.loads(text)
players = replayData["players"]
playerDatas = replayData["playerDatas"]
df = pd.DataFrame(columns=['ID', 'Name', 'Data'])

for i in range(len(players)):
    id = players[i]["id"]
    name = players[i]["Name"]
    data = []
    # Shape should be number_samples, 200, 3
    for j in range(0, playerDatas[i]["movementData"]["headLen"], 3):
        movementData = playerDatas[i]["movementData"]
        dataline = []
        if(len(data) == 200):
            df = pd.concat([df, pd.DataFrame.from_records([{'ID': id, 'Data': data.copy()}])], ignore_index=True)
            data.clear()
        dataline.append(float(movementData["headPositions"][j]))
        dataline.append(float(movementData["headPositions"][j+1]))
        dataline.append(float(movementData["headPositions"][j+2]))
        data.append(dataline)

x = df['Data']
y = df['ID']

tsne = TSNE(n_components=3, perplexity=10, random_state=123)
z = tsne.fit_transform(x)


from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(z[:, 0], z[:, 1], z[:, 2])

ax.set_xlabel('Dimension 1')
ax.set_ylabel('Dimension 2')
ax.set_zlabel('Dimension 3')

plt.show()