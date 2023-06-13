from pathlib import Path
import pandas as pd
from Replay import Replay
import plotly.express as px
import plotly.graph_objects as go
from plotly_resampler import FigureResampler


base_path = Path("replay_files")
file = "SCRIMWW4536-12-2023 9-34-29 PM.txt"

replay = Replay(base_path / file)
fig = go.Figure()

for player in replay.players_stats:
    if 'gorilla' in player.name.lower() or 'mins' in player.name.lower() or 'ref' in player.name.lower():
        continue
    
    speeds = player.pruned_smooth_speeds
    x = speeds[(speeds > 0) & (speeds < 11)]
    y = player.pdf(x)
    df = pd.DataFrame({'x': x, 'y': y})
    df_sorted = df.sort_values('x')

    fig.add_trace(go.Scatter(x=df_sorted['x'], y=df_sorted['y'], mode='lines', name=player.name))
    
fig.update_layout(
    hovermode='x unified',
    xaxis_title="Speed (m/s)",
    xaxis=dict(tickmode='array', tickvals=list(range(12))),
    yaxis_title="Density Estimate",
    title="Lateral Speed of all Untagged Monkes During Silly vs. WW Scrim",
    width=1080,
    height=600,
)

# fig = go.Figure(data, layout=layout)

fig.write_html('wwscrim_interactive.html')