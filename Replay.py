import os
import json
import datetime
from pprint import pprint
from pathlib import Path
from tabulate import tabulate
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class Replay:
    def __init__(self, filename, hz=20):
        self.filename = filename
        self.hz = hz
        print(f"[INFO] Reading Replay json {self.filename}")
        with open(self.filename) as f:
            data = json.load(f)

        self.data = data
        
        self.version = data["FormatVersion"]
        self.duration = datetime.timedelta(seconds=data['FinalTime'] / self.hz) # recording duration in seconds

        self.players_stats = self.generate_player_stats()


    def get_fields(self):
        for k, v in self.data.items():
            print(k)

            if isinstance(v, list) and isinstance(v[0], dict):
                first_dict = v[0]
                for n_k, n_v in first_dict.items():
                    print(' - ' + n_k)

                    if isinstance(n_v, list) and len(n_v) > 0 and isinstance(n_v[0], dict): # and isinstance(n_v[0], dict):
                        print("yes") 
    
    def generate_player_stats(self, verbose=False):
        players_dicts = [player_dict for player_dict in self.data['players']]
        playerDatas_dicts = [data_dict for data_dict in self.data['playerDatas']]

        for pl_d, pd_d in zip(players_dicts, playerDatas_dicts):
            pd_d['id'] = pl_d['id']
            assert pd_d['actorNumber'] == pl_d['actornumber'], f"The actornumbers don't match! {pd_d['actornumber']} != {pl_d['actornumber']}"
            pd_d['color'] = pl_d['color']
            pd_d['Name'] = pl_d['Name']
            pd_d['JoinTimes'] = pl_d['JoinTimes']
            pd_d['LeaveTimes'] = pl_d['LeaveTimes']

        players_stats = []

        for playerData in playerDatas_dicts:
            player_stats = PlayerStats(playerData, self.hz)
            players_stats.append(player_stats)
            if verbose:
                print(f"[INFO] PlayerStats created for id: {playerData['id']}, name: {playerData['Name']}...")

        if verbose:
            print("[INFO] Done generating PlayerStats.")

        return players_stats


    def join_duplicate_ids(self):
        # if a player leaves and joins back (i.e., there are multiple entries in playerDatas 
        # that contain the same id), merge the data into a single object
        pass
        
        
