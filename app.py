# -*- coding: utf-8 -*-

#------------- Import Library -------------#
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import pandas as pd
import numpy as np
from scipy import signal
from dash.dependencies import Input, Output, State, ClientsideFunction, MATCH, ALL
from dash.exceptions import PreventUpdate
import io
import base64
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import visdcc
#------------------------------------------#

#-------------- Import Pages --------------#
from modules.functions.trataDados import Trata_dados
from modules.functions.filtros import Filtros
from modules.functions.somaLista import somaLista
from modules.callbacks.divVoltas import DivVoltas
from modules.callbacks.lerArquivo import lerArquivo
from modules.callbacks.plotarGrafico import plotarGrafico
#------------------------------------------#

#---------- Instanciando Objetos ----------#
dados_tratados = Trata_dados()
filtros = Filtros()
soma_Lista = somaLista()
divisao_voltas = DivVoltas()
leitura_de_arquivos = lerArquivo(None,None)
grafico = plotarGrafico(None)
#------------------------------------------#

external_stylesheets = [dbc.themes.BOOTSTRAP]
external_scripts = ["https://cdn.plot.ly/plotly-1.2.0.min.js"]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.scripts.config.serve_locally = True

#--------------- Global var ---------------#
num_dados = None #Número de colunas dos arquivos de dados
data = None #Pandas Dataframe com os dados utilizados
data_copy = None #Cópia da variável data para a 
eixoY = None #Armazena as colunas que estão plotadas
ploted_figure = None #Armazena os dados da dcc.Graph() figure plotada
tempo_voltas = [0] #Armazena os valores dos tempos de cada volta (divisão de voltas)
#------------------------------------------#


