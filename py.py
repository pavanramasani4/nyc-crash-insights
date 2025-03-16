import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# Load dataset
CSV_FILE_PATH = "C:/Pavan/VS/JYPNB/WebPage/NYC_Collisions.csv"
data = pd.read_csv(CSV_FILE_PATH, parse_dates=[['Date', 'Time']])
data.columns = data.columns.str.strip().str.upper()  # Clean column names

# Data preprocessing
data['HOUR'] = data['DATE_TIME'].dt.hour

# Initialize the Dash app
dash_app = dash.Dash(__name__)

# Define the layout and visualizations for the Dash app
dash_app.layout = html.Div([
    html.H1("NYC Collisions Dashboard", style={'textAlign': 'center', 'color': 'blue'}),
    
    dcc.Tabs([
        dcc.Tab(label='Persons Injured by Borough', children=[
            dcc.Graph(
                figure=px.bar(
                    data.groupby('BOROUGH')['NUMBER OF PERSONS INJURED'].sum().reset_index(),
                    x='BOROUGH', y='NUMBER OF PERSONS INJURED',
                    color='BOROUGH',
                    title="Persons Injured by Borough"
                )
            )
        ]),

        dcc.Tab(label='Persons Injured by Vehicle Type', children=[
            dcc.Graph(
                figure=px.bar(
                    data.groupby('VEHICLE TYPE CODE 1')['NUMBER OF PERSONS INJURED'].sum().nlargest(10).reset_index(),
                    x='VEHICLE TYPE CODE 1', y='NUMBER OF PERSONS INJURED',
                    color='VEHICLE TYPE CODE 1',
                    title="Top 10 Vehicle Types: Persons Injured"
                )
            )
        ]),

        dcc.Tab(label='Pedestrians Killed by Vehicle Type', children=[
            dcc.Graph(
                figure=px.bar(
                    data.groupby('VEHICLE TYPE CODE 1')['PEDESTRIANS KILLED'].sum().nlargest(10).reset_index(),
                    x='VEHICLE TYPE CODE 1', y='PEDESTRIANS KILLED',
                    color='VEHICLE TYPE CODE 1',
                    title="Top 10 Vehicle Types: Pedestrians Killed"
                )
            )
        ]),

        dcc.Tab(label='Persons Injured by Time of Day', children=[
            dcc.Graph(
                figure=px.line(
                    data.groupby('HOUR')['NUMBER OF PERSONS INJURED'].sum().reset_index(),
                    x='HOUR', y='NUMBER OF PERSONS INJURED',
                    markers=True,
                    title="Persons Injured by Hour of Day"
                )
            )
        ]),

        dcc.Tab(label='Persons Injured by Contributing Factor', children=[
            dcc.Graph(
                figure=px.bar(
                    data.groupby('CONTRIBUTING FACTOR VEHICLE 1')['NUMBER OF PERSONS INJURED'].sum().nlargest(10).reset_index(),
                    x='CONTRIBUTING FACTOR VEHICLE 1', y='NUMBER OF PERSONS INJURED',
                    color='CONTRIBUTING FACTOR VEHICLE 1',
                    title="Top 10 Contributing Factors: Persons Injured"
                )
            )
        ])
    ])
])

# Run the Dash app
if __name__ == '__main__':
    dash_app.run_server(debug=True)
