import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Sample data for YouTube, Reddit, and Popularity
youtube_data = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D'],
    'Views': [1000, 1500, 700, 1200],
    'Likes': [500, 800, 400, 600]
})

reddit_data = pd.DataFrame({
    'Date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
    'Upvotes': [50, 75, 30, 60, 45, 70, 55, 80, 40, 65],
    'Comments': [10, 15, 5, 12, 8, 18, 14, 20, 7, 16]
})

popularity_data = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D'],
    'Popularity': [20, 30, 15, 25]
})

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout of the app with tabs
app.layout = html.Div([
    html.H1("Social Media Data Analysis Dashboard"),
    
    dcc.Tabs(id='tabs', value='youtube-tab', children=[
        dcc.Tab(label='YouTube', value='youtube-tab'),
        dcc.Tab(label='Reddit', value='reddit-tab'),
        dcc.Tab(label='Popularity', value='popularity-tab')
    ]),
    
    html.Div(id='tab-content'),
])

# Define callbacks to update the content of the selected tab
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def render_tab_content(tab):
    if tab == 'youtube-tab':
        # Create YouTube tab content with bar chart and circle chart
        youtube_bar_chart = dcc.Graph(id='youtube-bar-chart')
        youtube_circle_chart = dcc.Graph(id='youtube-circle-chart')
        
        return [
            html.H2("YouTube Data Analysis"),
            youtube_bar_chart,
            youtube_circle_chart
        ]
    elif tab == 'reddit-tab':
        # Create Reddit tab content with line chart and bar chart
        reddit_line_chart = dcc.Graph(id='reddit-line-chart')
        reddit_bar_chart = dcc.Graph(id='reddit-bar-chart')
        
        return [
            html.H2("Reddit Data Analysis"),
            reddit_line_chart,
            reddit_bar_chart
        ]
    elif tab == 'popularity-tab':
        # Create Popularity tab content with a bar chart
        popularity_bar_chart = dcc.Graph(id='popularity-bar-chart')
        
        return [
            html.H2("Popularity Data Analysis"),
            popularity_bar_chart
        ]

# Define callbacks to update the charts
@app.callback(
    Output('youtube-bar-chart', 'figure'),
    Input('tabs', 'value')
)
def update_youtube_bar_chart(tab):
    if tab == 'youtube-tab':
        # Create a bar chart for YouTube data
        fig = px.bar(youtube_data, x='Category', y='Views', title='YouTube Views by Category')
        return fig

@app.callback(
    Output('youtube-circle-chart', 'figure'),
    Input('tabs', 'value')
)
def update_youtube_circle_chart(tab):
    if tab == 'youtube-tab':
        # Create a circle chart for YouTube data
        fig = px.pie(youtube_data, names='Category', values='Likes', title='YouTube Likes by Category')
        return fig

@app.callback(
    Output('reddit-line-chart', 'figure'),
    Input('tabs', 'value')
)
def update_reddit_line_chart(tab):
    if tab == 'reddit-tab':
        # Create a line chart for Reddit data
        fig = px.line(reddit_data, x='Date', y='Upvotes', title='Reddit Upvotes Over Time')
        return fig

@app.callback(
    Output('reddit-bar-chart', 'figure'),
    Input('tabs', 'value')
)
def update_reddit_bar_chart(tab):
    if tab == 'reddit-tab':
        # Create a bar chart for Reddit data
        fig = px.bar(reddit_data, x='Date', y='Comments', title='Reddit Comments Over Time')
        return fig

@app.callback(
    Output('popularity-bar-chart', 'figure'),
    Input('tabs', 'value')
)
def update_popularity_bar_chart(tab):
    if tab == 'popularity-tab':
        # Create a bar chart for popularity data
        fig = px.bar(popularity_data, x='Category', y='Popularity', title='Popularity by Category')
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
