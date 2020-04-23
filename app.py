# -*- coding: utf-8 -*-
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


#debug
import time

external_stylesheets = [dbc.themes.BOOTSTRAP]
external_scripts = ["https://cdn.plot.ly/plotly-1.2.0.min.js"]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.scripts.config.serve_locally = True

#--------------- Global var ---------------#
num_dados = None #Número de colunas dos arquivos de dados
data = None #Pandas Dataframe com os dados utilizados
data_copy = None #Cópia da variável data para a 
converted_data = [] #Armazena o nome das colunas que já tiveram seus dados tratados para evitar retrabalho
eixoY = None #Armazena as colunas que estão plotadas
ploted_figure = None #Armazena os dados da dcc.Graph() figure plotada
tempo_voltas = [0] #Armazena os valores dos tempos de cada volta (divisão de voltas)
empty_ploted_figure = None #Armazena a Figure do gráfico plotado sem nenhum linha de referência
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
                                                            # Configuraçao Filtros
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
                                            
                                            html.Div(
                                                id='Graph-content'
                                            ), 

                                            html.Div(
                                                id="graph-control-panel",
                                                className="interactive-graph-box",
                                                style={'display':'none'},
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
                                            html.Div(
                                                className="divisão-content",
                                                children=[
                                                    # Opção para selecionar divisão por distancia ou tempo
                                                    dbc.Checklist(
                                                        options=[
                                                            {"label": "Divisão de Voltas", "value": 1},
                                                        ],
                                                        id="switches-input",
                                                        value=[],
                                                        switch=True
                                                    ),
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
                                                            html.Div(
                                                                className="checklist-selected",
                                                                children=[
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
                                                                                max=100
                                                                            ),
                                                                            # Setando o valor de cada volta
                                                                            html.H4(
                                                                                children='Defina o tempo de cada volta (s.ms):',
                                                                                className='form-label',
                                                                                style={'margin-top':'8px', 'font-size':'1rem'}
                                                                            ),
                                                                            html.Div(
                                                                                id="time-input",
                                                                                children= []
                                                                            ),
                                                                            dbc.Button(
                                                                                children="Set",
                                                                                color="secondary",
                                                                                className="set-numero-voltas",
                                                                                id='input-voltas-button'
                                                                            ),
                                                                        ]
                                                                    ),
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
                                                                                    min=0
                                                                                 )
                                                                                ]
                                                                            ),
                                                                        ]
                                                                    ),
                                                                ]
                                                            ),
                                                        ]   
                                                    ),
                                                ]
                                            ),
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
            dbc.ModalHeader(
                children="Configurações avançadas de plotagem",
                className="modal-header-and-footer"
            ),
            dbc.ModalBody(
                id='modal-body'
            ),
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

# Dicionário(HASH) com todas as unidades dos dados conhecidos
unidades_dados_hash = {
    'Intensidade_Frenagem': '%',
    'Timer': 's',
    'V_motor_D':'RPM',
    'V_motor_E':'RPM',
    'Volante': 'graus',
    'Speed_LR': 'km/h',
    'Speed_RR': 'km/h',
    'Pedal': '%',
    'AccelX': 'G',
    'AccelY': 'G',
    'AccelZ': 'G',
    'GyroX': 'graus/s',
    'GyroY': 'graus/s',
    'GyroZ': 'graus/s',
    'Temp_pack0_1': 'ºC',
    'Temp_pack0_2': 'ºC',
    'Temp_pack1_1': 'ºC',
    'Temp_pack1_2': 'ºC',
    'Temp_pack2_1': 'ºC',
    'Temp_pack2_2': 'ºC',
    'Temp_pack3_1': 'ºC',
    'Temp_pack3_2': 'ºC',
    'Temp_pack4_1': 'ºC',
    'Temp_pack4_2': 'ºC',
    'Temp_pack5_1': 'ºC',
    'Temp_pack5_2': 'ºC',
    'Tempmediabb': 'ºC',
    'Tempmaxbb': 'ºC',
    'TempInv_D1': 'ºC',
    'TempInv_D2': 'ºC',
    'TempInv_E1': 'ºC',
    'TempInv_E2': 'ºC',
    'TempInt2': 'ºC',
    'TempInt': 'ºC',
    'Temp': 'ºC',
    'Tensao_GLV': 'mV',
    'Volt_BAT': 'mV',
    'Tensaototal': 'mV',
    'Hodometro_P': 'm',
    'Hodometro_T': 'm'
}

