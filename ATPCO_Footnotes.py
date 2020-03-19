import base64
import ast
import io
from datetime import datetime
import pandas as pd
import time
import math
import requests
import os
from zipfile import ZipFile


from dateutil.parser import isoparse

#Dash Imports
import dash
#import dash_daq as daq
import dash_table
from dash.exceptions import PreventUpdate
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

#import webbrowser
#webbrowser.open('http://127.0.0.1:8050/', new=0)

# -----------------------------------------------------------------------------

#Username Pull based on Machine
userhome = os.path.expanduser('~')
PPR = os.getenv('username')

VALID_USERNAME_PASSWORD_PAIRS = {
    'XDL1SEM': 'secretpassword'
}

app = dash.Dash(__name__)
app.title = 'Delta Footnote Submission Tool'
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

#Get Airport List
airports = pd.read_csv('https://raw.githubusercontent.com/jsemrau3/gpd/master/airports.txt')
airports_dict = airports.to_dict(orient='records')

#Record 2 Blank File
df_headers = pd.DataFrame(columns = ['REC TYPE', 'FNT TYPE', 'FARE TARIFF #', 'FARE TARIFF #.1',
       'FARE TARIFF #.2', 'CARRIER CODE', 'CARRIER CODE.1', 'CARRIER CODE.2',
       'FOOTNOTE', 'FOOTNOTE.1', 'FOOTNOTE.2', 'CATEGORY #', 'CATEGORY #.1',
       'CATEGORY #.2', 'BLANK (FOR FUTURE USE)', 'BLANK (FOR FUTURE USE).1',
       'BLANK (FOR FUTURE USE).2', 'BLANK (FOR FUTURE USE).3',
       'BLANK (FOR FUTURE USE).4', 'BLANK (FOR FUTURE USE).5',
       'BLANK (FOR FUTURE USE).6', 'BLANK (FOR FUTURE USE).7', 'SEQUENCE #',
       'SEQUENCE #.1', 'SEQUENCE #.2', 'SEQUENCE #.3', 'SEQUENCE #.4',
       'SEQUENCE #.5', 'SEQUENCE #.6', 'TYPE', 'COUNTRY/CITY',
       'COUNTRY/CITY.1', 'CITY', 'BLANK (FOR FUTURE USE).8',
       'BLANK (FOR FUTURE USE).9', 'BLANK (FOR FUTURE USE).10',
       'BLANK (FOR FUTURE USE).11', 'TYPE.1', 'COUNTRY/CITY.2',
       'COUNTRY/CITY.3', 'CITY.1', 'BLANK (FOR FUTURE USE).12',
       'BLANK (FOR FUTURE USE).13', 'FARE CLASS', 'FARE CLASS.1',
       'FARE CLASS.2', 'FARE CLASS.3', 'FARE CLASS.4', 'FARE CLASS.5',
       'FARE CLASS.6', 'FARE CLASS.7', 'OW/RT', 'Routing #', 'Routing #.1',
       'Routing #.2', 'Routing #.3', 'Routing #.4', 'Effective Date (0YYMMDD)',
       'Effective Date (0YYMMDD).1', 'Effective Date (0YYMMDD).2',
       'Effective Date (0YYMMDD).3', 'Effective Date (0YYMMDD).4',
       'Effective Date (0YYMMDD).5', 'Effective Date (0YYMMDD).6',
       'Discontinued Date (0YYMMDD)', 'Discontinued Date (0YYMMDD).1',
       'Discontinued Date (0YYMMDD).2', 'Discontinued Date (0YYMMDD).3',
       'Discontinued Date (0YYMMDD).4', 'Discontinued Date (0YYMMDD).5',
       'Discontinued Date (0YYMMDD).6', 'BLANK (FOR FUTURE USE).14',
       'BLANK (FOR FUTURE USE).15', 'BLANK (FOR FUTURE USE).16',
       'BLANK (FOR FUTURE USE).17', 'BLANK (FOR FUTURE USE).18',
       'BLANK (FOR FUTURE USE).19', 'BLANK (FOR FUTURE USE).20',
       'NOT APPLC. (X or Blank)', '# SEGS', '# SEGS.1', '# SEGS.2',
       'Relational Indicator', 'Category #', 'Category #.1', 'Category #.2',
       'Table #', 'Table #.1', 'Table #.2', 'Table #.3', 'Table #.4',
       'Table #.5', 'Table #.6', 'Table #.7', 'Inbound-Outbound Indic.',
       'Direct. Indic.'])

# Copy and Empty the Headers Dataframe 
# df_info will be used to store the standard header information
# (NOTE: This is done to ensure the Dataframe is empty when it is rerun)
df_info = df_headers.iloc[0:0]

# Copy and Empty the Headers Dataframe 
# df_body will be used to store all the information that users input
# (NOTE: This is done to ensure the Dataframe is empty when it is rerun)
df_body = df_headers.iloc[0:0]

# Carriers
carriers = [{'label':'Delta', 'value':'DL'}, {'label':'Aeromexico', 'value':'AM'}, {'label':'KLM', 'value':'KL'}, {'label':'Air France', 'value':'AF'}]

# Tariff Dictionaries
df_TariffData = pd.read_csv('https://raw.githubusercontent.com/jsemrau3/gpd/master/tariff_data.txt', index_col=0)

publicDom = ast.literal_eval(df_TariffData.Domestic.Public)
privateDom = ast.literal_eval(df_TariffData.Domestic.Private)

df_public = pd.DataFrame.from_dict(publicDom)
df_private = pd.DataFrame.from_dict(privateDom)

allTariffs = []
unpublishedTariffs = []

for i,j in zip(list(df_public),list(df_private)):
    a = i + "/" + j
    allTariffs.append(a)

for i in list(df_private):
    unpublishedTariffs.append(i)

#public_keys = dict(df_public.loc['descr',:])
#private_keys = dict(df_private.loc['descr',:])
    
