import numpy as np
from scipy import signal
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_core_components as dcc
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc

class modalBody:
    @staticmethod
    def element_modal_body(column_name):
        
        html_generated = [
            html.Div(
                id={
                    'type': 'advconfig-data',
                    'index': column_name
                },
                children=[
                    dbc.Button(
                        children=[
                            column_name,
                            html.I(
                                className='dropdown-triangle'
                            )
                        ],
                        color="secondary",
                        block=True,
                        id={
                            'type': 'advchanges-button-collapse',
                            'index': column_name
                        },
                        style={'margin': '5px 0'},
                        n_clicks=0
                    ),
                    dbc.Collapse(
                        id={
                            'type': 'advchanges-collapse',
                            'index': column_name
                        },
                        children=[
                            html.H4(
                                children='Filtros Adicionais',
                                className='adv-config-subtitle',
                            ),
                            dcc.Checklist(
                                id={
                                    'type': 'bandpass-checklist',
                                    'index': column_name
                                },
                                options=[
                                    {'label': 'Passa-Banda', 'value': 'Passa-Banda'},
                                ],
                                inputStyle={'margin-right': '3px'},
                                labelStyle={'margin-right': '8px'},
                                value=[]
                            ),
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        daq.NumericInput(
                                            id={
                                                'type': "bandpass-inf-limit",
                                                'index': column_name
                                            },
                                            label={
                                                'label': 'limite inferior (Hz)'},
                                            min=1,
                                            max=15,
                                            value=1
                                        )
                                    ),
                                    dbc.Col(
                                        daq.NumericInput(
                                            id={
                                                'type': "bandpass-sup-limit",
                                                'index': column_name
                                            },
                                            label={
                                                'label': 'limite superior (Hz)'},
                                            min=1,
                                            max=15,
                                            value=15
                                        )
                                    )
                                ]
                            ),
                            dcc.Checklist(
                                id={
                                    'type': "savitzky-checklist",
                                    'index': column_name
                                },
                                options=[
                                    {'label': 'Filtro savitzky-golay (Passa-baixas)',
                                    'value': 'Filtro savitzky-golay'},
                                ],
                                inputStyle={'margin-right': '3px'},
                                labelStyle={'margin-right': '8px'},
                                value=[]
                            ),
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        daq.NumericInput(
                                            id={
                                                'type': "savitzky-cut",
                                                'index': column_name
                                            },
                                            label={
                                                'label': 'Tamanho da subsequência'},
                                            min=0,
                                            max=20,
                                            value=5
                                        )
                                    ),
                                    dbc.Col(
                                        daq.NumericInput(
                                            id={
                                                'type': "savitzky-poly",
                                                'index': column_name
                                            },
                                            label={'label': 'Grau polinomial'},
                                            min=0,
                                            max=5,
                                            value=1
                                        )
                                    )
                                ]
                            ),
                            dbc.Row(
                                className="divider"
                            )
                        ]
                    )
                ]
            )
        ]

        return html_generated