from ReplayStats import ReplayStats


file = "replay_files\PRETSOD3-8-2023 9-16-42 PM.txt"

replay = ReplayStats(file)

print(replay.get_fields())
print(replay.get_players())
print(replay.get_recording_duration(), "seconds")

replay.calculate_lateral_velocities()

replay.get_velocity_statistics()

mi, ma, av, st = replay.test_calc_vel()