app.layout = html.Div([
        #Top Bar                      
        html.Div([
                # Image - 16.66
                html.Div(html.Img(src="http://prcp2.delta.com:17063/iris/images/delta_airlines_logo_trans_white_350x40.png", className= "w3-image w3-center"), className = "s2 w3-col", style = {'padding-block-start':'2.55%', 'padding-inline-start':'1%', 'padding-inline-end':'0.5%'}),
                # Text - Stacked & Centered - 83.33
                html.Div([
                        html.H1('Footnote Submission', className = "w3-xxxlarge w3-header"),
                        html.H3("Welcome to the Delta Footnote Submission Tool", className = "w3-header")
                        ], className = "s10 w3-col"
                    )
                ]
            ),

        #Middle Container
        html.Div([
                #Left
                html.Div([
                        dbc.FormGroup([
                                html.H3("ATPCO ID", style = {'color':'#FFFFFF'}),
                                dbc.Input(
                                        placeholder='XXX1XXX...',
                                        type='text',
                                        value='',
                                        id = 'user-input',
                                        pattern = u"^([A-Z]{,3}+[0-1]{,1}+[A-Z]{,3})$",
                                        debounce = True,
                                        valid=False,
                                        maxLength=7,
                                        minLength=7,
                                        style = {'width': '90%'}
                                    ),
                                html.Br(),
#                                dbc.FormText(
#                                        "Please enter a 7-Digit ATPCO ID", color="secondary"
#                                    )
                                ],className = "s12 w3-col", style = {'padding-inline-start':'5%', 'padding-top':'10%', 'padding-inline-end':'5%'}
                            ),

                        ], className = "w3-sidebar w3-delta-blue", style = {'width': '16.66%'}
                    ),
                #Main Container
                html.Div([            
                    #Second Layer of Formatting on Main Container
                    html.Div([
                        #Break
                        html.Br(),
                        
                        # Top Input Container - Work in Progress
                        html.Div([
                                # Header
                                html.Div([
                                    html.Div(
                                            html.H3("INPUTS", 
                                                    style={'padding-top': "8px", 'padding-bottom': "8px", "paddingLeft":"16px", "margin":"0px"}
                                                ), 
                                            className = "w3-left-align w3-delta-red",
                                        ),
                                        ], className = "w3-container w3-card",style = {"padding":"0px"}
                                    ),
                                # Main Body
                                html.Div([
                                        # Left - 16.66%
                                        html.Div([
                                                html.Div([
                                                        # Publication Type
                                                        html.H3('Publication', style = {'text-decoration': 'underline'}),
                                                        dcc.RadioItems(
                                                            id = 'publication',
                                                            options=[
                                                                {'label': 'Public & Private', 'value': 'Public/Private'},
                                                                {'label': 'Private Only', 'value': 'Private'}],
                                                            style = {"paddingLeft":"16px"},
                                                            value = "Public/Private"
                                                            ),
                                                        
                                                        
                                                        ],
                                                    ),
                                                html.Br(),
                                                html.Div([
                                                        # Type of Submission
                                                        html.H3('Type', style = {'text-decoration': 'underline'}),
                                                        dcc.RadioItems(
                                                            options=[
                                                                {'label': 'New', 'value': 'New'},
                                                                {'label': 'Change', 'value': 'Change'},
                                                                {'label': 'Delete', 'value': 'Delete'}],
                                                            style = {"paddingLeft":"16px"},
                                                            value = "New"
                                                            ),
                                                        ]
                                                    ),
                                                ], className = "l2 w3-col"
                                            ),
                                        # Middle - 83.33%
                                        html.Div([
                                                # Top Row - 33.33 - 33.33 - 33.33
                                                html.Div([
                                                        # Carrier
                                                        html.Div([
                                                                html.H3('Carrier', style = {'text-decoration': 'underline'}),
                                                                dcc.Dropdown(
                                                                    id = 'carrier-dropdown',
        #                                                            disabled = True,
                                                                    style = {'padding-left': '8px'},
                                                                    options = carriers,
                                                                    placeholder="Select a Carrier...",
                                                                    )
                                                                ], className = "s4 w3-col"
                                                            ),
                                                        # Tariff
                                                        html.Div([
                                                                html.H3('Tariff', style = {'text-decoration': 'underline'}),
                                                                dcc.Dropdown(
                                                                    id = 'tariff-dropdown',
                                                                    options=[{'label': l, 'value': v} for v,l in dict(df_private.loc['descr',:]).items()],
                                                                    value = list(privateDom.keys())[0],
                                                                    placeholder="Select a Tariff...",
        #                                                            disabled = True,
                                                                    style = {'padding-left': '8px'},
                                                                    
                                                                    )
                                                                ], className = "s4 w3-col"
                                                            ),
                                                        # Footnote
                                                        html.Div([
                                                                html.H3('Footnote', style = {'text-decoration': 'underline'}),
                                                                dcc.Dropdown(
                                                                    id = 'footnote-dropdown',
        #                                                            disabled = True,
                                                                    style = {'padding-left': '8px'},
                                                                    placeholder="Select a Footnote...",
                                                                    
                                                                    )
                                                                ], className = "s4 w3-col"
                                                            )
                                                        ]
                                                    ),
                                                # Loc Row - 41.66 - (3.33)10(3.33) - 41.66
                                                html.Div([
                                                        # Loc 1
                                                        html.Div([
                                                                html.H3('LOC 1', style = {'text-decoration': 'underline'}),
                                                                dcc.Dropdown(
                                                                    id = 'loc1-dropdown',
        #                                                            disabled = True,
                                                                    )
                                                                ], className = "s5 w3-col"
                                                            ),
                                                        # Direction
                                                        html.Div([
                                                                html.H3('Direction', style = {'color': '#fff'}),
                                                                dcc.Dropdown(
                                                                    id = 'directional-dropdown',
        #                                                            disabled = True,
                                                                    options = [
                                                                            {'label': '\u21C0', 'value': '1'},
                                                                            {'label': '\u21BC', 'value': '2'},
                                                                            {'label': '\u21D2', 'value': '3'},
                                                                            {'label': '\u21D0', 'value': '4'},
                                                                            {'label': 'N/A', 'value': ' '},
                                                                        ],
                                                                    value = ' ',
                                                                    style = {'margin': 'auto', 'width':'90%', 'padding-left':'5%', 'padding-right':'5%'}
                                                                    )
                                                                ], className = "s2 w3-col"
                                                            ),
                                                        # Loc 2
                                                        html.Div([
                                                                html.H3('LOC 2', style = {'text-decoration': 'underline'}),
                                                                dcc.Dropdown(
                                                                    id = 'loc2-dropdown',
        #                                                            disabled = True,
                                                                    )
                                                                ], className = "s5 w3-col" 
                                                            ),
                                                        ]
                                                    ),
                                                # Date Row - 26.66 - 26.66 - 26.66 - 20                
                                                html.Div([
                                                        # Commence
                                                        html.Div([
                                                                html.H3('Commence', style = {'text-decoration': 'underline'}),
                                                                dcc.DatePickerSingle(
                                                                        id = 'commence-date',
                                                                        style = {'padding-left': '8px'},
                                                                        className = "s11 w3-col",
                                                                        )
                                                                ], className = "s3b w3-col" 
                                                            ),
                                                        html.Div([
                                                                html.H3('Return', style = {'text-decoration': 'underline'}),
                                                                dcc.DatePickerSingle(
                                                                        id = 'return-date',
                                                                        style = {'padding-left': '8px'},
                                                                        className = "s11 w3-col",
                                                                        )
                                                                ], className = "s3b w3-col" 
                                                            ),
                                                        html.Div([
                                                                html.H3('Last Ticket Date', style = {'text-decoration': 'underline'}),
                                                                dcc.DatePickerSingle(
                                                                        id = 'last-ticket-date',
                                                                        style = {'padding-left': '8px'},
                                                                        className = "s11 w3-col",
                                                                        )
                                                                ], className = "s3b w3-col" 
                                                            ),
                                                        html.Div([
                                                                html.H3('Time', style = {'text-decoration': 'underline'}),
                                                                dbc.Input(
                                                                        placeholder='HHMM...',
                                                                        type='text',
                                                                        value='0000',
                                                                        id = 'time-input',
                                                                        pattern = u"^([0-24]{,2}+[0-59]{,2})$",
                                                                        debounce = True,
                                                                        valid=False,
                                                                        maxLength=4,
                                                                        minLength=4,
                                                                        className = "s11 w3-col",
                                                                    ) 
                                                                ], className = "s2b w3-col" 
                                                            )
                                                        ]
                                                    ),
                                                ], className = "s10 w3-col"
                                            ),
                                        ], className = "w3-container w3-card w3-padding-16"
                                    ),
                                
                                # Adding Entry Button
                                html.Div([
                                        html.Button('Add to Submission', id='add-entry-button', className = "btn-secondary", style = {'float':'right'}),
#                                        dbc.Modal(
#                                                [
#                                                    dbc.ModalHeader("WARNING"),
#                                                    dbc.ModalBody("Please complete additional fields to proceed."),
#                                                    dbc.ModalFooter(
#                                                        dbc.Button(
#                                                            "Close", id="trigger-dismiss-button", className="ml-auto"
#                                                        )
#                                                    ),
#                                                ],
#                                                id="input-warning",
#                                                centered=True,
#                                            ),
                                        ], className = "w3-container w3-padding-16"
                                    ),
                                
                                ], className = "w3-container"
                            ),
                        # End of of Top Input Container
                        
                        #Break
                        html.Br(),
        
                        #Break                    
                        html.Br(),
                        
                        #Travel Restrictions Table
                        html.Div([
                                html.Div([
                                    html.H3("PREVIEW", 
                                            className = "l6 w3-col w3-left-align", style={'padding-top': "8px", 'padding-bottom': "8px", "paddingLeft":"16px", "margin":"0px"}), 
                                    ], className = "w3-container w3-delta-red",style = {"padding":"0px", "color":"#FFF"}
                                    ),
                                    
                                    
#                                    html.Div([
                                            dash_table.DataTable(
                                                id='input-table',
                                                columns=[{'id':'Carrier','name':['','Carrier'], 'presentation':'dropdown'},
                                                        {'id':'PUvU_Selection','name':['','Publication'], 'presentation':'dropdown'},
                                                        {'id':'Tariff','name':['','Tariff'], 'presentation':'dropdown'},
                                                        {'id':'Footnote','name':['','Footnote'], 'presentation':'dropdown'},
                                                        {'id':'LOC1','name':['','LOC1'], 'presentation':'dropdown'},
                                                        {'id':'Direction','name':['','Direction'], 'presentation':'dropdown'},
                                                        {'id':'LOC2','name':['','LOC2'], 'presentation':'dropdown'},
                                                        {'id':'Commence_Date','name':['Dates (YYYY-MM-DD)','Commence'], 'type': 'datetime'},
                                                        {'id':'Return_Date','name':['Dates (YYYY-MM-DD)','Return By'], 'type': 'datetime'},
                                                        {'id':'LastTicket_Date','name':['Dates (YYYY-MM-DD)','Last Ticket'], 'type': 'datetime'},
                                                        {'id':'Time','name':['HHMM (24 Hour)','Time']}
                                                    ],
                                                merge_duplicate_headers=True,
                                                data = [],
                                                editable=True,
                                                style_cell = {
                                                        'overflow': 'hidden',
                                                        'textOverflow': 'clip',
                                                        'textAlign':'center',
                                                        'font-size': 'smaller',
                                                        'font-family': '"Material-Design-Icons",Arial,sans-serif',
                                                    },
                                                style_header={
                                                        'fontWeight': 'bold',
                                                    },
                                                style_data_conditional=[
                                                        {
                                                            'if': {'row_index': 'odd'},
                                                            'backgroundColor': 'rgb(248,248,248)'
                                                        }
                                                    ],
                                                style_cell_conditional=[
                                                    {'if': {'column_id': 'Carrier'},
                                                     'width': '12%'},
                                                    {'if': {'column_id': 'PUvU_Selection'},
                                                     'width': '16%'},
                                                    {'if': {'column_id': 'Tariff'},
                                                     'width': '10%'},
                                                    {'if': {'column_id': 'Footnote'},
                                                     'width': '10%'},
                                                    {'if': {'column_id': 'LOC1'},
                                                     'width': '7%'},
                                                    {'if': {'column_id': 'Direction'},
                                                     'width': '8%'},
                                                    {'if': {'column_id': 'LOC2'},
                                                     'width': '7%'},
                                                    {'if': {'column_id': 'Commence_Date'},
                                                     'width': '8%'},
                                                    {'if': {'column_id': 'Return_Date'},
                                                     'width': '8%'},
                                                    {'if': {'column_id': 'LastTicket_Date'},
                                                     'width': '8%'},
                                                    {'if': {'column_id': 'Time'},
                                                     'width': '6%'},
                                                    
                                                    ],
                                                style_table={
                                                        'maxWidth': '100%',
                                                        'border': 'thin lightgrey solid',
                                                        'accent': 'slateblue',
                                                        'selected-background': 'rgb(125,155,193,0.2)'
                                                        
                                                    },
                                                row_deletable=True,
                                                fill_width = False,
                                                css=[
                                                        {"selector": ".column-header--delete svg", "rule": 'display: "none"'},
                                                        {"selector": ".column-header--delete::before", "rule": 'content: "X"'}
                                                    ],
                                                dropdown = {
                                                        'Carrier': {
                                                            'options': carriers
                                                            },
                                                        'PUvU_Selection': {
                                                            'options': [
                                                                {'label': 'Public/Private', 'value': 'Public/Private'},
                                                                {'label': 'Private', 'value': 'Private'},
                                                                ]
                                                            },
                                                        'LOC1': {
                                                            'options': [
                                                                {'label': v, 'value': v}
                                                                for v in airports['value']
                                                                ]
                                                            },
                                                        'Direction': {
                                                            'options': [
                                                                {'label': '\u21C0', 'value': '1'},
                                                                {'label': '\u21BC', 'value': '2'},
                                                                {'label': '\u21D2', 'value': '3'},
                                                                {'label': '\u21D0', 'value': '4'},
                                                                {'label': 'N/A', 'value': ' '},
                                                                ]
                                                            },
                                                        'LOC2': {
                                                            'options': [
                                                                {'label': v, 'value': v}
                                                                for v in airports['value']
                                                                ]
                                                            },
                                                    },
                                                dropdown_conditional = [
                                                        {'if': {
                                                                'column_id': 'Tariff',
                                                                'filter_query': '{PUvU_Selection} eq "Public/Private"'
                                                            },
                                                        'options': [
                                                                {'label': p, 'value': p} for p in allTariffs
                                                            ]
                                                            },
                                                        
                                                        {'if': {
                                                                'column_id': 'Tariff',
                                                                'filter_query': '{PUvU_Selection} eq "Private"'
                                                            },
                                                        'options': [
                                                                {'label': p, 'value': p} for p in unpublishedTariffs
                                                            ]
                                                            },
                                                        
                                                        {'if': {
                                                                'column_id': 'Footnote',
                                                                'filter_query': '{Tariff} eq "DLUS" or {Tariff} eq "PF17/DLUS"'
                                                            },
                                                        'options': [
                                                                {'label': p, 'value': p} for p in df_private['DLUS']['allowed_vals']
                                                            ]
                                                            },
                                                        
                                                        {'if': {
                                                                'column_id': 'Footnote',
                                                                'filter_query': '{Tariff} eq "DLAH" or {Tariff} eq "DLEC" or {Tariff} eq "DLVPC" or {Tariff} eq "DLTBC" or {Tariff} eq "OF1/DLAH" or {Tariff} eq "EF2/DLEC" or {Tariff} eq "VPD/DLVPC" or {Tariff} eq "DLTBC"'
                                                            },
                                                        'options': [
                                                                {'label': p, 'value': p} for p in df_private['DLAH']['allowed_vals']
                                                            ]
                                                            },
                                                    ]
                                                ),
                                            html.Br(),
                                            html.Div([
                                                    html.Div(dcc.ConfirmDialogProvider(
                                                                    id = "confirm",
                                                                    children = html.Button('Upload', id='submit-button', className = "btn-success"),
                                                                    message = "Before you continue, please confirm all information is correct?"
                                                                ), className = "w3-right", style = {'padding-bottom':'16px!important'}
                                                        )
                                                    ], className = "w3-container w3-padding-16"
                                                ),
                                            html.Br()
                                            
#                                        ], id = 'travel-alt-inner-container', className = "w3-container w3-card", style = {'padding-bottom':'16px!important','padding-top':'0px!important','padding-left':'0px!important','padding-right':'0px!important'})
                            ], id = 'travel-alt-outer-container', className = "w3-container"
                            ),
                        #Break
                        html.Br(),
                            
                        html.Div([
                                #Upload Field goes here
                                dcc.Upload(
                                        id='upload-data',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select Files')
                                        ]),
                                        style={
                                            'height': '60px',
                                            'lineHeight': '60px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center',
                                            'margin': '10px',
                                            'box-sizing': 'content-box'
                                        },
                                        # Allow multiple files to be uploaded
                                        multiple=True
                                    ),
                                ], className = "w3-container"
                            ),
                        html.Br(),                        
                            ]
                        )
                        ], className = "w3-main w3-white", style = {'margin-left':'16.66%'}
                    ), #Main Container Ends
            ], className = "w3-container", style = {'padding':'0'}
        ), 
            #Middle Content
                                
        html.Div(id="output", style={'display':'none'})
    ], className = "w3-delta-blue"
)