# Dicionário(HASH) com todas as funções de conversão de unidades de cada dado 
tratamento_dados_hash = {
    'Intensidade_Frenagem': lambda x: x/10,
    'Timer': lambda x: x/1000,
    'Speed_LR': lambda x: x/10,
    'Speed_RR': lambda x: x/10,
    'Pedal': lambda x: x/10,
    'AccelX': lambda x: x/1000,
    'AccelY': lambda x: x/1000,
    'AccelZ': lambda x: x/1000,
    'Volante': lambda x: (x-1030)/10
}

# Lista com todos os possíveis dados a serem analisados no software
data_name = [
    'ECU_Mode',
    'Intensidade_Frenagem',
    'Ecu_flag',
    'Timer',
    'Hodometro_P',
    'Hodometro_T',
    'Speed_LR',
    'Speed_RR',
    'V_motor_D',
    'V_motor_E',
    'Torque_LM',
    'Torque_RM',
    'Torque_ref_R',
    'Torque_ref_L',
    'Current_LM',
    'Current_RM',
    'Pedal',
    'Volante',
    'TempInv_D1',
    'TempInv_D2',
    'TempInv_E1',
    'TempInv_E2',
    'AccelX',
    'AccelY',
    'AccelZ',
    'GyroX',
    'GyroY',
    'GyroZ',
    'Temp',
    'Sensorpressao1',
    'Leitura_PotInt',
    'TempInt',
    'Ext1',
    'Ext2',
    'Ext13',
    'Ext23',
    'Ext22',
    'Leitura_PotInt2',
    'PotTD',
    'Sensorpressao2',
    'Leitura_PotInt3',
    'TempInt2',
    'Current_sensor1_baixa',
    'Current_sensor1_alta',
    'Current_sensor2',
    'Current_sensor3',
    'Tensaototal',
    'Tempmediabb',
    'Tempmaxbb',
    'Temp_pack0_1',
    'Temp_pack0_2',
    'Temp_pack1_1',
    'Temp_pack1_2',
    'Temp_pack2_1',
    'Temp_pack2_2',
    'Temp_pack3_1',
    'Temp_pack3_2',
    'Temp_pack4_1',
    'Temp_pack4_2',
    'Temp_pack5_1',
    'Temp_pack5_2',
    'Current_BAT',
    'Volt_BAT',
    'Tensao_GLV',
    'IRCan[0]',
    'IRCan[1]',
    'IRCan[2]',
    'IRCan[3]'
]

# Funçao de Media Movel
def smooth(y, box_pts):

    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')

    return y_smooth

# Função que faz as conversões de unidade nos dados dos arquivos, aplicando cada função da tabela hash de conversão no seu respectivo dado
def trataDados(selected_x, selected_y):

    global data
    global converted_data
    
    selected_y_copy = selected_y.copy()

    if not(selected_x in selected_y_copy):
        selected_y_copy.append(selected_x)

    for coluna in selected_y_copy:
        if not(coluna in converted_data):
            if(coluna in tratamento_dados_hash):
                data[coluna] = tratamento_dados_hash[coluna](data[coluna])

            converted_data.append(coluna)    

# Funções de filtro passa-banda
def butter_bandpass(lowcut, highcut, fs, order=5):
    
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')

    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):

    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.lfilter(b, a, data)
    
    return y

# Função utilizada nos callbacks de abrir/fechar os bootstrap collapses dentro do modal de config avançadas
def generate_toggle_callback():

    def toggle_collapse(n, is_open):

        if n:
            return not is_open
        
        return is_open
    
    return toggle_collapse

