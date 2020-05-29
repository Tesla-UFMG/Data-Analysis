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
from modules.functions.somaLista import somaLista
from modules.callbacks.processingPOSGraphic import processingPOSGraphic
from modules.callbacks.lerArquivo import lerArquivo
from modules.callbacks.plotarGrafico import plotarGrafico
#------------------------------------------#

#---------- Instanciando Objetos ----------#
soma_Lista = somaLista()
Pos_Graphic = processingPOSGraphic()
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
                                                                    html.Div(
                                                                        className="divisão-content",
                                                                        style={
                                                                                    "display":"none"
                                                                            },
                                                                        id = "lap-division-show-or-hide",
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
                                                                            dbc.Checklist(
                                                                                options=[
                                                                                    {"label": "Sobrepor", "value": 1},
                                                                                ],
                                                                                id="sobreposicao-button",
                                                                                value=[],
                                                                                switch=True,
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
# Callback que muda a classe do botão de linhas horizontais, se pressionado
@app.callback(
    Output('add-line-button' , 'labelClassName'),
    [Input('add-line-button' , 'value')]
)
def change_button_class(value):

    if('Line' in value):
        return 'interations-button-pressed button-int'

    return 'interations-button button-int'



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
    return [
        leitura_de_arquivos.index_page_style,
        leitura_de_arquivos.main_page_style,
        leitura_de_arquivos.analise_Y_options,
        leitura_de_arquivos.analis_X_options,
        leitura_de_arquivos.upload_loading_children,
        leitura_de_arquivos.files_alert_open,
        leitura_de_arquivos.files_alert_children
    ]
    


# Callback do botão de plotagem de gráficos
@app.callback(
    [Output('apply-adv-changes-loading','children'),
     Output('Graph-content','children'),
     Output('modal-button','style'),
     Output('modal-body','children'),
     Output('plot-loading','children'),
     Output('config-ref-line', 'style'),
     Output('config-sobreposicao','style'),
     Output('lap-division-show-or-hide','style')],
    [Input('plot-button','n_clicks_timestamp'),
     Input('apply-adv-changes-button','n_clicks_timestamp'),
     Input('switches-input-divisao','value'),
     Input('radios-row','value'),
     Input('input-voltas-button-distancia', 'n_clicks'),
     Input('sobreposicao-button', 'value')],
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
    if button_plot != 0 or button_apply != 0:
        grafico.filtros(button_plot, button_apply, selected_columns_Y, selected_X, filters, filters_subseq, identificador,
                        bandpass_check, bandpass_inf, bandpass_sup, savitzky_check, savitzky_cut, savitzky_poly, leitura_de_arquivos.data)
                        
        grafico.plotar(div_switches_value, div_radios_value, set_div_dist, sobreposicao_button,
                       selected_columns_Y, selected_X, input_div_dist, tempo_voltas)
        if(1 in div_switches_value):
            grafico._overlap_lines(div_radios_value,selected_columns_Y,selected_X,input_div_dist, set_div_dist)
            grafico._overlap(sobreposicao_button,selected_columns_Y, input_div_dist)
    else:
        raise PreventUpdate
    return [grafico.changes_loading_children,
            grafico.graph_content_children,
            grafico.modal_button_style,
            grafico.modal_body_children,
            grafico.plot_loading_children ,
            grafico.ref_line_style ,
            grafico.configuracao_sobreposicao_style,
            grafico.lap_division_show_or_hide_style
        ]




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
def _display_reference_lines(clickData, checklist_horizontal, radios_value, n1, zoom_options, add_line, input_value):
    
    Pos_Graphic._display_reference_lines(clickData, checklist_horizontal, radios_value, n1, zoom_options, add_line, input_value, grafico.ploted_figure)
    
    return(Pos_Graphic.figure_id_figure,Pos_Graphic.add_line_button_value)

# Callback que habilita e desabilita as configurações de divisao de voltas
@app.callback(
    [Output('corpo-divisao-voltas','style'),
    Output('corpo-divisao-tempo','style'),
    Output('corpo-divisao-distancia','style'),
    Output('time-input', 'children')],
    [Input('switches-input-divisao','value'),
    Input('radios-row','value'),
    Input('divisão-voltas-tempo-input', 'value'),
     Input('input-voltas-button-tempo', 'n_clicks')],
    [State('time-input', 'children'),
     State({'type':'input-tempo','index':ALL}, 'value')]
)
def _lap_division(switch_value,radios_value,numero_voltas, n1, children, input_value):
    
    Pos_Graphic._able_lap_division(switch_value, radios_value,numero_voltas, n1, children, input_value)
    return (Pos_Graphic.lap_division_style,Pos_Graphic.time_division_style,Pos_Graphic.distance_division_style,Pos_Graphic.time_input_children)
    
if __name__ == '__main__':
    app.run_server(debug=True)