#Helper Functions
# Read an upload file
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df_upload = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df_upload = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
#    data =                                
    return df_upload.to_dict('records') 

# Travel Restriction Function
def cat14Tbl(UserID, CommAftDt, CommBefDt, RtnDt, loc1, loc2, tsi):
    #Function includes request as well as header and payload to obtain token automatically. Each call generates a new token.
    #Header to pass into request. Ensure Content Type is set to FORM_URLENCODED (Dictated by ATPCO)
    #hdr_4tkn = {
    #       "Content-type": "FORM_URLENCODED"
    #     }
    #Payload information provided by ATPCO. Client ID and Secret are standard across Delta Air Lines organization
    payload_4tkn = {
            "client_id" : "d0314db0-9470-4b94-b754-b9b95aa411f7",
            "client_secret": "4c11f753-384a-4583-bab6-bc71a3a72b0d",
            "grant_type": "client_credentials",
        }
    authorization_url = "https://developer.atpco.net/api/oauth/token"
    #Post Request to generate and return token
    keyInfo = requests.post(authorization_url, data = payload_4tkn)
    
    #Extract the token from the json response. ATPCO formating dictates that the Authorization string includes the preamble "Bearer "
    key = keyInfo.json()
    token = key['access_token']
    
    #Travel Restriction (CAT 14) Footnote API
    trvl_url = "https://developer.atpco.net/services/gtst/v1/footnotes/record3/cat14/travelrestrictions"
    
    Authorization = "Bearer "+ token
    

    tvlDtCommParam = 'C'