class PlayerStats:
    def __init__(self, playerDatas_dict, hz):
        # info
        self.id = playerDatas_dict['id']
        self.actornumber = playerDatas_dict['actorNumber']
        self.name = playerDatas_dict['Name']
        self.color = playerDatas_dict['color']
        self.join_times = playerDatas_dict['JoinTimes']
        self.leave_times = playerDatas_dict['LeaveTimes']
        self.raw_tag_times = True
        self.tag_times = playerDatas_dict['tagstimes']

        self.hz = hz
        self.untagged_speed_threshold = 11

        # head
        self.headLen = playerDatas_dict['movementData']['headLen']
        self.headPositions = playerDatas_dict['movementData']['headPositions']
        self.headRotLen = playerDatas_dict['movementData']['headRotLen']
        self.headRot = playerDatas_dict['movementData']['headRot']
        
        # right hand
        self.rightHandPosLen = playerDatas_dict['movementData']['rightHandPosLen']
        self.rightHandPositions = playerDatas_dict['movementData']['rightHandPositions']
        self.rightHandRotLen = playerDatas_dict['movementData']['rightHandRotLen']
        self.rightHandRot = playerDatas_dict['movementData']['rightHandRot']
        
        # left hand
        self.leftHandPosLen = playerDatas_dict['movementData']['leftHandPosLen']
        self.leftHandPositions = playerDatas_dict['movementData']['leftHandPositions']
        self.leftHandRotLen = playerDatas_dict['movementData']['leftHandRotLen']
        self.leftHandRot = playerDatas_dict['movementData']['leftHandRot']

        # calculations
        self.smooth_speeds = self.calculate_lateral_velocities()
        self.raw_speeds = self.calculate_lateral_velocities(raw=True)
        self.pruned_smooth_speeds = self.parse_tag_times()
        self.pruned_raw_speeds = self.parse_tag_times(raw=True)

        # utilities
        self.speeds_mapping = {
            (True, True): self.raw_speeds,
            (False, True): self.pruned_raw_speeds,
            (True, False): self.smooth_speeds,
            (False, False): self.pruned_smooth_speeds
        } # first bool is include_lava, second is raw
        self.colors = sns.color_palette('Set2', n_colors=4)
        self.color_mapping = {
            (True, True): self.colors[0],
            (False, True): self.colors[1],
            (True, False): self.colors[2],
            (False, False): self.colors[3]
        }


    def __repr__(self):
            return f"PlayerStats(id={self.id}, name(s)={self.names})"
        
    def __str__(self):
        table_data = {'id': self.id,
                      'actornumber': self.actornumber,
                      'name(s)': self.names}
        self.table = tabulate(table_data, headers="keys", tablefmt="simplegrid")
        return self.table
        
    def __len__(self):
        return self.headLen

    def __eq__(self, other):
        return self.id == other.id # and self.actornumber == other.actornumber
    

    def parse_tag_times(self, raw=False):
        if raw:
            speeds = self.raw_speeds
        else:
            speeds = self.smooth_speeds

        # tag_times structure: [ts, tagged_bool, ts, tagged_bool, ...]
        # times = np.array(self.tag_times[::2]) / 100. # convert times to index of speeds
        time_idxs = np.array(self.tag_times[::2]) / 5 # convert timestamp to index of speeds
        tagged_bool = np.array(self.tag_times[1::2])

        infected_start = None
        pruned_speeds = []
        for i in range(len(time_idxs)):
            if tagged_bool[i]:
                if infected_start is None:
                    infected_start = time_idxs[i]
            elif not tagged_bool[i] and infected_start is not None:
                infected_end = time_idxs[i]
                pruned_speeds.extend(speeds[int(infected_start):int(infected_end)])
                infected_start = None

        if infected_start is not None:
            pruned_speeds.extend(speeds[int(infected_start):])

        return pd.Series(pruned_speeds)
    

    def _parse_positions(self):
        x = self.headPositions[::3]
        y = self.headPositions[1::3]
        z = self.headPositions[2::3]

        return x, y, z
    

    def _parse_rotations(self):
        x = self.headRot[::3]
        y = self.headRot[1::3]
        z = self.headRot[2::3]

        return x, y, z
    

    def player_statistics(self):
        title = f"{self.name} (id: {self.id}) Untagged Monke Statistics"

        raw_min = self.pruned_raw_speeds.min()
        raw_avg = self.pruned_raw_speeds.mean()
        raw_max = self.pruned_raw_speeds.max()
        raw_std = self.pruned_raw_speeds.std()

        smooth_min = self.pruned_smooth_speeds.min()
        smooth_avg = self.pruned_smooth_speeds.mean()
        smooth_max = self.pruned_smooth_speeds.max()
        smooth_std = self.pruned_smooth_speeds.std()

        data = [
            ['Raw Speed (m/s)', raw_min, raw_avg, raw_max, raw_std],
            ['Smooth Speed (m/s)', smooth_min, smooth_avg, smooth_max, smooth_std]
        ]

        headers = ['Min', 'Max', 'Average', 'Std. Dev.']

        table = tabulate(data, headers=headers, tablefmt="simplegrid")

        out = f"{title}\n{table}"

        print(out)
    

    def calculate_lateral_velocities(self, raw=False):
        if raw:
            speed = self._calculate_lateral_velocities_raw()
        else:
            speed = self._calculate_lateral_velocities()

        return speed
        
    

    def _calculate_lateral_velocities(self, history=9):
        xpos, ypos, zpos = self._parse_positions()
        df = pd.DataFrame({'x': xpos, 'y': ypos, 'z': zpos})
        
        df['distance'] = np.sqrt((df['x'].diff())**2 + (df['z'].diff())**2)
        df['cumulative_distance'] = df['distance'].rolling(window=history, min_periods=1).sum()
        df['speed'] = df['cumulative_distance'] / (history * (1 / self.hz))

        return df['speed']

    
    def _calculate_lateral_velocities_raw(self):
        xpos, ypos, zpos = self._parse_positions()
        df = pd.DataFrame({'x': xpos, 'y': ypos, 'z': zpos})

        df['distance'] = np.sqrt((df['x'].diff())**2 + (df['z'].diff()**2))
        df['raw_speed'] = df['distance'] / (1 / self.hz)

        return df['raw_speed']


    def plot_velocities_kde(self, include_lava=False, raw=False, save=False):
        speeds = self.speeds_mapping[(include_lava, raw)]

        plt.figure(figsize=(21, 9))

        # remove super large velocities
        speeds_in_range = speeds[(speeds > 0) & (speeds < self.untagged_speed_threshold)]

        sns.kdeplot(speeds_in_range, color=self.color_mapping[tuple(speeds)], shade=True)
        plt.title(f"{self.name}'s Velocity (Kernel Density Estimate) over {len(speeds_in_range) / 20} seconds")
        plt.xlabel("Speed (units/s)")
        plt.ylabel("Density Estimate")
        plt.show()
        if save:
            plot_path = Path("replays") / f"{self.name}_kde.png"
            counter = 1
            while os.path.exists(plot_path):
                counter_str = str(counter).zfill(2)
                plot_path = plot_path.name.append(f"_{counter_str}.png")

            plt.savefig(plot_path)
            print(f"[INFO] Plot saved as: {plot_path}.")


    def pdf(self, x):
        y = 1 / (x.std() * np.sqrt(2 * np.pi)) * np.exp(-(x - x.mean())**2 / (2 * x.std()**2))
        return y


    def plot_velocities_pdf(self, include_lava=False, raw=False, save=False):
        speeds = self.speeds_mapping[(include_lava, raw)]

        plt.figure(figsize=(21, 9))

        # remove super large velocities
        speeds_in_range = speeds[(speeds > 0) & (speeds < 11)]
        
        y = self.pdf(speeds_in_range)

        plt.scatter(speeds_in_range, y, s=25, color=self.color_mapping[tuple(speeds)])
        plt.title(f"{self.name}'s Velocity (Probability Density Function) over {len(speeds_in_range) / 20} seconds")
        plt.xlabel("Speed (m/s)")
        plt.ylabel("Density Estimate")
        plt.show()
        if save:
            plot_path = Path("replays") / f"{self.name}_pdf.png"
            counter = 1
            while os.path.exists(plot_path):
                counter_str = str(counter).zfill(2)
                plot_path = plot_path.name.append(f"_{counter_str}.png")

            plt.savefig(plot_path)
            print(f"[INFO] Plot saved as: {plot_path}.")
        

    def plot_all(self, save=False):
        # graphs (12 total)
        # pdf, kde, histogram (3)
        # raw, smooth, pruned raw, pruned smooth (4)

        fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(21, 21))

        label_mapping = ['all raw', 'all smooth', 'untagged raw', 'untagged smooth']

        # ax1: PDF; ax2: KDE; ax3: histogram
        for i, speeds in enumerate([self.raw_speeds, self.smooth_speeds, self.pruned_raw_speeds, self.pruned_smooth_speeds]):
            color = self.colors[i]
            label = label_mapping[i]
            alpha = 0.5
            
            # set data range from (0, 11)
            speeds_in_range = speeds[(speeds > 0) & (speeds < 11)]
            y = self.pdf(speeds_in_range)
            
            # plots
            axs[0].scatter(speeds_in_range, y, color=color, label=label, alpha=alpha) # pdf
            sns.kdeplot(speeds_in_range, ax=axs[1], color=color, fill=True, label=label, alpha=alpha)
            axs[2].hist(speeds_in_range, bins=np.arange(0, 11.25, .25), color=color, label=label, alpha=alpha)

        # x-axis shared
        fig.text(0.5, 0.04, 'Speed (m/s)', ha='center') # , fontsize=12)
        xticks = list(range(12))
        axs[0].set_xticks(xticks)
        axs[1].set_xticks(xticks)
        axs[2].set_xticks(xticks)

        # y-axis
        axs[0].set_ylabel('Density Estimate')
        axs[1].set_ylabel('Density Estimate')
        axs[2].set_ylabel('Frequency (Count)')

        # legends
        axs[0].legend()
        axs[1].legend()
        axs[2].legend()

        # titles
        axs[0].set_title('PDF')
        axs[1].set_title('KDE')
        axs[2].set_title('Histogram')
        fig.suptitle(f'{self.name} (id: {self.id}): Lateral Speeds from Replay')

        plt.show()

        if save:
            plot_path = Path("replays") / f"{self.name}_pdf.png"
            counter = 1
            while os.path.exists(plot_path):
                counter_str = str(counter).zfill(2)
                plot_path = plot_path.name.append(f"_{counter_str}.png")

            plt.savefig(plot_path)
            print(f"[INFO] Plot saved as: {plot_path}.")