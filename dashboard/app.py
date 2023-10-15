import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import requests
import dash_bootstrap_components as dbc

# Sample data for the multi-bar chart
# youtube_df = pd.DataFrame({
#     'country': ['USA', 'Canada', 'UK', 'Australia'],
#     'subscribers': [100, 200, 150, 120],
#     'videos': [500, 400, 300, 200],
#     'likes': [1000, 800, 600, 400],
#     'comments': [300, 250, 200, 150],
#     'views': [2000, 1600, 1200, 800]
# })
# Fetch data from your Flask API
api_url = 'http://127.0.0.1:5000/controller_youtube_channel/api/youtube_channel_data'
response = requests.get(api_url)
data = response.json()

# Convert the data into a DataFrame
df = pd.DataFrame(data)

# Calculate the percentage values for each metric
for col in ['subscribers', 'videos', 'likes', 'comments', 'views']:
    df[f'{col} (%)'] = (df[col] / df[col].sum()) * 100

# Sample data for the line chart (replace with your data)
# data_reddit = pd.DataFrame({
#     'submission_time': pd.to_datetime(['2023-10-01 08:00:00', '2023-10-01 10:00:00', '2023-10-01 12:00:00', '2023-10-01 14:00:00', '2023-10-01 16:00:00']),
#     'likes': [100, 150, 200, 250, 300],
#     'num_comments': [10, 15, 20, 25, 30]
# })
api_url = 'http://127.0.0.1:5000/controller_post_cleaned_reddit/api/post_cleaned_reddit_data'
response = requests.get(api_url)
data_reddit = response.json()

# data_youtube = pd.DataFrame({
#     'submission_time': pd.to_datetime(['2023-10-01 08:00:00', '2023-10-01 10:00:00', '2023-10-01 12:00:00', '2023-10-01 14:00:00', '2023-10-01 16:00:00']),
#     'likes': [80, 120, 160, 200, 240],
#     'num_comments': [8, 12, 16, 20, 24]
# })
api_url = 'http://127.0.0.1:5000/controller_post_cleaned_reddit/api/post_cleaned_youtube_data'
response = requests.get(api_url)
data_youtube = response.json()


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create the multi-bar chart with percentage y-axis label
def create_multi_bar_chart():
    traces = []
    
    for col in ['subscribers (%)', 'videos (%)', 'likes (%)', 'comments (%)', 'views (%)']:
        trace = go.Bar(
            x=df['source'],
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

    return dcc.Graph(figure=fig)

# Create the line chart
def create_line_chart(tab):
    if tab == 'Reddit':
        data = data_reddit
    elif tab == 'Youtube':
        data = data_youtube

    fig = px.line(data, x='submission_time', y=['likes', 'num_comments'], title='Likes and Comments Over Time')
    fig.update_layout(
        xaxis_title='Upload Time',
        yaxis_title='Count',
        template='plotly_dark',
    )

    return dcc.Graph(figure=fig, style={'height': '72vh'})

# Define the layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.Div([
            html.H1("Pizza Hut Social Media Data Dashboard", style={'color': 'white', 'background-color': 'black'}),
            create_multi_bar_chart(),
        ]), width=12, style={'padding': '20px', 'background-color': 'grey'}),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Tabs(id='tabs', value='Reddit', children=[
                dcc.Tab(label='Reddit', value='Reddit', style={'color': 'white', 'background-color': 'black', 'font-size': '25px'}),
                dcc.Tab(label='Youtube', value='Youtube', style={'color': 'white', 'background-color': 'black', 'font-size': '25px'}),
            ]),
            html.Div(id='tabs-content', style={'background-color': 'grey'}),
        ], width=12, style={'padding': '20px', 'background-color': 'grey'}),
    ]),
])

@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value')]
)
def render_content(tab):
    return create_line_chart(tab)

if __name__ == '__main__':
    app.run_server(debug=True)