#    loc1 = ''
#    loc2 = ''
    if not tsi==" ":
        tsi = '0' + tsi
    else:
        tsi = ""
    
    #Header to into table return request. Authorization is generated by previous request. UserID is input for record keeping. 
    #(**NOTE: ATPCO DOES TAKE USERID INTO CONSIDERATION FROM A SECURITY STANDPOINT)
    hdr = {
    
            "Content-type": "application/json",
            "Authorization": Authorization,
            "userId": UserID,
        }
    #Payload information to pass as inputs to return/create matching table number
    payload = {
            "tvlRstrxn14": {
                        **({"tvlDtComm": CommAftDt} if CommAftDt else {}),
                        **({"tvlDtExp": CommBefDt} if CommBefDt else {}),
                        **({"tvlDtCommComp": RtnDt} if RtnDt else {}),
                        **({"tvlDtAppl": tvlDtCommParam} if RtnDt else {}),
                        **({"tvlDtTm": "2400"} if RtnDt else {}),
                        **({"geoSpec995": {
                            **({"type": "P"} if loc1 or loc2 else {}),
                            **({"loc1": loc1} if loc1 else {}),
                            **({"loc2": loc2} if loc2 else {}),
                            **({"tsi": tsi} if tsi else {})
                        }} if loc1 or loc2 or tsi else {}),
            }
        }
    print(payload)
    #Pass Parameters into POST Request to the Applicable API
    response = ''
    while response == '':
        try:
            response = requests.post(trvl_url, json=payload, headers = hdr)
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
#     response = requests.post(trvl_url, json=payload, headers = hdr)
    response = response.json()
    print(response)
    msgCheck = response.get("msg", "")
    print(msgCheck)
    if msgCheck =="":
        tblNum = response['tvlRstrxn14']['tblNum']
    elif msgCheck:
        tblNum = None
    response = ''
    return tblNum
    #Need to potentially build in additional error handling
    #If 'Table Creation was Unsuccessful Due to Input, should it 
    # A) Ignore this entry 
    # B) Retry and then Ignore 
    # C) Notify the User somehow? Generate a report of which entries successfully produced a table number && uploaded or just which returned a table number

