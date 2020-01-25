import base64
import socket
import time
import hashlib

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc


import plotly.graph_objs as go
import plotly.graph_objs as go

from flask import Flask, jsonify, request
from pymongo import MongoClient


client = MongoClient("mongodb://db:27017")
db = client.MoneyManagementDB
reports = db["reports"]

server = Flask('main', static_url_path='')
app = dash.Dash(name='reportity_app', server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("D&D", href="#")),
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="Menu",
            children=[
                dbc.DropdownMenuItem("Home"),
                dbc.DropdownMenuItem("Log In"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Reportity git", href='https://github.com/fnatanoy/reportity'),
            ],
        ),
    ],
    brand="Reportity",
    brand_href="#",
    sticky="top",
)

drag_and_drop_card_base = dcc.Upload(
    id='upload-data',
    children=dbc.Row(
        [
            html.Div('Drag and Drop or Select Files', id='dnd_text'),
            html.A('')
        ],
        justify='center',
    ),
    style={
        'width': '80%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px',
    },
    multiple=False
)

instruction_card = dbc.Col(
    [
        html.H2("Reportity Hub"),
        html.P('Your friendly reports keeper'),
        html.P('Just drag & drop your html report and get the url! as simple as that'),
    ],
)

drag_and_drop_card = dbc.Col(
    [
        html.Br(),
        drag_and_drop_card_base,
        
    ],
)

url_card =  dbc.Col(
    [
        html.Br(),
        html.P('Heres your url'),
        html.P('lDON\'T loose the url since you won\'t be able to get it again!'),
        html.Br(),
        html.P('url', id='url_text'),
    ],
    align="right",
)

body = dbc.Container(   
    [
        dbc.Row(
            [
                dbc.Col(instruction_card, width=6),
                dbc.Col(
                    [
                        html.Div(children=[drag_and_drop_card], id="content", style={'display': 'block'}),
                        html.Div(children=[url_card], id="url_card", style={'display': 'none'}),
                        html.Br(),
                        dbc.Row(
                            dbc.Col(
                                [
                                    html.Div(dbc.Button(children=["Submit"], color="secondary", id='bt_submit', n_clicks=0), id='submit'),
                                ],
                                width=6
                            ),
                            justify='center'
                        )
                    ],
                ),
            ]
        )
    ],
    className="mt-4",
)



app.layout = html.Div([navbar, body])

@app.callback(
    [
        Output("content", "style"),
        Output("url_card", "style"),
        Output("bt_submit", "children"),
        Output("url_text", "children"),
        Output("dnd_text", "children"),
        Output('upload-data', 'filename'),
    ],
    [
        Input('bt_submit', 'n_clicks'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State('upload-data', 'last_modified'),
    ],
)
def update_output(
    bt_submit_clicks,
    list_of_contents,
    list_of_names,
    list_of_dates,
):
    if list_of_names is not None: 
        if int(bt_submit_clicks) % 2 == 1:
            if type(list_of_contents) is not str:
                return [
                    {'display': 'block'},
                    {'display': 'none'},
                    'Submit',
                    '',
                    'Drag and Drop or Select Files',
                    '',
                ]

            html_id = insert_html(
                contents=list_of_contents,
                names=list_of_names,
                dates=list_of_dates,
            )
            html_url = 'http://ec2-52-14-38-132.us-east-2.compute.amazonaws.com:5000/report_id/{html_id}'.format(
                html_id=html_id,
            )
            return [
                {'display': 'none'},
                {'display': 'block'},
                'Got it',
                html_id,
                'Drag and Drop or Select Files',
                None,
            ]

        else:
            return [
                {'display': 'block'},
                {'display': 'none'},
                'Submit',
                '',
                list_of_names,
                list_of_names,
            ]

    return [
        {'display': 'block'},
        {'display': 'none'},
        'Submit',
        '',
        'Drag and Drop or Select Files',
        '',
    ]


def insert_html(
    contents,
    names,   
    dates,   
):
    hashed_id = get_hashed_id()
    content_type, content_string = contents.split(',')

    decoded_html = base64.b64decode(content_string)
    reports.insert_one({
        "report_id": hashed_id,
        "report_data": decoded_html
    })

    return hashed_id


def get_hashed_id():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    time_stamp = time.time()
    html_id = '{time_stamp}_{ip_address}'.format(
        time_stamp=time_stamp,
        ip_address=ip_address,
    )

    html_hash_id = hashlib.md5(html_id.encode()).hexdigest()

    return html_hash_id


@server.route('/report_id/<report_id>', methods=['GET'])
def get_id(report_id):
    report_data = reports.find_one({
        "report_id":str(report_id)
    })["report_data"]

    return report_data



@server.route('/help')
def student():
    return '''
    <!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Index</title>
</head>

<body>
    <h1 style="color: blue">Index</h1>
    <p>This is an HTML file served up by Flask</p>
</body>

</html><title>Help</title>
    <h1>Help</h1>
        '''


if __name__=="__main__":
    server.run(host='0.0.0.0',debug=True)

