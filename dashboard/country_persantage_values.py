import dash
import requests
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


# Fetch data from your Flask API
api_url = 'http://127.0.0.1:5000/controller_youtube_channel/api/youtube_channel_data'
response = requests.get(api_url)
data = response.json()

# Convert the data into a DataFrame
df = pd.DataFrame(data)

# Calculate the percentage values for each metric
for col in ['subscribers', 'videos', 'likes', 'comments', 'views']:
    df[f'{col} (%)'] = (df[col] / df[col].sum()) * 100

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Pizza Hut Social Media Data Dashboard"),
    dcc.Graph(id='multi-bar-charts'),
])

# Define a callback to update the multi-bar charts
@app.callback(
    Output('multi-bar-charts', 'figure'),
    Input('multi-bar-charts', 'relayoutData')
)
def update_multi_bar_charts(_):
    traces = []
    
    for col in ['subscribers (%)', 'videos (%)', 'likes (%)', 'comments (%)', 'views (%)']:
        trace = go.Bar(
            x=df['country'],
            y=df[col],
            name=col,
        )
        traces.append(trace)

    layout = go.Layout(
        barmode='group',
        title='YouTube Channel Analytics by Country (Percentage)',
        xaxis={'title': 'Country'},
        yaxis={'title': 'Percentage (%)'},
        template='plotly_dark'
    )
    
    fig = go.Figure(data=traces, layout=layout)

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
