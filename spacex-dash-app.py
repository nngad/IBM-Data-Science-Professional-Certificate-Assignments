# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                                            [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                    value='ALL',
                                    placeholder='Select a Launch Site',
                                    searchable=True
                                ),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                
                                dcc.RangeSlider(
                                    id='payload-slider',          # Unique ID for the slider
                                    min=0,                        # Minimum value of the slider (Kg)
                                    max=10000,                    # Maximum value of the slider (Kg)
                                    step=1000,                    # Interval between slider steps (Kg)
                                    marks={i: str(i) for i in range(0, 10001, 1000)},  # Marks every 1000 Kg
                                    value=[min_payload, max_payload]  # Initial selected range
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ]),

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Total successful launches by site
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Successes']
        fig = px.pie(success_counts, names='Launch Site', values='Successes',
                     title='Total Successful Launches by Site')
    else:
        # Success vs. Failure for selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]['class'].value_counts().reset_index()
        filtered_df.columns = ['class', 'count']
        filtered_df['class'] = filtered_df['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(filtered_df, names='class', values='count',
                     title=f'Success vs. Failure for site {selected_site}')
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter_plot(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for site {selected_site}'
        )
    return fig


# Run the app
if __name__ == '__main__':
    app.run(port =8060)