#Sales Restriction Function
def cat15Tbl(UserID, LstTcktDt):
    #Function includes request as well as header and payload to obtain token automatically. Each call generates a new token.
    #Header to pass into request. Ensure Content Type is set to FORM_URLENCODED (Dictated by ATPCO)
    #hdr_4tkn = {
    #       "Content-type": "FORM_URLENCODED"
    #     }
    #Payload information provided by ATPCO. Client ID and Secret are standard across Delta Air Lines organization
    payload_4tkn = {
            "client_id" : "d0314db0-9470-4b94-b754-b9b95aa411f7",
            "client_secret": "4c11f753-384a-4583-bab6-bc71a3a72b0d",
            "grant_type": "client_credentials",
        }
    authorization_url = "https://developer.atpco.net/api/oauth/token"
    #Post Request to generate and return token
    keyInfo = requests.post(authorization_url, data = payload_4tkn)
    
    #Extract the token from the json response. ATPCO formating dictates that the Authorization string includes the preamble "Bearer "
    key = keyInfo.json()
    token = key['access_token']
    
    #Travel Restriction (CAT 14) Footnote API
    sale_url = "https://developer.atpco.net/services/gtst/v1/footnotes/record3/cat15/salesrestriction"
    
    Authorization = "Bearer "+ token
    
    #Header to into table return request. Authorization is generated by previous request. UserID is input for record keeping. 
    #(**NOTE: ATPCO DOES TAKE USERID INTO CONSIDERATION FROM A SECURITY STANDPOINT)
    hdr = {
    
            "Content-type": "application/json",
            "Authorization": Authorization,
            "userId": UserID,
        }
    #Payload information to pass as inputs to return/create matching table number
    payload = {
            "salesRstrxn15": {
                        **({"tktDisc": LstTcktDt} if LstTcktDt else {})
            }
        }
    print(payload)
    #Pass Parameters into POST Request to the Applicable API
    response = ''
    while response == '':
        try:
            response = requests.post(sale_url, json=payload, headers = hdr)
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
    #response = requests.post(trvl_url, json=payload, headers = hdr)
    response = response.json()
    print(response)
    msgCheck = response.get("msg", "")
    print(msgCheck)
    if msgCheck =="":
        tblNum = response['salesRstrxn15']['tblNum']
    elif msgCheck:
        tblNum = None
    response = ''
    return tblNum
    #Need to potentially build in additional error handling
    #If 'Table Creation was Unsuccessful Due to Input, should it 
    # A) Ignore this entry 
    # B) Retry and then Ignore 
    # C) Notify the User somehow? Generate a report of which entries successfully produced a table number && uploaded or just which returned a table number

#Counting Function
def countNums(n):
    if n > 0:
        digits = int(math.log10(n))+1
    elif n == 0:
        digits = 1
    else:
        digits = int(math.log10(-n))+2
    return digits

