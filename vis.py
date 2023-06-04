import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

files = [file for file in os.listdir() if file.endswith('.txt')]
colormap = matplotlib.colormaps.get_cmap('tab20')
colors = [colormap(i) for i in range(10)]

for file in files:
    df = pd.read_json(file)
    id_df = pd.DataFrame.from_records(df['players'])
    data_df = pd.DataFrame.from_records(df['playerDatas'])
    movement_df = pd.DataFrame.from_records(data_df['movementData'])
    num_timesteps = movement_df['headLen'].iloc[0]

    if num_timesteps > 1000:
        manager = plt.get_current_fig_manager()
        manager.resize(*manager.window.maxsize())

    data = {'Name': id_df['Name'], 'Color': id_df['color'], 'HeadPosition': movement_df['headPositions']}
    pruned_df = pd.DataFrame(data)

    names = pruned_df['Name'].tolist()
    names[0] = "REPLAY MOD"

    for i, row in pruned_df.iterrows():
        sns.kdeplot(row['HeadPosition'], color=colors[i])
    plt.title(f"KDE Plot of Head Position for {num_timesteps} Samples")
    plt.xlabel("Head Position (units=?)")
    plt.ylabel("Density")
    plt.legend(names)
    plt.show()
    break




# df = pd.read_json(file)
# # print(df.columns)
# # print(df.head(1))

# id_df = pd.DataFrame.from_records(df['players'])
# data_df = pd.DataFrame.from_records(df['playerDatas'])
# movement_df = pd.DataFrame.from_records(data_df['movementData'])

# print(id_df.columns)
# print(data_df.columns)
# print(movement_df.columns)
# print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")



# data = {'Name': id_df['Name'], 'Color': id_df['color'], 'HeadPosition': movement_df['headPositions']}
# new_df = pd.DataFrame(data)
# print(new_df.head(1))
# print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")



# stats = new_df['HeadPosition'].apply(lambda x: pd.Series(x).describe())
# stats['Name'] = new_df['Name']
# print(stats)
# print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")



# print(movement_df['headLen'])
# print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")



# deez = new_df.iloc[-1]
# pos = deez['HeadPosition']

# pos_sorted = sorted(pos)


# colormap = plt.cm.get_cmap('tab20', len(new_df))

# colors = [colormap(i) for i in range(10)]

# # sns.kdeplot(pos_sorted, color='blue', shade=True)
# # plt.plot(range(len(pos_sorted)), pos_sorted)

# labels = new_df['Name'].tolist()
# labels[0] = "POGO=REPLAYMOD"
# for i, row in new_df.iterrows():
#     sns.kdeplot(sorted(row['HeadPosition']), color=colors[i])

# plt.legend(labels)
# plt.show()