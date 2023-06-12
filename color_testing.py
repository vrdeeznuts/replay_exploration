import seaborn as sns
import matplotlib.pyplot as plt


colors = sns.color_palette('Set2', n_colors=4)

fig, ax = plt.subplots()

for i, color in enumerate(colors):
    ax.bar(i, 1, color=color)

ax.set_xlim(-0.5, 3.5)
ax.yaxis.set_ticks([])
plt.show()