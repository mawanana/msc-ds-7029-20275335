import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

# Sample data for India, Sri Lanka, Canada, and South Africa
data = pd.DataFrame({
    'Country': ['India', 'Sri Lanka', 'Canada', 'South Africa'],
    'Subscribers': [1000000, 250000, 500000, 750000],
    'Videos': [500, 300, 600, 400],
    'Likes': [50000, 3000, 6000, 40000],
    'Comments': [2000, 100, 400, 1500],
    'Views': [10000000, 300000, 5000000, 7500000]
})

# Calculate the percentage values
for col in ['Subscribers', 'Videos', 'Likes', 'Comments', 'Views']:
    data[f'{col} (%)'] = (data[col] / data[col].sum()) * 100

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Social Media Data Dashboard"),
    dcc.Graph(id='multi-bar-charts'),
])

# Define a callback to update the multi-bar charts
@app.callback(
    Output('multi-bar-charts', 'figure'),
    Input('multi-bar-charts', 'relayoutData')
)
def update_multi_bar_charts(_):
    traces = []
    
    for col in ['Subscribers (%)', 'Videos (%)', 'Likes (%)', 'Comments (%)', 'Views (%)']:
        trace = go.Bar(
            x=data['Country'],
            y=data[col],
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
