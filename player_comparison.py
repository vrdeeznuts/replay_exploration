from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from Replay import Replay

base_path = Path("replay_files")
f1 = "SCRIMWW4536-12-2023 9-34-29 PM.txt"
f2 = "ST7NKY3-9-2023 5-47-25 PM.txt"
f3 = "WTSOW13-5-2023 7-34-42 PM.txt"
f4 = "PRETSOD3-8-2023 9-16-42 PM.txt"

r1 = Replay(base_path / f1)
r2 = Replay(base_path / f2)
r3 = Replay(base_path / f3)
r4 = Replay(base_path / f4)

for player in r1.players_stats:
    if 'deez' in player.name.lower():
        deez = player
        print(f"Found {player.name}")
        print(player.headLen)
    
for player in r2.players_stats:
    if 'dawn' in player.name.lower():
        dawn = player
        print(f"Found {player.name}")
        print(player.headLen)
    if 'snoopy' in player.name.lower():
        snoopy = player
        print(f"Found {player.name}")
        print(player.headLen)
        
for player in r3.players_stats:
    if 'phinix' in player.name.lower():
        phinix = player
        print(f"Found {player.name}")
        print(player.headLen)
        
# for player in r4.players_stats:
#     if 'turb' in player.name.lower():
#         swipz = player
#         print(f"Found {player.name}")
#         print(player.headLen)

    
deez_speeds = deez.pruned_smooth_speeds
dawn_speeds = dawn.pruned_smooth_speeds
snoo_speeds = snoopy.pruned_smooth_speeds
phin_speeds = phinix.pruned_smooth_speeds
# swip_speeds = swipz.pruned_smooth_speeds

dz_x = deez_speeds[(deez_speeds > 0) & (deez_speeds < 11)]
dw_x = dawn_speeds[(dawn_speeds > 0) & (dawn_speeds < 11)]
sn_x = snoo_speeds[(snoo_speeds > 0) & (snoo_speeds < 11)]
ph_x = phin_speeds[(phin_speeds > 0) & (phin_speeds < 11)]
# sw_x = swip_speeds[(swip_speeds > 0) & (swip_speeds < 11)]

dz_y = deez.pdf(dz_x)
dw_y = dawn.pdf(dw_x)
sn_y = snoopy.pdf(sn_x)
ph_y = phinix.pdf(ph_x)
# sw_y = swipz.pdf(sw_x)

plt.figure(figsize=(21, 9))

plt.scatter(dz_x, dz_y, color='green', label=f'Deez ({len(dz_x)} points)', alpha=0.7)
plt.scatter(dw_x, dw_y, color='red', label=f'Dawn ({len(dw_x)} points)', alpha=0.7)
plt.scatter(sn_x, sn_y, color='orange', label=f'Snoopy ({len(sn_x)} points)', alpha=0.7)
plt.scatter(ph_x, ph_y, color='goldenrod', label=f'Phinix ({len(ph_x)} points)', alpha=0.7)
# plt.scatter(sw_x, sw_y, color='tomato', label=f'Turban ({len(sw_x)} points)', alpha=0.7)

plt.title('Lateral Speed Comparison')
plt.xlabel('Speed (m/s)')
plt.ylabel('Density Estimate')
plt.xticks(list(range(12)))
plt.legend()
plt.savefig(Path('AutoGraphs') / 'speed_comparison.png')
plt.show()