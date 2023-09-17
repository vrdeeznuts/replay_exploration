import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from sklearn.manifold import TSNE

from Replay import Replay


def make_df(filename):
    replay = Replay(filename)

    # relevant fields we want for each player
    ids = []
    names = []
    x_head_pos = []
    y_head_pos = []
    z_head_pos = []

    # loop over each player's data
    for player in replay.players_stats:
        if 'ref' in player.name.lower() or 'gorillagamer' == player.name.lower():
            continue
        x, y, z = player._parse_positions()
        ids.append(player.id)
        names.append(player.name)
        x_head_pos.append(x)
        y_head_pos.append(y)
        z_head_pos.append(z)

    data = {'id': ids, 
            'name': names, 
            'xHead': x_head_pos, 
            'yHead': y_head_pos, 
            'zHead': z_head_pos}

    df = pd.DataFrame(data)
    return df


def plot_tsne(df):
    # because each player probably has a different number of head positions 
    # due to being in the lobby for different durations, we need to truncate
    # the positions so they all match
    # that's what's going on here
    min_len = min(df['xHead'].apply(len).min(), df['yHead'].apply(len).min(), df['zHead'].apply(len).min())

    xpos = df['xHead'].apply(lambda x: x[:min_len])
    ypos = df['yHead'].apply(lambda x: x[:min_len])
    zpos = df['zHead'].apply(lambda x: x[:min_len])
    xpos = np.array(xpos.tolist())
    ypos = np.array(ypos.tolist())
    zpos = np.array(zpos.tolist())

    # tsne stuff
    feature_matrix = np.column_stack((xpos, ypos, zpos))
    y = df['name']
    tsne = TSNE(n_components=2, perplexity=10, random_state=123)
    z = tsne.fit_transform(feature_matrix)

    tsne_df = pd.DataFrame(z, columns=['tsne_1', 'tsne_2'])
    tsne_df['name'] = y

    # plotting
    fig, ax = plt.subplots(1)
    sns.scatterplot(x='tsne_1', y='tsne_2', data=tsne_df, hue='name')
    ax.set_xlabel('tsne 1')
    ax.set_ylabel('tsne 2')
    ax.legend()

    plt.show()



if __name__ == "__main__":
    f = 'tttvscc_replay.txt'
    players_df = make_df(f)
    plot_tsne(players_df)