@app.callback(
        Output('output', 'style'), 
        [Input('confirm', 'submit_n_clicks'),
         Input('input-table', 'derived_virtual_data'),
         Input('user-input', 'value')],
        [State('input-table', 'derived_virtual_data')]
)
def download_file(submit_n_clicks, data1, userID, data):
    if submit_n_clicks is None:
        raise PreventUpdate
    else:
        dff = pd.DataFrame.from_dict(data)
        
        for i, data in dff.iterrows():
            if data.Commence_Date:
                data.Commence_Date = isoparse(data.Commence_Date)
            else:
                data.Commence_Date = ""
        
        for i, data in dff.iterrows():
            if data.Return_Date:
                data.Return_Date = isoparse(data.Return_Date)
            else:
                data.Return_Date = ""
        
        for i, data in dff.iterrows():
            if data.LastTicket_Date:
                data.LastTicket_Date = isoparse(data.LastTicket_Date)
            else:
                data.Disc_Date = ""
        
        dff['Commence_Rcd2'] = ''
        dff['Commence_API'] = ''
        dff['Return_Rcd2'] = ''
        dff['Return_API'] = ''
        dff['LastTicket_Rcd2'] = ''
        dff['LastTicket_API'] = ''
        
        #Looping through extra columns and formatting accordingly
        for k in dff['Commence_Date']:
            dff['Commence_Rcd2'][dff['Commence_Date']==k] = "" if k =="" else k.strftime("0%y%m%d"),
            dff['Commence_API'][dff['Commence_Date']==k] = "" if k =="" else k.strftime("%Y%m%d")
        
        for k in dff['Return_Date']:
            dff['Return_Rcd2'][dff['Return_Date']==k] = "" if k =="" else k.strftime("0%y%m%d")
            dff['Return_API'][dff['Return_Date']==k] = "" if k =="" else k.strftime("%Y%m%d")
        
        for k in dff['LastTicket_Date']:
            dff['LastTicket_Rcd2'][dff['LastTicket_Date']==k] = "" if k =="" else k.strftime("0%y%m%d")
            dff['LastTicket_API'][dff['LastTicket_Date']==k] = "" if k =="" else k.strftime("%Y%m%d")
        
        for k in dff['Time']:
            dff['Time'] = "" if k =="" else time.strftime("%I%M", time.strptime(k, '%H%M'))
            
        #Travel Restriction and Sales Restriction API Calls. Add additional columns and API functions here
        # Append Empty Columns for CAT14 and CAT15 Table Numbers
        dff['TableNumber_CAT14'] = ""
        dff['TableNumber_CAT15'] = ""
        dff['Sequence_Number'] = ""
        
        for i,d in dff.iterrows():
            #Iterate over the rows of the CAT14 Column and fill with Table Numbers using the applicable function. NOTE: The function currently has not been fed the "Commence Before/On" date
            #as this is currently disabled within the input table. It can be enabled by adding the corresponding input field within the input table and referencing it as an input for the function.
            dff.iloc[i]['TableNumber_CAT14'] = cat14Tbl(userID, d.Commence_API, "", d.Return_API, d.LOC1, d.LOC2, d.Direction)
            #Iterate over the rows of the CAT15 Column and fill with Table Numbers using the applicable function.
            dff.iloc[i]['TableNumber_CAT15'] = cat15Tbl(userID, d.LastTicket_API)
            #Hard coded time gap between for loops to prevent errors. Execution has shown to still work at down to 0.1 seconds.
            time.sleep(0.1)
        
        #Add Leading Zeroes for the Table Numbers if the number of digits is less than 8.
        dff.loc[(dff.TableNumber_CAT14.str.len() == 7),'TableNumber_CAT14'] = "0" + dff.loc[(dff.TableNumber_CAT14.str.len() == 7),'TableNumber_CAT14']
        dff.loc[(dff.TableNumber_CAT15.str.len() == 7),'TableNumber_CAT15'] = "0" + dff.loc[(dff.TableNumber_CAT15.str.len() == 7),'TableNumber_CAT15']
        
        for i,data in dff.iterrows():
            data.Footnote = " "*(2-len(data.Footnote)) + data.Footnote + " "
            data.Carrier = data.Carrier + " "*(3-len(data.Carrier))
            # Sequence Number Rnaking 
            data.Sequence_Number = 0
            # First, assign sequence number based on Commence and Return Dates
            if data.Commence_Date and data.Return_Date:
                data.Sequence_Number = 25000
            elif data.Commence_Date:
                data.Sequence_Number = 40000 
            elif data.Return_Date:
                data.Sequence_Number = 50000
            else:
                data.Sequence_Number = 1000000
            # Second, assign sequence number based on LOC1 and LOC2
            if data.LOC1 and data.LOC2:
                data.Sequence_Number = data.Sequence_Number - 15000
            elif data.LOC1:
                data.Sequence_Number = data.Sequence_Number - 10000
            elif data.LOC2:
                data.Sequence_Number = data.Sequence_Number - 5000
            elif data.Sequence_Number == 1000000:
                data.Sequence_Number = data.Sequence_Number + 1000000
            # Third, include directionality
            if data.Direction:
                data.Sequence_Number = data.Sequence_Number - 5000
            # Check if the sequence number is already listed and increase until it does not match current records (May need to be rewritten if a certain ordering scenario is hit, i.e. two high priority sequences followed by a lower priority occupying a certain sequence number)
            for k in dff.Sequence_Number:
                if data.Sequence_Number == k:
                    data.Sequence_Number = data.Sequence_Number + 5000
#            while data.Sequence_Number in dff.Sequence_Number:
#                data.Sequence_Number = data.Sequence_Number + 5000
        
        for i,data in dff.iterrows():
            data.Sequence_Number = "0"*(7-countNums(data.Sequence_Number)) + str(data.Sequence_Number)
        
        #Build DataFrame 2 out with all correctly formatted data for the Record 2 Upload File
        #Iterate over Dataframe 3 one row at a time. Each row and row index is grabbed and then data is extracted if correctly formatted
        for index,row in dff.iterrows():
            #Create reference variables to make formatting easier
            z = "0"
            b = " "
            
            if row['TableNumber_CAT14'] or row['TableNumber_CAT15']:
                #Pull Tariff Variable from the Row
                tariff = row['Tariff']
                
                #Create reference variables to make formatting easier
                z = "0"
                # Footnote Type
                Ftn_Type = " "
                
                #Determine whether this entry is 'Unpublished Only' or 'Published & Unpublished'
                if "/" in tariff:
                    #This occurs if it is both a Published and Unpublished submission. Both Tariff Values are extracted to be added into the upload file as separate entries
                    #Code Count = Value in the public Dictionary. The value represents the Tariff
                    #Tariff Codes need to be three digits. Therefore additional leading zeroes are added if necessary. Logic: Code = "0" * (3 - (number of digits for the Value of the applicable Tariff)) + the string of the actual value
                    publicTariffCodeCount = z * (3-countNums(publicDom[tariff[:tariff.find("/")]]['value'])) + str(publicDom[tariff[:tariff.find("/")]]['value'])
                    privateTariffCodeCount = z * (3-countNums(privateDom[tariff[tariff.find("/")+1:]]['value'])) + str(privateDom[tariff[tariff.find("/")+1:]]['value'])
                else:
                    #Here we only are producing the code for the Unpublished side. Logic Remains the same.
                    publicTariffCodeCount = None
                    privateTariffCodeCount = z * (3-countNums(privateDom[tariff]['value'])) + str(privateDom[tariff]['value'])
            print(row.Direction)
            #Create List to Append to Dataframe 
            l = [None for _ in range(96)]
            
            # Information on writing to the list: Python Lists can use indices. The indices were mapped out based on ATPCO Record 2 Documentation
            # See Link: https://customer.atpco.net/system/files/Data_Application/Footnotes%20Upload_Record2D_C.pdf
            
            #### Create and Append list for Travel Restrictions ####
            #Extract Inputs from dff Tied to a Travel Restriction (CAT 14)
            if row['TableNumber_CAT14']:
                CAT = "014"
                
                #Write to the list for Unpublished - CAT 14
                
                l[:22] = "2" + Ftn_Type + privateTariffCodeCount + row.Carrier + row.Footnote + CAT + "        "
                l[22:29] = row.Sequence_Number
                l[29:33] = "P" + row.LOC1 if row.LOC1 else "    "
                l[37:41] = "P" + row.LOC2 if row.LOC2 else "    "
                #Effective Date = Today (Domestic) or Tomorrow (International)
                #Discontinued Date = 0999999
                l[57:71] = datetime.today().strftime("0%y%m%d") + '0999999'
                l[83:86] = CAT
                l[86:94] = row.TableNumber_CAT14
                l[95:96] = row.Direction
                conv = lambda i : i or ' ' 
                [conv(i) for i in l] 
                print(l)
                # Append to List
                df_body.loc[len(df_body)] = l
                
                if publicTariffCodeCount:
                    #Write to the list for Published - CAT 14
                    l[:22] = "2" + Ftn_Type + publicTariffCodeCount + row.Carrier + row.Footnote + CAT + "        "
                    l[22:29] = row.Sequence_Number
                    l[29:33] = "P" + row.LOC1 if row.LOC1 else "    "
                    l[37:41] = "P" + row.LOC2 if row.LOC2 else "    "
                    l[57:71] = datetime.today().strftime("0%y%m%d") + '0999999'
                    l[83:86] = CAT
                    l[86:94] = row.TableNumber_CAT14
                    l[95:96] = row.Direction
                    conv = lambda i : i or ' ' 
                    [conv(i) for i in l] 
                    # Append to List
                    df_body.loc[len(df_body)] = l
                
            #### Create and Append list for Sales Restrictions ####
                
            #Extract Inputs from dff Tied to a Sales Restriction (CAT 15)
            if row['TableNumber_CAT15']:
