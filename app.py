# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import io
import base64

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
                        className="row align-items-center justify-content-center",
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
                                                        children='EIXO Y',
                                                        className='form-label'
                                                    ),
                                                    html.Div(
                                                        className='row-drop',
                                                        children=[
                                                            dcc.Dropdown(
                                                                id='dropdown-analise-geral',
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
                                                                    {'label': 'Savitzky-Golay', 'value': 'Savitzky-Golay'},
                                                                    {'label': 'Wiener', 'value': 'Wiener'}
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
                                                                style={'background-color':'#4ed840', 'margin':'20px 0px 20px 0px'}
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        id='Graph-content'
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

@app.callback(
    [Output('index-page', 'style'), Output('main-page', 'style'), Output('dropdown-analise-geral', 'options')],
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
            options = []
            for i in legenda:
                if i != 'timer':
                    options.append({'label' : i, 'value' : i})
            return [{'display': 'none'},{'display':'inline'}, options]
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
    if 'Média Móvel' in selected_filters:
        return False
    else:
        return True

@app.callback(
    Output('Graph-content','children'),
    Input('plot-button','n_clicks'),
    [State('dropdown-analise-geral','value'), State('filtros-checklist','value'), State('media-movel-input','value')]
)
def plot_graph_analise_geral(selected_columns, filters, media_movel_subseq):
    

if __name__ == '__main__':
    app.run_server(debug=True)