# Função utilizada nos callbacks de habilitar/desabilitar inputs numéricos do filtro passa-banda
def generate_input_passabanda_disable_callback():

    def disable_inputs_passabanda(checkbox):

        if( 'Passa-Banda' in checkbox):
            return [False,False]
        else:
            return [True,True]

    return disable_inputs_passabanda

# Função utilizada nos callbacks de habilitar/desabilitar inputs numéricos do filtro Savitzky-golay
def generate_input_savitzky_disable_callback():

    def disable_inputs_savitzky(checkbox):

        if( 'Filtro savitzky-golay' in checkbox):
            return [False,False]
        else:
            return [True,True]

    return disable_inputs_savitzky

# Função que cria o corpo HTML do modal. Cada Chamada dessa função retorna um Bootstrap collapse para o dado passado como parâmetro
def generate_element_modal_body(column_name):

    html_generated = [
        html.Div(
            id={
                'type': 'advconfig-data',
                'index': column_name
            },
            children = [
                dbc.Button(
                    children=[
                        column_name,
                        html.I(
                            className='dropdown-triangle'
                        )
                    ],
                    color="secondary", 
                    block=True,
                    id = {
                        'type':'advchanges-button-collapse',
                        'index': column_name
                    },
                    style={'margin':'5px 0'},
                    n_clicks=0
                ),
                dbc.Collapse(
                    id= {
                        'type':'advchanges-collapse',
                        'index': column_name
                    },
                    children=[
                        html.H4(
                            children='Filtros Adicionais',
                            className='adv-config-subtitle',
                        ),
                        dcc.Checklist(
                            id={
                                'type':'bandpass-checklist',
                                'index': column_name
                            },
                            options=[
                                {'label': 'Passa-Banda', 'value': 'Passa-Banda'},
                            ],
                            inputStyle = {'margin-right':'3px'},
                            labelStyle =  {'margin-right':'8px'},
                            value=[]
                        ),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    daq.NumericInput(
                                        id={
                                            'type':"bandpass-inf-limit",
                                            'index': column_name
                                        },
                                        label={'label':'limite inferior (Hz)'},
                                        min=1,
                                        max=15,
                                        value=1
                                    )
                                ),
                                dbc.Col(
                                    daq.NumericInput(
                                        id={
                                            'type':"bandpass-sup-limit",
                                            'index': column_name
                                        },
                                        label={'label':'limite superior (Hz)'},
                                        min=1,
                                        max=15,
                                        value=15
                                    )
                                )
                            ]
                        ),
                        dcc.Checklist(
                            id={
                                'type':"savitzky-checklist",
                                'index': column_name
                            },
                            options=[
                                {'label': 'Filtro savitzky-golay (Passa-baixas)', 'value': 'Filtro savitzky-golay'},
                            ],
                            inputStyle = {'margin-right':'3px'},
                            labelStyle =  {'margin-right':'8px'},
                            value=[]
                        ),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    daq.NumericInput(
                                        id={
                                            'type':"savitzky-cut",
                                            'index': column_name
                                        },
                                        label={'label':'Tamanho da subsequência'},
                                        min=0,
                                        max=20,
                                        value=5
                                    )
                                ),
                                dbc.Col(
                                    daq.NumericInput(
                                        id={
                                            'type':"savitzky-poly",
                                            'index': column_name
                                        },
                                        label={'label':'Grau polinomial'},
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

def soma_lista(lista):
    if len(lista) == 1:
        return lista[0]
    else:
        return lista[0] + soma_lista(lista[1:])

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

# Callback que habilita e desabilita as configurações de divisao de voltas
@app.callback(
    Output('corpo-divisao-voltas','style'),
    [Input('switches-input','value')]
)
def able_divisao_volta(switch_value):
    if (1 in switch_value):
        return {'display':'inline-block'}
    else:
        return {'display':'none'}

# Callback que habilita e desabilita as configurações de setar distancia ou tempo
@app.callback(
    [Output('corpo-divisao-tempo','style'),
     Output('corpo-divisao-distancia','style')],
    [Input('radios-row','value')]
)
def able_tempo_or_distancia(radios_value):
    
    if ('distancia' in radios_value):
        return [{'display':'none'}, {'display':'inline-block'}]
    elif ('tempo' in radios_value):
        return [{'display':'inline-block'}, {'display':'none'}]
    else: 
        raise PreventUpdate

# Callback que define a quantidade de inputs para o tempo das voltas e guarda os tempos no array
@app.callback(
    Output('time-input', 'children'),
    [Input('divisão-voltas-tempo-input', 'value'),
     Input('input-voltas-button', 'n_clicks')],
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

    if n1:
        tempo_voltas = input_value

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

    global data
    global num_dados

    if list_of_contents is not None:
        if ('legenda.txt' in list_of_names):
            if len(list_of_names) >= 2:
                files = dict(zip(list_of_names, list_of_contents))
                legenda = pd.read_csv(io.StringIO(base64.b64decode(files['legenda.txt'].split(',')[1]).decode('utf-8')))
                legenda = [name.split()[0][0].upper() + name.split()[0][1:] for name in legenda.columns.values]

                try:
                    for nome_do_arquivo in files:
                        if(nome_do_arquivo != 'legenda.txt'):
                            data = pd.read_csv(io.StringIO(base64.b64decode(files[nome_do_arquivo].split(',')[1]).decode('utf-8')), delimiter='\t', names=legenda, index_col=False)
                except:
                    return [dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, True, "Os arquivos de dados não são do tipo .txt"]
                
                options = []
                num_dados = len(legenda)
                
                for cont, column_name in enumerate(legenda):
                    options.append( {'label' : column_name, 'value' : column_name} )

                return [{'display': 'none'}, {'display':'inline'}, options, options, [], dash.no_update, dash.no_update]
            else:
                return [dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, True, "É necessário o upload de um arquivo de dados do tipo .txt"]    
        else:
            return [dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, True, "É necessário o upload de um arquivo chamado legenda.txt"]
    else:
        raise PreventUpdate
        
# Callback do botão de plotagem de graficos
@app.callback(
    [Output('apply-adv-changes-loading','children'),
     Output('Graph-content','children'),
     Output('modal-button','style'),
     Output('modal-body','children'),
     Output('plot-loading','children'),
     Output('graph-control-panel', 'style')],
    [Input('plot-button','n_clicks_timestamp'),
     Input('apply-adv-changes-button','n_clicks_timestamp')],
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
     State({'type':'savitzky-poly', 'index': ALL}, 'value')]
)
def plot_graph_analise_geral(button_plot, button_apply, selected_columns_Y, selected_X, filters, filters_subseq, identificador, bandpass_check, bandpass_inf, bandpass_sup , savitzky_check, savitzky_cut, savitzky_poly):
    
    global data_copy
    global empty_ploted_figure
    global ploted_figure
    global eixoY
    global tempo_voltas

    if button_plot != 0 or button_apply != 0:
        modal_itens = []

        if int(button_plot) > int(button_apply):
            eixoY = selected_columns_Y
            trataDados(selected_X, selected_columns_Y)
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

                    
        elif(int(button_plot) < int(button_apply)):
            for cont, id in enumerate(identificador):
                if('Passa-Banda' in bandpass_check[cont]):
                    data_copy[id['index']] = butter_bandpass_filter(data_copy[id['index']], 
                                                                    bandpass_inf[cont],
                                                                    bandpass_sup[cont],
                                                                    fs=60
                                                                   )
                if('Filtro savitzky-golay' in savitzky_check[cont]):
                    window_length = savitzky_cut[cont]
                    if window_length % 2 == 0:
                        window_length += 1

                    data_copy[id['index']] = signal.savgol_filter(data_copy[id['index']],
                                                                  window_length=window_length,
                                                                  polyorder=savitzky_poly[cont]
                                                                 )

        fig = make_subplots(rows=len(selected_columns_Y),
                            cols=1, 
                            shared_xaxes=True, 
                            vertical_spacing=0.0
                           )
        for cont, column_name in enumerate(selected_columns_Y):
            if (column_name in unidades_dados_hash):
                fig.add_trace(go.Scatter(y=data_copy[column_name], 
                                         x=data_copy[selected_X], 
                                         mode="lines", 
                                         name=column_name, 
                                         hovertemplate = "%{y} " + unidades_dados_hash[column_name]
                                        ), 
                              row=cont+1, 
                              col=1
                             )
            else:
                fig.add_trace(go.Scatter(y=data_copy[column_name], 
                                         x=data_copy[selected_X],
                                         mode="lines", 
                                         name=column_name, 
                                         hovertemplate = "%{y}"
                                        ), 
                              row=cont+1, 
                              col=1
                             )
            modal_itens.extend( generate_element_modal_body(column_name) )

        tempo_div_voltas = np.zeros(len(tempo_voltas))

        for i in range(0, len(tempo_voltas)-1):
            tempo_div_voltas[i] = soma_lista(tempo_voltas[:i+1])

        tempo_div_voltas[len(tempo_voltas)-1] = 0
        tempo_div_voltas[len(tempo_voltas)-1] = soma_lista(tempo_voltas)

        # Acresenta traços de divisão de voltas
        for cont, column_name in enumerate(selected_columns_Y):
            for z in tempo_div_voltas:
                fig.add_trace(go.Scatter(y=[min(data_copy[column_name]), max(data_copy[column_name])],   # linha reta do valor minimo ao maximo do dado 
                                         x=[z, z],                                                       # array com os valores dos tempos das voltas 
                                         mode="lines", 
                                         line=go.scatter.Line(color="gray"), 
                                         showlegend=False
                                        ),
                              row=cont+1,
                              col=1
                             )

        fig['layout'].update(height=120*len(selected_columns_Y)+35, margin={'t':25, 'b':10, 'l':100, 'r':100}, uirevision='const')

        ploted_figure = empty_ploted_figure = fig

        return [
            [],
            dcc.Graph(
                figure=fig,
                id='figure-id',
                config={'autosizable' : False}
            ),
            {'display':'inline'},
            modal_itens,
            [],
            {'display':'flex'}
        ]

    else:
        #TRATAR ERRO
        raise PreventUpdate

@app.callback(
    Output('add-line-button' , 'labelClassName'),
    [Input('add-line-button' , 'value')]
)
def change_button_class(value):
    if('Line' in value):
        return 'interations-button-pressed button-int'
    return 'interations-button button-int'
    
@app.callback (
    [Output("figure-id","figure"),
     Output("add-line-button", "value")],
    [Input("figure-id","clickData")],
    [State("figure-id","relayoutData"),
     State("add-line-button", "value")]
)
def display_vertical_line(clickData, zoom_options, add_line):
    if clickData is not None:
        global ploted_figure
        if("Line" in add_line):
            #HORIZONTAL
            yref = "y"
            curveNumber = clickData['points'][0]['curveNumber']
            if(  curveNumber != 0 ):
                yref = yref + str(curveNumber+1)
            
            ploted_figure.add_shape(type="line",
                                    xref="paper",
                                    yref=yref,
                                    y0 = clickData['points'][0]['y'],
                                    y1 = clickData['points'][0]['y'],
                                    x0 = 0,
                                    x1 = 1,
                                    line = dict(
                                        color = "black",
                                        dash = "dot",
                                        width = 1
                                    ),
                                   )
            return [ploted_figure,[]]
        else:
            #VERTICAL
            last_figure = go.Figure(ploted_figure)
            last_figure.add_shape(type = "line",
                                  yref = "paper",
                                  x0 = clickData['points'][0]['x'],
                                  x1 = clickData['points'][0]['x'],
                                  y0 = 0,
                                  y1 = 1,
                                  line = dict(
                                    color = "#505050",
                                    width = 1.5
                                  )
                                 )
            return [last_figure, dash.no_update]
    else:
        raise PreventUpdate



if __name__ == '__main__':
    app.run_server(debug=True)