#                CarrierCode = "0DL"
#                Footnote = row['Footnote']
                CAT = "015"
                
                # Write to the list for Unpublished - CAT 15
                l[:22] = "2" + Ftn_Type + privateTariffCodeCount + row.Carrier + row.Footnote + CAT + "        "
                l[22:29] = row.Sequence_Number
                l[29:33] = "P" + row.LOC1 if row.LOC1 else "    "
                l[37:41] = "P" + row.LOC2 if row.LOC2 else "    "
                l[57:71] = datetime.today().strftime("0%y%m%d") + '0999999'
                l[83:86] = CAT
                l[86:94] = row.TableNumber_CAT15
                l[95:96] = row.Direction
                conv = lambda i : i or ' ' 
                [conv(i) for i in l] 
                # Append to List
                df_body.loc[len(df_body)] = l
                
                
                if publicTariffCodeCount:
                    # Write to the list for Published - CAT 15
                    l[:22] = "2" + b + publicTariffCodeCount + row.Carrier + row.Footnote + CAT + "        "
                    l[22:29] = row.Sequence_Number
                    l[29:33] = "P" + row.LOC1 if row.LOC1 else "    "
                    l[37:41] = "P" + row.LOC2 if row.LOC2 else "    "
                    l[57:71] = datetime.today().strftime("0%y%m%d") + '0999999'
                    l[83:86] = CAT
                    l[86:94] = row.TableNumber_CAT15
                    l[95:96] = row.Direction
                    conv = lambda i : i or ' ' 
                    [conv(i) for i in l] 
                    # Append to List
                    df_body.loc[len(df_body)] = l
        
        # Remove Existing Text file if it already exists to prevent appending
        filepath = os.getcwd() + '\Footnote_Rcd2.txt'
        if os.path.exists(filepath):
            os.remove('Footnote_Rcd2.txt')
        
#        # Attach Header at the top
#        l = [None for _ in range(96)]
#        rowCt = z * (5-countNums(len(df_body.index)+3)) + str(len(df_body.index)+3)
#        a = "U DL" + "                 " + PPR + "N" + rowCt
#        l[:len(a)] = a
#        df_info.loc[len(df_info)] = l
#        # Line is used for emailing user based on PPR
#        l = [None for _ in range(96)]
#        a = "N " + PPR + "@DELTA.COM                                                               "
#        l[:len(a)] = a
#        df_info.loc[len(df_info)] = l
#        # Setting permissions and recording user
#        l = [None for _ in range(96)]
#        a = "W                " + PPR + "N               "
#        l[:len(a)] = a
#        df_info.loc[len(df_info)] = l

        a = "U DL" + "                 " + "332572" + "N" + "00003"
        b = "N " + "332572" + "@DELTA.COM                                                               "
        c = "W                " + "332572" + "N               "
        
        header = [a, b, c]

        with open('header.txt', 'w') as filehandle:
            for listitem in header:
                filehandle.write('%s\n' % listitem)
        
        # Sort Body by Carrier, Tariff, Footnote, and then Sequence
        df_body.sort_values(by=['CARRIER CODE','CARRIER CODE.1','CARRIER CODE.2','FARE TARIFF #', 'FARE TARIFF #.1','FARE TARIFF #.2', 'FOOTNOTE', 'FOOTNOTE.1', 'FOOTNOTE.2', 'SEQUENCE #', 'SEQUENCE #.1', 'SEQUENCE #.2' , 'SEQUENCE #.3', 'SEQUENCE #.4', 'SEQUENCE #.5', 'SEQUENCE #.6'])
        df_body.to_csv('body.txt', index=False, header=False)
        
        s = open("body.txt").read()
        s = s.replace(',,', '  ')
        f = open("body.txt", 'w')
        f.write(s)
        f.close()
        
        s = open("body.txt").read()
        s = s.replace(',', '')
        f = open("body.txt", 'w')
        f.write(s)
        f.close()
        
        filenames = ['header.txt', 'body.txt']
        with open('Footnote_Rcd2.txt', 'w') as outfile:
            for fname in filenames:
                with open(fname) as infile:
                    outfile.write(infile.read())
                        
        # Join the Information and Body dataframes together
#        df_upload_ready = pd.concat([df_info, df_body])                        
        
        # Convert the newly created dataframe to the Footnote_Rcd2 Upload File
