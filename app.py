# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import pandas as pd
import numpy as np
from scipy import signal
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import io
import base64
from plotly.subplots import make_subplots
import plotly.graph_objects as go

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.scripts.config.serve_locally = True

data = None

app.layout = html.Div(children=[
    html.Nav(
        className="navbar",
        children=[
            html.A(children=[
                html.Img(
                    src="/assets/images/LOGO FUNDO PRETO.png",
                    style={
                        'height':'80px',
                        'margin':'auto'
                    }
                )
            ])
        ]
    ),

    html.Div(
        className="background",
        children=[
            html.Div(
                className="overlay"
            ),

            html.Div(
                id="index-page",
                className="container center-content",
                children=[
                    html.Div(
                        className="row align-items-center justify-content-center no-opacity",
                        children=[
                            html.Div(
                                className="col-md-8 text-center",
                                children=[
                                    html.Div(
                                        className="text",
                                        children=[
                                            html.H1(
                                                children='Análise de dados NK319'
                                            ),
                                            html.H4(
                                                className="mb-5",
                                                children='Fórmula Tesla UFMG'
                                            ),
                                            dcc.Upload(
                                                children=[
                                                    'Upload de arquivos'
                                                ], 
                                                id="upload-data",
                                                className="btn btn-primary px-4 py-3 upload-btn",
                                                style={
                                                    'background-color':'#4ed840',
                                                    'border-color':'#0d0d0d'
                                                },
                                                multiple=True
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),

            html.Div(
                id="main-page",
                className="hidePage",
                children=[
                    dcc.Tabs(
                        value='tab-1',
                        parent_className='justify-content-center set-eighty-width',
                        content_className='tab-content',
                        colors={
                            'border':'black',
                            'primary':'#4ed840',
                            'background':'grey'
                        },
                        children=[
                            dcc.Tab(
                                label='Análise Geral',
                                value='tab-1',
                                children=[
                                    html.Div(
                                        className="form-plot-config",
                                        children=[
                                            html.Div(
                                                className="form-title",
                                                children=[
                                                    html.H1(
                                                        children=[
                                                            'Opções de Plotagem'
                                                        ]
                                                        
                                                    )
                                                ]
                                            ),
                                            html.Div(
                                                className='container-form',
                                                children=[
                                                    html.H4(
                                                        children='EIXO X',
                                                        className='form-label'
                                                    ),
                                                    dcc.Dropdown(
                                                        id='dropdown-analise-geral-X',
                                                        value='timer',
                                                        className='',
                                                        multi=False,
                                                        placeholder='Selecione as grandezas do eixo X'
                                                    ),
                                                    html.H4(
                                                        children='EIXO Y',
                                                        className='form-label'
                                                    ),
                                                    html.Div(
                                                        className='row-drop',
                                                        children=[
                                                            dcc.Dropdown(
                                                                id='dropdown-analise-geral-Y',
                                                                className='',
                                                                multi=True,
                                                                placeholder='Selecione as grandezas do eixo Y'
                                                            ),
                                                            html.H4(
                                                                children='Filtros',
                                                                className='form-label'
                                                            ),
                                                            dcc.Checklist(
                                                                id='filtros-checklist',
                                                                options=[
                                                                    {'label': 'Média Móvel', 'value': 'Média Móvel'},
                                                                    {'label': 'Filtro Mediana', 'value': 'Filtro Mediana'}
                                                                ],
                                                                inputStyle = {'margin-right':'3px'},
                                                                labelStyle =  {'margin-right':'8px'},
                                                                value=[]
                                                            ),
                                                            html.H4(
                                                                children='Subsequência do filtro média móvel',
                                                                className='form-label',
                                                                style={'margin-top':'8px', 'font-size':'1rem'}
                                                            ),
                                                            daq.NumericInput(
                                                                id='media-movel-input',
                                                                value=5,
                                                                min=1,
                                                                max=50
                                                            ),
                                                            html.Button(
                                                                id='plot-button',
                                                                children='Plotar',
                                                                className="btn btn-primary btn-lg",
                                                                style={'background-color':'#4ed840', 'margin':'20px 0px 20px 0px', 'border-color':'black'}
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            html.Div(
                                                id='Graph-content',
                                                children=[
                                            
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            dcc.Tab(
                                label='Gráficos customizados',
                                value='tab-2',
                                children=[
                                    dcc.Graph(
                                        figure={
                                            'data': [
                                                {'x': [1, 2, 3], 'y': [1, 4, 1],
                                                    'type': 'bar', 'name': 'SF'},
                                                {'x': [1, 2, 3], 'y': [1, 2, 3],
                                                'type': 'bar', 'name': u'Montréal'},
                                            ]
                                        }
                                    )
                                ]
                            ),
                            dcc.Tab(
                                label='Configurações',
                                value='tab-3',
                                children=[
                                    dcc.Graph(
                                        figure={
                                            'data': [
                                                {'x': [1, 2, 3], 'y': [2, 4, 3],
                                                    'type': 'bar', 'name': 'SF'},
                                                {'x': [1, 2, 3], 'y': [5, 4, 3],
                                                'type': 'bar', 'name': u'Montréal'},
                                            ]
                                        }
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
])
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

@app.callback(
    [Output('index-page', 'style'), Output('main-page', 'style'), Output('dropdown-analise-geral-Y', 'options'), Output('dropdown-analise-geral-X', 'options')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def hide_index_and_read_file(list_of_contents, list_of_names):
    global data
    if list_of_contents is not None:
        if ('legenda.txt' in list_of_names) and (len(list_of_names) >= 2):
            files = dict(zip(list_of_names, list_of_contents))
            legenda = pd.read_csv(io.StringIO(base64.b64decode(files['legenda.txt'].split(',')[1]).decode('utf-8')))
            legenda = [name for name in legenda.columns.values]
            for nome_do_arquivo in files:
                if(nome_do_arquivo != 'legenda.txt'):
                    data = pd.read_csv(io.StringIO(base64.b64decode(files[nome_do_arquivo].split(',')[1]).decode('utf-8')), delimiter='\t', names=legenda, index_col=False)
            
            options = [{'label' : column_name, 'value' : column_name} for column_name in legenda]
            return [{'display': 'none'},{'display':'inline'}, options, options]
        else:
            #TRATAR ERRO
            raise PreventUpdate
    else:
        raise PreventUpdate



@app.callback(
    Output('media-movel-input','disabled'),
    [Input('filtros-checklist','value')]
)
def disable_media_movel_input(selected_filters):
    if ('Média Móvel' in selected_filters) or ('Filtro Mediana' in selected_filters):
        return False
    else:
        return True

@app.callback(
    Output('Graph-content','children'),
    [Input('plot-button','n_clicks')],
    [State('dropdown-analise-geral-Y','value'),State('dropdown-analise-geral-X','value'), State('filtros-checklist','value'), State('media-movel-input','value')]
)
def plot_graph_analise_geral(button_clicks, selected_columns_Y, selected_X, filters, filters_subseq):
    if button_clicks != 0 and button_clicks != None:
        data_copy = data.copy()
        if filters_subseq % 2 == 0:
            filters_subseq = filters_subseq + 1
        if ('Filtro Mediana' in filters) and ('Média Móvel' in filters):
            for column in selected_columns_Y:
                data_copy[column] = smooth(signal.medfilt(data_copy[column], filters_subseq), filters_subseq)
        elif 'Média Móvel' in filters:
            for column in selected_columns_Y:
                data_copy[column] = smooth(data_copy[column], filters_subseq)
        elif 'Filtro Mediana' in filters:
            for column in selected_columns_Y:
                data_copy[column] = signal.medfilt(data_copy[column], np.array(filters_subseq))


        fig = make_subplots(rows=len(selected_columns_Y), cols=1, shared_xaxes=True, vertical_spacing=0.0)
        for cont, column_name in enumerate(selected_columns_Y):
            fig.add_trace(go.Scatter(y=data_copy[column_name], x=data_copy[selected_X], mode="lines", name=column_name), row=cont+1, col=1)
        fig['layout'].update(height=120*len(selected_columns_Y)+100, margin={'t':50, 'b':50, 'l':100, 'r':100})
        return dcc.Graph(
            figure=fig,
            id='figure-id',
            config={'autosizable' : False}
        )
    else:
        #TRATAR ERRO
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