# LAYOUT DA PAGINA
app.layout = html.Div(children=[
    # Layout NavBar
    html.Header(
        children=[
            html.Nav(
                style={"background-color":"black"},
                className="navbar navbar-expand-md navbar-dark",
                children=[
                    html.A(
                        children=[
                            html.Img(
                                src="/assets/images/logo-fundo-preto.png",
                                className="logo-tesla"
                            )
                        ],
                        href="https://formulateslaufmg.wixsite.com/teslaufmg"
                    ),
                    html.Div(
                        className="collapse navbar-collapse",
                        children=[
                            html.Ul(
                                className="navbar-nav ml-5",
                                children = [
                                    html.Li(
                                        className="nav-item",
                                        children=[
                                            html.A(
                                                href="#",
                                                className="nav-link",
                                                children="Gerar relatório"
                                            )
                                        ]
                                    ),
                                    html.Li(
                                        className="nav-item",
                                        children=[
                                            html.A(
                                                href="#",
                                                className="nav-link",
                                                children="Manual de instruções"
                                            )
                                        ]
                                    )
                                ]
                            ),
                            dbc.ButtonGroup(
                                size="md",
                                className="mr-1 ml-auto",
                                children=[
                                    dbc.Button(
                                        children="Salvar",
                                        outline=True,
                                        color="success"
                                    ), 
                                    dbc.Button(
                                        children="Exportar",
                                        color="success"
                                    )
                                ],                               
                            ),
                        ]
                    )
                ]
            )
        ]
    ),

    # Layout do Corpo da pagina
    html.Div(
        className="background",
        children=[
            # Layout do Fundo
            html.Div(
                className="overlay"
            ),
            dbc.Alert(
                duration=5000,
                dismissable=True,
                color="danger",
                fade = True,
                id="upload-files-alert",
                is_open=False,
                className="mx-4",
                style={"top":"15px"}
            ),
            # Layout da parte central, com o escrito e botao
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
                                    # Definiçao dos escritos
                                    html.Div(
                                        className="text",
                                        children=[
                                            # H1 = Fonte maior, Título
                                            html.H1(
                                                children='Análise de dados NK319'
                                            ),
                                            # H4 = Fonte menor, subtítulo
                                            html.H4(
                                                className="mb-5",
                                                children='Fórmula Tesla UFMG'
                                            ),
                                            # Layout botão
                                            dbc.Spinner(
                                                color='success',
                                                children=[
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
                                                    ),
                                                    html.Div(
                                                        id="upload-data-loading"
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),

            # Segunda pagina, com graficos e configuraçoes
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
                                #Primeiro Tab (Analise Geral)
                                label='Análise Geral',
                                value='tab-1',
                                children=[
                                    # Conteudo do primeiro tab
                                    html.Div(
                                        className="form-plot-config",
                                        children=[
                                            # Título
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
                                            # Conteudo abaixo do titulo
                                            html.Div(
                                                className='container-form',
                                                children=[
                                                    # Configuraçao Eixo X
                                                    html.H4(
                                                        children='EIXO X',
                                                        className='form-label'
                                                    ),
                                                    # Dropdown para selecionar coluna de dados para o eixo X
                                                    dcc.Dropdown(
                                                        id='dropdown-analise-geral-X',
                                                        value='Timer',
                                                        className='',
                                                        multi=False,
                                                        placeholder='Selecione as grandezas do eixo X'
                                                    ),
                                                    # Configuraçao Eixo Y
                                                    html.H4(
                                                        children='EIXO Y',
                                                        className='form-label'
                                                    ),
                                                    html.Div(
                                                        className='row-drop',
                                                        children=[
                                                            # Dropdown para selecionar coluna de dados para o eixo Y
                                                            dcc.Dropdown(
                                                                id='dropdown-analise-geral-Y',
                                                                className='',
                                                                multi=True,
                                                                placeholder='Selecione as grandezas do eixo Y'
                                                            ),
                                                            html.Div(
                                                                className='config-pre-plot',
                                                                style={'display':'flex'},
                                                                children=[
                                                                    # Configuraçao Filtros
                                                                    html.Div(
                                                                        className='config-filtros',
                                                                        children=[
                                                                            # Título
                                                                            html.H4(
                                                                                children='Filtros',
                                                                                className='form-label'
                                                                            ),
                                                                            # Checklist de filtros
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
                                                                            # Selecionar valor de subsequencia do filtro
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
                                                                        ]
                                                                    ),
                                                                    # Configuração Linhas de Referência
                                                                    html.Div(
                                                                        id='config-ref-line',
                                                                        className='ref-line',
                                                                        style={
                                                                            'display':'none'
                                                                        },
                                                                        children=[
                                                                            # Título
                                                                            html.H4(
                                                                                children='Linhas de Referência',
                                                                                style={
                                                                                    'position': 'relative',
                                                                                    'left': '10px',
                                                                                    'bottom': '15px'
                                                                                },
                                                                                className='form-label'
                                                                            ),
                                                                            # Selecionar valor de onde a linha vai estar
                                                                            html.Div(
                                                                                className='definir-valor',
                                                                                style={
                                                                                    'position': 'relative',
                                                                                    'bottom': '15px',
                                                                                    'display': 'flex'
                                                                                },
                                                                                children=[
                                                                                    # Selecionar da linha horizontal
                                                                                    html.Div(
                                                                                        className='definir-valor-horizontal',
                                                                                        style={
                                                                                            'position':'relative',
                                                                                            'left': '10px'
                                                                                        },
                                                                                        children=[
                                                                                            # Checklist da linha horizontal
                                                                                            dcc.Checklist(
                                                                                                id='checklist-horizontal',
                                                                                                options=[
                                                                                                    {'label': 'Linha Horizontal', 'value': 'Horizontal'}
                                                                                                ],
                                                                                                inputStyle = {'margin-right':'8px'},
                                                                                                labelStyle =  {'margin-right':'8px'},
                                                                                                value=[]
                                                                                            ),
                                                                                            # Escolher definir valor ou definir no gráfico
                                                                                            dbc.RadioItems(
                                                                                                id="horizontal-row",
                                                                                                style={
                                                                                                    'position':'relative',
                                                                                                    'left': '10px'
                                                                                                },
                                                                                                options=[
                                                                                                    {"label": "Definir no gráfico", "value": "horizontal-grafico"},
                                                                                                    {"label": "Definir valor", "value": "horizontal-value", "disable":True},
                                                                                                ],
                                                                                                value=[]
                                                                                            ),
                                                                                            html.Div(
                                                                                                className='horizontal-input-set',
                                                                                                id='set-input-div',
                                                                                                style={
                                                                                                    'display':'none'
                                                                                                },
                                                                                                children=[
                                                                                                    daq.NumericInput(
                                                                                                        id='horizontal-input',
                                                                                                        max=100000,
                                                                                                        min=-100000,
                                                                                                        value=0
                                                                                                    ),
                                                                                                    dbc.Button(
                                                                                                        style={
                                                                                                            'position':'relative',
                                                                                                            'left':'15px'
                                                                                                        },
                                                                                                        children="Set",
                                                                                                        color="secondary",
                                                                                                        className="set-numero-voltas",
                                                                                                        id='set-reference-button'
                                                                                                    ),
                                                                                                ]
                                                                                            ),
                                                                                            # Botão para acrescentar linha de referência horizontal
                                                                                            html.Div(
                                                                                                id="graph-control-panel",
                                                                                                className="interactive-graph-box",
                                                                                                style={
                                                                                                    'margin': '10px 0px 0px 40px'
                                                                                                    },
                                                                                                children=[
                                                                                                    dcc.Checklist(
                                                                                                        id="add-line-button",
                                                                                                        labelClassName="interations-button button-int",
                                                                                                        options=[
                                                                                                            {'label':'+ Line', 'value':'Line'}
                                                                                                            ],
                                                                                                        inputClassName="bg-plus",
                                                                                                        value=[]
                                                                                                    )
                                                                                                ]
                                                                                            ),
                                                                                        ]
                                                                                    ),
                                                                                ]
                                                                            ),     
                                                                        ]
                                                                    ),
                                                                    # Configuração de Sobreposição de Voltas
                                                                    html.Div(
                                                                        className="config-sobreposicao",
                                                                        id="config-sobreposicao",
                                                                        style={
                                                                            'display':'none'
                                                                        },
                                                                        children=[
                                                                            # Título
                                                                            html.H4(
                                                                                children='Sobreposição de Voltas',
                                                                                style={
                                                                                    'position': 'relative',
                                                                                    'left': '10px',
                                                                                    'bottom': '15px'
                                                                                },
                                                                                className='form-label'
                                                                            ),
                                                                            dbc.Button(
                                                                                children="Sobrepor",
                                                                                color="secondary",
                                                                                className="sovoltas",
                                                                                id='sobreposicao-button',
                                                                                style={
                                                                                    'margin-left':'50px'
                                                                                }
                                                                            ),
                                                                        ]
                                                                    ),
                                                                ]
                                                            ),
                                                            # Botão de Plotagem
                                                            dbc.Button(
                                                                id='plot-button',
                                                                className="tesla-button",
                                                                children=[
                                                                    'Plotar',
                                                                    dbc.Spinner(
                                                                        spinner_style = {'display':'inline-block', 'margin':'0 0 0 .5rem'},
                                                                        size='sm',
                                                                        children=[
                                                                            html.Div(id="plot-loading")
                                                                        ]
                                                                    )
                                                                ],
                                                                color="success",
                                                                style={'margin':'20px 0px 20px 0px'},
                                                                n_clicks_timestamp=0
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            # Conteudo dos gráficos
                                            html.Div(
                                                id='Graph-content',
                                                children=[
                                                    dcc.Graph(
                                                        id='figure-id',
                                                        config={'autosizable' : False},
                                                        style={'display':'none'}
                                                    ),
                                                ]
                                            ),
                                            # Botão de Opções Avançadas
                                            html.Br(), 
                                            dbc.Button(
                                                children="Opções avançadas",
                                                color="secondary",
                                                className="mr-1 hiden modal-open-button-style",
                                                id='modal-button'
                                            )
                                        ]
                                    )
                                ]
                            ),
                            # #Segundo Tab (Grafico Customizados)
                            # dcc.Tab(
                            #     label='Gráficos customizados',
                            #     value='tab-2',
                            #     children=[
                            #         dcc.Graph(
                            #             figure={
                            #                 'data': [
                            #                     {'x': [1, 2, 3], 'y': [1, 4, 1],
                            #                         'type': 'bar', 'name': 'SF'},
                            #                     {'x': [1, 2, 3], 'y': [1, 2, 3],
                            #                     'type': 'bar', 'name': u'Montréal'},
                            #                 ]
                            #             }
                            #         )
                            #     ]
                            # ),
                            #Terceiro Tab (Configuraçoes)
                            dcc.Tab(
                                label='Configurações',
                                value='tab-3',
                                children=[
                                    # Conteudo Terceiro Tab
                                    html.Div(
                                        className='config-page',
                                        children=[
                                            # Título
                                            html.Div(
                                                className="config-title",
                                                children=[
                                                    html.H1(
                                                        children=[
                                                            'Configurações Gerais'
                                                        ]   
                                                    )
                                                ]
                                            ),
                                            # Conteudo do Tab
                                            html.Div(
                                                className="divisão-content",
                                                children=[
                                                    # Opção para selecionar divisão de voltas
                                                    dbc.Checklist(
                                                        options=[
                                                            {"label": "Divisão de Voltas", "value": 1},
                                                        ],
                                                        id="switches-input-divisao",
                                                        value=[],
                                                        switch=True,
                                                        style={
                                                            'margin-top':'8px',
                                                            'margin-bottom':'8px',
                                                            'font-size':'18px'
                                                        }
                                                    ),
                                                    # Conteudo divisão de voltas
                                                    html.Div(
                                                        id="corpo-divisao-voltas",
                                                        className="divisao-sub-content",
                                                        style={'display':'none'},
                                                        children=[
                                                            # Checklist de Distancia ou Tempo
                                                            dbc.RadioItems(
                                                                id="radios-row",
                                                                options=[
                                                                    {"label": "Distância", "value": "distancia"},
                                                                    {"label": "Tempo", "value": "tempo"},
                                                                ],
                                                                value=[]
                                                            ),
                                                            # Conteudo do Item selecionado
                                                            html.Div(
                                                                className="checklist-selected",
                                                                children=[
                                                                    # Se Tempo for Selecionado
                                                                    html.Div(
                                                                        className="if-tempo-selected",
                                                                        id="corpo-divisao-tempo",
                                                                        style={'display':'none'},
                                                                        children=[
                                                                            # Selecionar número de voltas
                                                                            html.H4(
                                                                                children='Número de Voltas:',
                                                                                className='form-label',
                                                                                style={'margin-top':'8px', 'font-size':'1rem'}
                                                                            ),
                                                                            daq.NumericInput(
                                                                                id='divisão-voltas-tempo-input',
                                                                                value=1,
                                                                                min=1,
                                                                                max=100,
                                                                                style={
                                                                                    'position':'relative',
                                                                                    'top':'4px'
                                                                                }
                                                                            ),
                                                                            # Setando o valor de cada volta
                                                                            html.H4(
                                                                                children='Defina o tempo de cada volta (s.ms):',
                                                                                className='form-label',
                                                                                style={'margin-top':'8px', 'font-size':'1rem'}
                                                                            ),
                                                                            html.Div(
                                                                                id="time-input",
                                                                                style={
                                                                                    'margin-top':'8px',
                                                                                    'margin-bottom':'8px'
                                                                                },
                                                                                children= []
                                                                            ),
                                                                            dbc.Button(
                                                                                children="Set",
                                                                                color="secondary",
                                                                                className="set-numero-voltas",
                                                                                id='input-voltas-button-tempo',
                                                                                style={
                                                                                    'margin-bottom':'6px'
                                                                                }
                                                                            ),
                                                                        ]
                                                                    ),
                                                                    # Se Distancia for Selecionado
                                                                    html.Div(
                                                                        className="if-dist-selected",
                                                                        id="corpo-divisao-distancia",
                                                                        style={'display':'none'},
                                                                        children=[
                                                                            # Selecionar a distância das voltas
                                                                            html.H4(
                                                                                children='Distância das Voltas:',
                                                                                className='form-label',
                                                                                style={'margin-top':'8px', 'font-size':'1rem'}
                                                                            ),
                                                                            dbc.InputGroup(
                                                                                [dbc.InputGroupAddon("Distancia", addon_type="prepend"), 
                                                                                 dbc.Input(
                                                                                    placeholder="Distância em metros",
                                                                                    type="number",
                                                                                    min=0,
                                                                                    id="input-div-distancia"
                                                                                 )
                                                                                ],
                                                                                style={
                                                                                    'margin-top':'8px',
                                                                                    'margin-bottom':'8px'
                                                                                }
                                                                            ),
                                                                            dbc.Button(
                                                                                children="Set",
                                                                                color="secondary",
                                                                                className="set-distancia-voltas",
                                                                                id='input-voltas-button-distancia',
                                                                                style={
                                                                                    'margin-bottom':'6px'
                                                                                }
                                                                            ),
                                                                        ]
                                                                    ),
                                                                ]
                                                            ),
                                                        ]   
                                                    ),
                                                ]
                                            ),
                                            #html.Div(
                                            #    className="sobreposicao-content",
                                            #    children=[
                                            #        # Opção para selecionar sobreposição de voltas
                                            #        dbc.Checklist(
                                            #            options=[
                                            #                {"label": "Sobreposição de Voltas", "value": 1},
                                            #            ],
                                            #            id="switches-input-sobreposicao",
                                            #            value=[],
                                            #            switch=True,
                                            #            style={
                                            #                'margin-top':'8px',
                                            #                'margin-bottom':'8px',
                                            #                'font-size':'18px'
                                            #            }
                                            #        ),
                                            #    ]
                                            #),
                                        ]
                                    ), 
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    ),

    # Layout botão de Configurações avançadas
    dbc.Modal(
        contentClassName = 'modal-content',
        children = [
            # Título
            dbc.ModalHeader(
                children="Configurações avançadas de plotagem",
                className="modal-header-and-footer"
            ),
            # Corpo
            dbc.ModalBody(
                id='modal-body'
            ),
            # Parte de baixo
            dbc.ModalFooter(
                children=[
                    dbc.Button("Fechar", id="close-modal", className="ml-auto tesla-button"),
                    dbc.Spinner(
                        children = [
                            dbc.Button("Aplicar", id="apply-adv-changes-button", className="tesla-button", n_clicks_timestamp=0),
                            html.Div(
                                id="apply-adv-changes-loading"
                            )
                        ],
                        size="sm",
                        spinner_style = {'margin': '0 37px'},
                        color="success"
                    )
                ],
                className="modal-header-and-footer"
            )
        ],
        id="modal-graph-config",
        scrollable=True
    )
])
# Função utilizada para somar os valores de uma lista
def soma_lista(lista):

    if len(lista) == 1:
        return lista[0]
    else:
        return lista[0] + soma_lista(lista[1:])

# Função que divide o array de distancia pelas voltas
def chunks(lista, n):
    for i in range(0, len(lista), n):
        yield lista[i:i + n]

# Desativa as exceptions ligadas aos callbacks, permitindo a criação de callbacks envolvendo IDs que ainda não foram criados
app.config['suppress_callback_exceptions'] = True

@app.callback(
    Output({'type':'advchanges-collapse','index': MATCH}, 'is_open'),
    [Input({'type':'advchanges-button-collapse','index': MATCH}, 'n_clicks')],
    [State({'type':'advchanges-collapse','index': MATCH}, 'is_open')]
)
def toggle_collapse(n_clicks, is_open):
    if(n_clicks):
        return not is_open
    return is_open

@app.callback(
    [Output({'type':"bandpass-inf-limit",'index': MATCH},'disabled'),
     Output({'type':"bandpass-sup-limit",'index': MATCH},'disabled')],
    [Input({'type':'bandpass-checklist','index': MATCH}, 'value')]
) 
def disable_inputs_passabanda(checklist):
    if('Passa-Banda' in checklist):
        return [False,False]
    return [True, True]

@app.callback(
    [Output({'type':"savitzky-cut",'index': MATCH},'disabled'),
     Output({'type':"savitzky-poly",'index': MATCH},'disabled')],
    [Input({'type':'savitzky-checklist','index': MATCH}, 'value')]
) 
def disable_inputs_savitzky(checklist):
    if('Filtro savitzky-golay' in checklist):
        return [False,False]
    return [True, True]

# Callback de abrir/fechar o modal de configurações avançadas
@app.callback(
    Output("modal-graph-config", "is_open"),
    [Input("modal-button", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("modal-graph-config", "is_open")]
)
def toggle_modal(n1, n2, is_open):

    if n1 or n2:
        return not is_open
    
    return is_open

# Callback que habilita e desabilita o INPUT de média móvel
@app.callback(
    Output('media-movel-input','disabled'),
    [Input('filtros-checklist','value')]
)
def disable_media_movel_input(selected_filters):
    
    if ('Média Móvel' in selected_filters) or ('Filtro Mediana' in selected_filters):
        return False
    else:
        return True

# Callback que habilita e desabilita os radioItens de linha de referência horizontal
@app.callback(
    Output('horizontal-row','options'),
    [Input('checklist-horizontal','value')]
)
def disable_radioItens_ref_horizontal(selected_checklist):

    if('Horizontal' in selected_checklist):
        return ({"label": "Definir no gráfico", "value": "horizontal-grafico"}, 
                {"label": "Definir valor", "value": "horizontal-value", "disabled": True},)
    else:
        return ({"label": "Definir no gráfico", "value": "horizontal-grafico", "disabled": True}, 
                {"label": "Definir valor", "value": "horizontal-value", "disabled": True},)

# Callback que habilita e desabilita o INPUT de linha de referencia horizontal
@app.callback(
    Output('set-input-div','style'),
    [Input('horizontal-row','value'),
     Input('checklist-horizontal','value')]
)
def disable_ref_horizontal_input(selected_radio, selected_checklist):
    
    if('horizontal-value' in selected_radio) and ('Horizontal' in selected_checklist):
        return ({'display': 'flex',
                 'position':'relative',
                 'left':'20px',
                 'top':'10px'
                })
    else:
        return {'display':'none'}

# Callback que habilita e desabilita o botão de acrescentar linha de referência horizontal no gráfico
@app.callback(
    Output('graph-control-panel','style'),
    [Input('horizontal-row','value'),
     Input('checklist-horizontal','value')]
)
def disable_ref_vertical_button(selected_radio, selected_checklist):

    if('Horizontal' in selected_checklist) and ('horizontal-grafico' in selected_radio):
        return ({'margin': '10px 0px 0px 40px',
                 'display': 'block'
                })
    else:
        return {'display':'none'}

# Callback que habilita e desabilita as configurações de divisao de voltas
@app.callback(
    Output('corpo-divisao-voltas','style'),
    [Input('switches-input-divisao','value')]
)
def able_divisao_volta(switch_value):
    
    return divisao_voltas.able_divisao_volta(switch_value)

# Callback que habilita e desabilita as configurações de setar distancia ou tempo
@app.callback(
    [Output('corpo-divisao-tempo','style'),
     Output('corpo-divisao-distancia','style')],
    [Input('radios-row','value')]
)
def able_tempo_or_distancia(radios_value):
    
    return divisao_voltas.able_tempo_or_distancia(radios_value)

# Callback que define a quantidade de inputs para o tempo das voltas e guarda os tempos no array
@app.callback(
    Output('time-input', 'children'),
    [Input('divisão-voltas-tempo-input', 'value'),
     Input('input-voltas-button-tempo', 'n_clicks')],
    [State('time-input', 'children'),
     State({'type':'input-tempo','index':ALL}, 'value')]
)
def quantidade_input_div_voltas(numero_voltas, n1, children, input_value):

    global tempo_voltas

    new_input = html.Div([
                    dbc.InputGroup(
                        [dbc.InputGroupAddon(("Volta {}:".format(i)), 
                                              addon_type="prepend"
                                            ), 
                         dbc.Input(
                            id={
                                'type':'input-tempo',
                                'index':'input-volta-{}'
                            },
                            type="number",
                            min=0,
                            step=0.01,
                            value=0
                         )
                        ]
                    ) 
                    for i in range(1, numero_voltas+1)
                ])

    children.insert(0, new_input)
    for i in range(1, len(children)):
        children.pop(i)

    tempo_div_voltas = [0]
    if n1:
        tempo_div_voltas = input_value

        # Seta o array com os valores das voltas somados
        tempo_voltas = np.zeros(len(tempo_div_voltas))

        for i in range(0, len(tempo_voltas)-1):
            tempo_voltas[i] = soma_lista(tempo_div_voltas[:i+1])

        tempo_voltas[len(tempo_div_voltas)-1] = soma_lista(tempo_div_voltas)

    return children

# Callback para o Upload de arquivos, montagem do dataFrame e do html do modal
@app.callback(
    [Output('index-page', 'style'), 
     Output('main-page', 'style'),
     Output('dropdown-analise-geral-Y', 'options'),
     Output('dropdown-analise-geral-X', 'options'),
     Output('upload-data-loading','children'), 
     Output('upload-files-alert','is_open'), 
     Output('upload-files-alert', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def hide_index_and_read_file(list_of_contents, list_of_names):   
    
    leitura_de_arquivos.get_data(list_of_contents, list_of_names)
    global data 
    data = leitura_de_arquivos.data
    global num_dados 
    num_dados = leitura_de_arquivos.num_dados
    return [
        leitura_de_arquivos.index_page_style,
        leitura_de_arquivos.main_page_style,
        leitura_de_arquivos.analise_Y_options,
        leitura_de_arquivos.analis_X_options,
        leitura_de_arquivos.upload_loading_children,
        leitura_de_arquivos.files_alert_open,
        leitura_de_arquivos.files_alert_children]
    
# Callback do botão de plotagem de gráficos
@app.callback(
    [Output('apply-adv-changes-loading','children'),
     Output('Graph-content','children'),
     Output('modal-button','style'),
     Output('modal-body','children'),
     Output('plot-loading','children'),
     Output('config-ref-line', 'style'),
     Output('config-sobreposicao','style')],
    [Input('plot-button','n_clicks_timestamp'),
     Input('apply-adv-changes-button','n_clicks_timestamp'),
     Input('switches-input-divisao','value'),
     Input('radios-row','value'),
     Input('input-voltas-button-distancia', 'n_clicks'),
     Input('sobreposicao-button', 'n_clicks')],
    [State('dropdown-analise-geral-Y','value'), 
     State('dropdown-analise-geral-X','value'),
     State('filtros-checklist','value'),
     State('media-movel-input','value'),
     State({'type': 'advconfig-data', 'index': ALL}, 'id'),
     State({'type': 'bandpass-checklist', 'index': ALL}, 'value'),
     State({'type':'bandpass-inf-limit', 'index': ALL}, 'value'),
     State({'type':'bandpass-sup-limit', 'index': ALL}, 'value'),
     State({'type': 'savitzky-checklist', 'index': ALL}, 'value'),
     State({'type':'savitzky-cut', 'index': ALL}, 'value'),
     State({'type':'savitzky-poly', 'index': ALL}, 'value'),
     State('input-div-distancia', 'value')]
)
def plot_graph_analise_geral(button_plot, button_apply, div_switches_value, div_radios_value, set_div_dist, sobreposicao_button,
                             selected_columns_Y, selected_X, filters, filters_subseq, 
                             identificador, bandpass_check, bandpass_inf, bandpass_sup , savitzky_check, savitzky_cut, savitzky_poly,
                             input_div_dist):
    
    
    global data#ja foi usada e nao sera mais
    global tempo_voltas#ja foi usada antes e termina aq
    grafico.plotar(button_plot, button_apply, div_switches_value, div_radios_value, set_div_dist, sobreposicao_button,
                 selected_columns_Y, selected_X, filters, filters_subseq,
                 identificador, bandpass_check, bandpass_inf, bandpass_sup, savitzky_check, savitzky_cut, savitzky_poly,
                 input_div_dist,data,tempo_voltas)
    global ploted_figure#começa aq e continua
    ploted_figure = grafico.ploted_figure
    
    return[grafico.changes_loading_children,
        grafico.graph_content_children,
        grafico.modal_button_style,
        grafico.modal_body_children ,
        grafico.plot_loading_children ,
        grafico.ref_line_style ,
        grafico.configuracao_sobreposicao_style]

# Callback que muda a classe do botão de linhas horizontais, se pressionado
@app.callback(
    Output('add-line-button' , 'labelClassName'),
    [Input('add-line-button' , 'value')]
)
def change_button_class(value):

    if('Line' in value):
        return 'interations-button-pressed button-int'

    return 'interations-button button-int'

# Callback que adiciona linhas de referencia no gráfico (Horizontais e Verticais)
@app.callback (
    [Output("figure-id","figure"),
     Output("add-line-button", "value")],
    [Input("figure-id","clickData"),
     Input("checklist-horizontal", "value"),
     Input('horizontal-row','value'),
     Input('set-reference-button','n_clicks')],
    [State("figure-id","relayoutData"),
     State("add-line-button", "value"),
     State('horizontal-input','value')]
)
def display_reference_lines(clickData, checklist_horizontal, radios_value, n1, zoom_options, add_line, input_value):

    if clickData is not None:

        global ploted_figure

        #HORIZONTAL
        if("Horizontal" in checklist_horizontal):

            if('horizontal-grafico' in radios_value):
        
                if("Line" in add_line):
                    
                    yref = "y"
                    curveNumber = clickData['points'][0]['curveNumber']
                    if(  curveNumber != 0 ):
                        yref = yref + str(curveNumber+1)
                    
                    ploted_figure.add_shape(type="line",
                                            xref="paper", yref=yref,
                                            y0 = clickData['points'][0]['y'], y1 = clickData['points'][0]['y'],
                                            x0 = 0, x1 = 1,
                                            line = dict(
                                                color = "black",
                                                dash = "dot",
                                                width = 1
                                            ),
                                           )
                    
                    return [ploted_figure,[]]
                else:
                    raise PreventUpdate
            else:
                raise PreventUpdate
        #VERTICAL
        else:
            
            last_figure = go.Figure(ploted_figure)
            last_figure.add_shape(type = "line",
                                  yref = "paper",
                                  x0 = clickData['points'][0]['x'], x1 = clickData['points'][0]['x'],
                                  y0 = 0, y1 = 1,
                                  line = dict(
                                    color = "#505050",
                                    width = 1.5
                                  )
                                 )
            
            return [last_figure, dash.no_update]
    elif clickData is None:
        # Horizontal definido no input
        if('horizontal-value' in radios_value) and ("Horizontal" in checklist_horizontal):

            if n1:
                        
                ploted_figure.add_shape(type="line",
                                        xref="paper", yref="y",
                                        y0 = input_value, y1 = input_value,
                                        x0 = 0, x1 = 1,
                                        line = dict(
                                            color = "black",
                                            dash = "dot",
                                            width = 1
                                        ),
                                    )
                
                return [ploted_figure,[]]
        else:
            raise PreventUpdate

# Callback que aciona a sobreposição de voltas (por distância)
#@app.callback(

#)
#def sobreposicao_voltas():



if __name__ == '__main__':
    app.run_server(debug=True)