#        df_upload_ready.to_csv('Footnote_Rcd2.txt', index=False, header=False)
#        s = open("Footnote_Rcd2.txt").read()
#        s = s.replace(',,', '  ')
#        f = open("Footnote_Rcd2.txt", 'w')
#        f.write(s)
#        f.close()
#        
#        s = open("Footnote_Rcd2.txt").read()
#        s = s.replace(',', '')
#        f = open("Footnote_Rcd2.txt", 'w')
#        f.write(s)
#        f.close()
        
        if os.path.exists('submission_log.csv'):
            dff.to_csv('submission_log.csv', mode='a', header=False, index=False)
        else:
            dff.to_csv('submission_log.csv', index=False)
        
        filepath = os.getcwd() + '\Footnote_Rcd2.zip'
        if os.path.exists(filepath):
            os.remove('Footnote_Rcd2.zip')
        
        # filepath = os.getcwd() + '\!XDL.GTST.XMTDLRCZ.PARCHNGS'
        # if path.exists(filepath):
        #     os.remove('!XDL.GTST.XMTDLRCZ.PARCHNGS')
            
        # create a ZipFile object
        zipObj = ZipFile('Footnote_Rcd2.zip', 'w')
         
        # Add multiple files to the zip
        zipObj.write('Footnote_Rcd2.txt')
        # zipObj.write('test_1.log')
        # zipObj.write('test_2.log')
         
        # close the Zip File
        zipObj.close()
        
        os.popen('"C:/Users/332572/OneDrive - Delta Air Lines/Projects/Footnotes_Automation/Testing/WinSCP/WinSCP.exe" XDL0FT2:X16a1dl@ftpin.atpco.net /console /script="C:/Users/332572/OneDrive - Delta Air Lines/Projects/Footnotes_Automation/atpcoTest.txt" /log="C:/Users/332572/OneDrive - Delta Air Lines/Projects/Footnotes_Automation/log.txt"')

#Travel Restrictions Table - Add Rows Functionality
#@app.callback(
#    Output('input-table', 'data'),
##    [Input('upload-data', 'contents'),Input('upload-data', 'filename'),
#     [Input('add-travel-restriction-button', 'n_clicks')],
#    [State('input-table', 'data'), State('input-table', 'columns')])
#def add_TravelRestr_row(n_clicks, rows, columns):
#    if n_clicks > 0:
#        rows.append({c['id']: '' for c in columns})
#    return rows

@app.callback(
        Output('input-table', 'data'),
        [Input('add-entry-button', 'n_clicks'),
         Input('carrier-dropdown', 'value'),
         Input('publication', 'value'),
         Input('tariff-dropdown', 'value'),
         Input('footnote-dropdown', 'value'),
         Input('loc1-dropdown', 'value'),
         Input('directional-dropdown', 'value'),
         Input('loc2-dropdown', 'value'),
         Input('commence-date', 'date'),
         Input('return-date', 'date'),
         Input('last-ticket-date', 'date'),
         Input('time-input', 'value'),],
         [State('input-table', 'data')]
        )
def add_Entry(n_clicks, carrier, publication, tariff, footnote, loc1, direc, loc2, commenceD, returnD, lastD, time, rows):
    if commenceD is not None:
        commenceD = datetime.strptime(commenceD.split(' ')[0], '%Y-%m-%d')
        commenceD_string = commenceD.strftime('%Y-%m-%d')
    else:
        commenceD_string = ""
    
    if returnD is not None:
        returnD = datetime.strptime(returnD.split(' ')[0], '%Y-%m-%d')
        returnD_string = returnD.strftime('%Y-%m-%d')
    else:
        returnD_string = ""
    
    if lastD is not None:
        lastD = datetime.strptime(lastD.split(' ')[0], '%Y-%m-%d')
        lastD_string = lastD.strftime('%Y-%m-%d')
    else:
        lastD_string = ""
    
    if n_clicks > 0:
        rows.append({'Carrier':carrier,
                   'PUvU_Selection':publication,
                   'Tariff':tariff,
                   'Footnote':footnote,
                   'LOC1':loc1,
                   'Direction':direc,
                   'LOC2':loc2,
                   'Commence_Date':commenceD_string,
                   'Return_Date':returnD_string,
                   'LastTicket_Date':lastD_string,
                   'Time':time})
    return rows
    

@app.callback(
        Output('tariff-dropdown','options'),
        [Input('publication', 'value')]
        )
def update_tariff_dropdown(publication):
    if publication == "Public/Private":
        return [{'label': p, 'value': p} for p in allTariffs]
    elif publication == "Private":
        return [{'label': p, 'value': p} for p in unpublishedTariffs]

@app.callback(
    Output('footnote-dropdown', 'options'),
    [Input('tariff-dropdown','value'),
     Input('publication', 'value')]
)

def update_footnote_dropdown(name,publication):
    if publication == "Public/Private":
        return [{'label': p, 'value': p} for p in df_private[name[name.find("/")+1:]]['allowed_vals']]
    elif publication == "Private":
        return [{'label': p, 'value': p} for p in df_private['DLAH']['allowed_vals']]
    

#Dynamic Dropdown Menues
@app.callback(
    Output("loc1-dropdown", "options"),
    [Input("loc1-dropdown", "search_value")],
)
def update_options(search_value):
    if not search_value:
        raise PreventUpdate
    return [o for o in airports_dict if search_value.lower() in o["label"].lower()]

#Dynamic Dropdown Menues
@app.callback(
    Output("loc2-dropdown", "options"),
    [Input("loc2-dropdown", "search_value")],
)
def update_options2(search_value):
    if not search_value:
        raise PreventUpdate
    return [o for o in airports_dict if search_value.lower() in o["label"].lower()]

#@app.callback(
#        Output("input-warning", "is_open"),
#        [Input("add-entry-button", "n_clicks"),
#         Input("trigger-dismiss-button", "n_clicks"),
#         Input('carrier-dropdown', 'value'),
#         Input('publication', 'value'),
#         Input('tariff-dropdown', 'value'),
#         Input('footnote-dropdown', 'value'),
#         Input('loc1-dropdown', 'value'),
#         Input('directional-dropdown', 'value'),
#         Input('loc2-dropdown', 'value'),
#         Input('commence-date', 'date'),
#         Input('return-date', 'date'),
#         Input('last-ticket-date', 'date'),
#         Input('time-input', 'value'),],
#        [State("input-warning", "is_open")]
#        )
#
#def trigger_warning(n1, n2, carrier, publication, tariff, footnote, loc1, direction, loc2, commenceD, returnD, lastD, time, is_open):
#    if n1 or n2 and carrier=='' and publication=='' and tariff=='' and footnote=='' or commenceD is None or returnD is None or lastD is None:
#        return not is_open
#    return is_open

if __name__ == '__main__':
    app.run_server(debug=False)