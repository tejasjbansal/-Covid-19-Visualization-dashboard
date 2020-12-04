import pandas as pd
import requests
import dash
#import dash_auth
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from dash.dependencies import Input, Output,State

#VALID_USERNAME_PASSWORD_PAIRS = {
#    'covid': '2019'
#}

external_stylesheets = ["assets/main.css"]
app = dash.Dash(__name__,external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

#auth = dash_auth.BasicAuth(
#    app,
#    VALID_USERNAME_PASSWORD_PAIRS
#)
server = app.server
daily_case_url = 'https://api.covid19india.org/data.json'
daily_case = requests.get(daily_case_url)
daily_case = daily_case.json()
daily_cases = pd.DataFrame(daily_case['cases_time_series'])

def fig_fun():
    dd = pd.DataFrame(daily_case['statewise'])
    dd = dd.loc[1:]
    geojson = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'
    fig = px.choropleth(dd, geojson=geojson,color='state',
                        locations="state", featureidkey="properties.ST_NM",
                        projection="mercator",hover_data=["active","confirmed", "deaths", "recovered"]
                    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def ploting():
    dd = pd.DataFrame(daily_case['statewise'])
    dd = dd.loc[1:]
    fig = make_subplots(rows=2, cols=2,subplot_titles=("Active", "Confirmed", "Deaths", "Recovered"))

    fig.append_trace(go.Bar(
        x=dd['statecode'],
        y=dd['active'],
        name='Active'
    ), row=1, col=1)

    fig.append_trace(go.Scatter(
        x=dd['statecode'],
        y=dd['confirmed'],
        mode='markers',
        name='Confirmed'
    ), row=1, col=2)

    fig.append_trace(go.Scatter(
        x=dd['statecode'],
        y=dd['deaths'],
        mode='lines+markers',
        name='Deaths'
    ), row=2, col=1)

    fig.append_trace(go.Scatter(
        x=dd['statecode']
        ,y=dd['recovered'],
        name='Recovered'
    ), row=2, col=2)


    fig.update_layout(height=600, width=1200, title_text="Spread Trends")
    return fig

app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content'),
           
],style={'textAlign':'center'})

Page_1_layout = html.Div([
                html.H1(["Coronavirus Disease (COVID-19) Dashboard"],style={'background':'black',"color":'blue'}),
                html.Div([
                    html.H3(['Globally, as of 10:34am CEST,{}, there have been {} confirmed cases of COVID-19, including {} deaths, reported to WHO.'.format(daily_cases['date'][len(daily_cases)-1],daily_cases['totalconfirmed'][len(daily_cases)-1],daily_cases['totaldeceased'][len(daily_cases)-1])]),
                ]),
                html.Div([
                    html.H4(
                    "Total Confirmed {}".format(daily_cases['totalconfirmed'][len(daily_cases)-1])   
                    ),
                html.H4(
                    "Total Deaths {}".format(daily_cases['totaldeceased'][len(daily_cases)-1])
                ),
                html.H4(
                    "Total Recovery {}".format(daily_cases['totalrecovered'][len(daily_cases)-1])
                ),
                html.H4(
                    "Daily Confirmed {}".format(daily_cases['dailyconfirmed'][len(daily_cases)-1])
                ),
                ],style={'color':'red'}),
                html.Br(),
                html.Div([
                    dcc.Graph(id='indiamap',figure= fig_fun())
                ]),
                html.Br(),
                html.Div([
                    dcc.Graph(id='states-plotes',figure=ploting())
                ]),
                dcc.Link('Search By State Name', href='/state',id='mylink'),
])

Page_2_layout = html.Div([
                html.H1(["Coronavirus Disease (COVID-19) Dashboard"],style={'background':'black',"color":'blue'}),
                html.H3("Enter your State Name"),
                html.Div([
                dcc.Input(
                id='input-on-submit',
                placeholder='Enter your state...',
                type='text',
                value='Uttar Pradesh',
                style={'fontsize':24}
            ),],style={'textAlign':'center'}),
            html.Br(),
            html.Button('Submit', id='submit-val', n_clicks=0,style={'fontsize':24}),
            html.Div([
            html.H4(id='hover-data', style={'paddingTop':35})
            ], style={'width':'30%'}),
            html.Div([
                dcc.Graph(id='graph')
            ]),
            html.Div([
            dcc.Graph(id='feature-graphic')
        ])
])


@app.callback(Output("feature-graphic","figure"),
        [Input("submit-val","n_clicks")],
        [State('input-on-submit','value')])

def display_map2(n_clicks,district):
    uurl = "https://api.covid19india.org/state_district_wise.json"
    All_district = requests.get(uurl)
    data = All_district.json()
    Any_map = pd.DataFrame(data[district]['districtData'])
    Any_map = Any_map.T
    Any_map.drop('delta',axis=1,inplace=True)
    Any_map.reset_index(inplace=True)
    Any_map.rename(columns={'index':'District'},inplace=True)
    
    fig = make_subplots(rows=2, cols=2,subplot_titles=("Active", "Confirmed", "Deaths", "Recovered"))

    fig.append_trace(go.Scatter(
        x=Any_map['District'],
        y=Any_map['active'],
        name='Active'
    ), row=1, col=1)

    fig.append_trace(go.Scatter(
        x=Any_map['District'],
        y=Any_map['confirmed'],
        name="Confirmed"
    ), row=1, col=2)

    fig.append_trace(go.Scatter(
        x=Any_map['District']
        ,y=Any_map['deceased'],
        name='Deaths'
    ), row=2, col=1)

    fig.append_trace(go.Scatter(
        x=Any_map['District']
        ,y=Any_map['recovered'],
        name='Recoverd'
    ), row=2, col=2)


    fig.update_layout(height=800, width=1200, title_text="Spread Trends")
    return fig




@app.callback(
    Output('hover-data', 'children'),
    [Input('graph', 'hoverData')])
def callback_image(hoverData):
    
    location = hoverData['points'][0]['location']
    Active_case = hoverData['points'][0]['customdata'][0]
    return location + " active cases " + str(Active_case)


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/state':
        return Page_2_layout
    else:
        return Page_1_layout



@app.callback(Output("graph","figure"),
        [Input("submit-val","n_clicks")],
        [State('input-on-submit','value')])

def display_map(n_clicks,district):
    uurl = "https://api.covid19india.org/state_district_wise.json"
    All_district = requests.get(uurl)
    data = All_district.json()
    Any_map = pd.DataFrame(data[district]['districtData'])
    Any_map = Any_map.T
    Any_map.drop('delta',axis=1,inplace=True)
    Any_map.reset_index(inplace=True)
    Any_map.rename(columns={'index':'District'},inplace=True)


    geojson = 'https://raw.githubusercontent.com/geohacker/india/master/district/india_district.geojson'
    fig = px.choropleth(Any_map, geojson=geojson,color='District',
                        locations="District", featureidkey="properties.NAME_2",
                        projection="mercator",hover_data=["active","confirmed", "deceased", "recovered"]
                       )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":50})
    return fig

if __name__ == '__main__':
    app.run_server()
