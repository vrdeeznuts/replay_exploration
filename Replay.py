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


    def get_fields(self):
        for k, v in self.data.items():
            print(k)

            if isinstance(v, list) and isinstance(v[0], dict):
                first_dict = v[0]
                for n_k, n_v in first_dict.items():
                    print(' - ' + n_k)

                    if isinstance(n_v, list) and len(n_v) > 0 and isinstance(n_v[0], dict): # and isinstance(n_v[0], dict):
                        print("yes") 
    
    def generate_player_stats(self):
        players_dicts = [player_dict for player_dict in self.data['players']]
        playerDatas_dicts = [data_dict for data_dict in self.data['playerDatas']]

        for pl_d, pd_d in zip(players_dicts, playerDatas_dicts):
            pd_d['id'] = pl_d['id']
            assert pd_d['actorNumber'] == pl_d['actornumber'], f"The actornumbers don't match! {pd_d['actornumber']} != {pl_d['actornumber']}"
            pd_d['color'] = pl_d['color']
            pd_d['Name'] = pl_d['Name']
            pd_d['JoinTimes'] = pl_d['JoinTimes']
            pd_d['LeaveTimes'] = pl_d['LeaveTimes']

        self.players_stats = []

        for playerData in playerDatas_dicts:
            player_stats = PlayerStats(playerData, self.hz)
            self.players_stats.append(player_stats)
            print(f"[INFO] PlayerStats created for id: {playerData['id']}, name: {playerData['Name']}...")

        print("[INFO] Done generating PlayerStats.")


    def join_duplicate_ids(self, all_players):
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
        self.hz = hz

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
        return self.id == other.id and self.actornumber == other.actornumber
    

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
    

    def calculate_lateral_velocities(self, history=9):
        xpos, ypos, zpos = self._parse_positions()
        df = pd.DataFrame({'x': xpos, 'y': ypos, 'z': zpos})
        
        df['distance'] = np.sqrt((df['x'].diff())**2 + (df['z'].diff())**2)
        df['cumulative_distance'] = df['distance'].rolling(window=history, min_periods=1).sum()
        df['speed'] = df['cumulative_distance'] / (history * (1 / self.hz))

        self.speeds = df['speed']
    

    def plot_velocities_kde(self, save=False):
        if not hasattr(self, 'speeds'):
            self.calculate_lateral_velocities()
            assert hasattr(self, 'speeds')

        plt.figure(figsize=(21, 9))

        # remove super large velocities
        pruned_speeds = self.speeds[(self.speeds > 0) & (self.speeds < 11)]

        sns.kdeplot(pruned_speeds, color='blue', shade=True)
        plt.title(f"{self.name}'s Velocity (Kernel Density Estimate) over {len(pruned_speeds) / 20} seconds")
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


    def plot_velocities_pdf(self, save=False):
        def pdf(x):
            y = 1 / (x.std() * np.sqrt(2 * np.pi)) * np.exp(-(x - x.mean())**2 / (2 * x.std()**2))
            return y
        
        if not hasattr(self, 'speeds'):
            self.calculate_lateral_velocities()
            assert hasattr(self, 'speeds')

        plt.figure(figsize=(21, 9))

        # remove super large velocities
        pruned_speeds = self.speeds[(self.speeds > 0) & (self.speeds < 11)]
        
        y = pdf(pruned_speeds)

        plt.scatter(pruned_speeds, y, s=25, color='blue')
        plt.title(f"{self.name}'s Velocity (Probability Density Function) over {len(pruned_speeds) / 20} seconds")
        plt.xlabel("Speed (units/s)")
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
        