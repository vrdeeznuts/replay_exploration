import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class ReplayStats:
    def __init__(self, filename):
        self.filename = filename

        # flatten json df, combine into single df
        df = pd.read_json(filename) # top-level json df
        id_df = pd.DataFrame.from_records(df['players'])
        data_df = pd.DataFrame.from_records(df['playerDatas'])
        movement_df = pd.DataFrame.from_records(data_df['movementData'])
        self.full_df = pd.concat([id_df, data_df, movement_df], axis=1)

        del df
        del id_df
        del data_df
        del movement_df

        self.num_timesteps = self.full_df['headLen'].iloc[0]
        self.Hz = 20 
        self.sampling_rate = 1 / self.Hz # reciprocal of Hz


    def get_fields(self):
        return self.full_df.columns


    def get_players(self):
        return self.full_df['Name'].values


    def get_recording_duration(self):
        print(f"Total number of timesteps: {self.num_timesteps}")
        return self.num_timesteps * self.sampling_rate


    def _calculate_lateral_velocities(self, name):
        velocities = []
        positions = self.full_df.loc[self.full_df['Name'] == name, "headPositions"].values[0]

        for i in range(0, len(positions)-3, 3):
            x1, y1, z1 = positions[i:i+3]
            if i == 0:
                x2, y2, z2 = x1, y1, z1
            else:
                x2, y2, z2 = positions[i+3:i+6]

            coord1 = np.array([x1, z1])
            coord2 = np.array([x2, z2])

            distance = np.linalg.norm(coord2 - coord1) / self.Hz
            velocities.append(distance)

        return velocities

    
    def calculate_lateral_velocities(self):
        all_velocities = []
        for player in self.full_df['Name']:
            player_velocities = self._calculate_lateral_velocities(player)
            all_velocities.append(player_velocities)

        self.full_df['Velocities'] = all_velocities
        print("Lateral velocities calculated for all players.")

    
    def test_calc_vel(self):
        velocities = []
        dt = self.sampling_rate
        z_pos = self.full_df.loc[self.full_df['Name'] == 'ZAINN', 'headPositions'].to_list()
        x = z_pos.apply(lambda row: row[::3])
        z = z_pos.apply(lambda row: row[2::3])

        x = x.to_list()
        z = z.to_list()

        positions = np.array(list(zip(x, z)))

        diff = np.diff(positions, axis=0)

        velocities = diff / dt

        magnitudes = np.linalg.norm(velocities, axis=1)

        mini = np.min(magnitudes)
        maxi = np.max(magnitudes)
        avg = np.mean(magnitudes)
        std = np.std(magnitudes)

        return mini, maxi, avg, std
        
        
    def _get_velocity_statistics(self, row):
        min_vel = np.min(row)
        max_vel = np.max(row)
        avg_vel = np.mean(row)
        std_vel = np.std(row)

        # return [min_vel, avg_vel, max_vel, std_vel]
        return pd.Series({'min': min_vel, 'max': max_vel, 'average': avg_vel, 'std': std_vel})


    def get_velocity_statistics(self):
        statistics = self.full_df['Velocities'].apply(self._get_velocity_statistics)
        statistics['Name'] = self.full_df['Name']
        print(statistics)
