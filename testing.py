import os
from pathlib import Path
from Replay import Replay
import matplotlib.pyplot as plt
import seaborn as sns



if __name__ == "__main__":
    base_path = Path('replay_files')
    file = "SCRIMWW4536-12-2023 9-34-29 PM.txt"
    
    replay = Replay(base_path / file)
    
    fig, ax = plt.subplots(figsize=(21, 9))
    
    colors = sns.color_palette('Set2', n_colors=len(replay.players_stats))
    
    for i, player in enumerate(replay.players_stats):
        if 'gorilla' in player.name.lower() or 'mins' in player.name.lower() or 'ref' in player.name.lower():
            continue
        
        speeds = player.pruned_smooth_speeds
        x = speeds[(speeds > 0) & (speeds < 11)]
        y = player.pdf(x)
        ax.scatter(x, y, s=3, color=colors[i], label=player.name) # , alpha=0.5)
        
    ax.set_title('Lateral Speeds (PDF)')
    ax.set_xlabel('Speed (m/s)')
    ax.set_xticks(list(range(12)))
    ax.set_ylabel('Density Estimate')
    
    legend = ax.legend()
    for handle in legend.legendHandles:
        handle._sizes = [20]
        handle.set_alpha(1)
    # plt.legend()
    plt.show()
    
    plt.savefig("WWSCRIM.png")