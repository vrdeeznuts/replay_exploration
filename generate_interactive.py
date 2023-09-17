from pathlib import Path
import pandas as pd
from Replay import Replay
import plotly.express as px
import plotly.graph_objects as go
from plotly_resampler import FigureResampler


base_path = Path("replay_files")
file = "TTTVADRNL9-1-2023 6-46-14 PM.txt"

replay = Replay(base_path / file)
fig = go.Figure()

for player in replay.players_stats:
    # remove ref/caster/etc player data from graphs
    if 'gorilla' == player.name.lower() or 'mins' in player.name.lower() or 'ref' == player.name.lower():
        continue
    
    speeds = player.pruned_smooth_speeds
    x = speeds[(speeds > 5)] # & (speeds < 11)]
    y = player.pdf(x)
    df = pd.DataFrame({'x': x, 'y': y})
    df_sorted = df.sort_values('x')

    fig.add_trace(go.Scatter(x=df_sorted['x'], y=df_sorted['y'], mode='lines', name=f"{player.name}: {len(df_sorted)} samples"))
    
fig.update_layout(
    hovermode='x unified',
    xaxis_title="Speed (m/s)",
    xaxis=dict(tickmode='array', tickvals=list(range(12))),
    yaxis_title="Density Estimate",
    title="Lateral Speed of all Untagged Monkes During TTT vs. Cheaters Scrim",
    width=1080,
    height=600,
)

# fig = go.Figure(data, layout=layout)

fig.write_html('tttvcheddar_sept1_interactive.html')