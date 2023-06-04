from ReplayStats import ReplayStats


file = "replay_files\TTTGOODNOW5-31-2023 7-05-52 PM.txt"

replay = ReplayStats(file)

print(replay.get_fields())

replay.calculate_lateral_velocities()

replay.get_velocity_statistics()