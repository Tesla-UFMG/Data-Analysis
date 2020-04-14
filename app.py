# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import pandas as pd
import numpy as np
from scipy import signal
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
import io
import base64
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


#debug
import time

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.scripts.config.serve_locally = True


num_max_dados = 80
num_dados = 0
is_loaded = False
data = None
data_copy = None
all_data_name = {}
converted_data = []
show_modal_items = [ {'display':'none'} for _ in range(num_max_dados) ]

state_for_apply_callback = [State('dropdown-analise-geral-Y','value'),State('dropdown-analise-geral-X','value'), State('filtros-checklist','value'), State('media-movel-input','value')]
output_for_apply_callback = [Output('apply-adv-changes-loading','children'), Output('Graph-content','children'), Output('modal-button','style')]
 
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
                                                                children='Plotar',
                                                                className="btn btn-primary btn-lg",
                                                                style={'background-color':'#4ed840', 'margin':'20px 0px 20px 0px', 'border':'solid 1px black', 'color':'black', 'font-weight': '350'},
                                                                n_clicks_timestamp=0
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            # Conteudo do Grafico
                                            dbc.Spinner(
                                                spinner_style={'margin':'10rem auto'},
                                                children=[
                                                    html.Div(
                                                        id='Graph-content'
                                                    ), 
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
                                                        switch=True,
                                                    ),
                                                    html.Div(
                                                        className="divisao-sub-content",
                                                        #style={'display':'none'},
                                                        children=[
                                                            # Checklist de Distancia ou Tempo
                                                            dbc.RadioItems(
                                                                id="radios-row",
                                                                options=[
                                                                    {"label": "Distância", "value": "distancia"},
                                                                    {"label": "Tempo", "value": "tempo"},
                                                                ],
                                                            ),
                                                            html.Div(
                                                                className="checklist-selected",
                                                                children=[
                                                                    html.Div(
                                                                        className="if-tempo-selected",
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
                                                                                children='Defina o tempo de cada volta:',
                                                                                className='form-label',
                                                                                style={'margin-top':'8px', 'font-size':'1rem'}
                                                                            ),
                                                                            dbc.Input(
                                                                                id="time-input", 
                                                                                placeholder="Tempo em segundos (s.ms)", 
                                                                                type="number",
                                                                                min=1
                                                                            ),
                                                                        ]
                                                                    ),
                                                                    html.Div(
                                                                        className="if-dist-selected",
                                                                        children=[
                                                                            # Selecionar a distância das voltas
                                                                            html.H4(
                                                                                children='Distância das Voltas:',
                                                                                className='form-label',
                                                                                style={'margin-top':'8px', 'font-size':'1rem'}
                                                                            ),
                                                                            dbc.Input(
                                                                                id="dist-input", 
                                                                                placeholder="Distância em metros", 
                                                                                type="number",
                                                                                min=1
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
                        children=[
                            dbc.Button("Aplicar", id="apply-adv-changes-button", className="tesla-button", n_clicks_timestamp=0),
                            html.Div(
                                id="apply-adv-changes-loading"
                            )
                        ],
                        size="sm",
                        spinner_style={'margin': '0 37px'},
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
def generate_element_modal_body(num, column_name):

    html_generated = [
        html.Div(
            id= num + '-modal-element',
            style = {'display': 'none'},
            children = [
                dbc.Button(
                    children=[
                        column_name,
                        html.I(className='dropdown-triangle')
                    ],
                    color="secondary", 
                    block=True,
                    id=num + '-collapse-button',
                    style={'margin':'5px 0'}
                ),
                dbc.Collapse(
                    id= num + '-collapse',
                    children=[
                        html.H4(
                            children='Filtros Adicionais',
                            className='adv-config-subtitle',
                        ),
                        dcc.Checklist(
                            id=num + '-passa-banda-check',
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
                                        id=num + '-passa-banda-input-inf',
                                        label={'label':'limite inferior (Hz)'},
                                        min=1,
                                        max=15,
                                        value=1
                                    )
                                ),
                                dbc.Col(
                                    daq.NumericInput(
                                        id=num + '-passa-banda-input-sup',
                                        label={'label':'limite superior (Hz)'},
                                        min=1,
                                        max=15,
                                        value=15
                                    )
                                )
                            ]
                        ),
                        dcc.Checklist(
                            id=num + '-savitzky-check',
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
                                        id=num + '-savitzky-cut',
                                        label={'label':'Tamanho da subsequência'},
                                        min=0,
                                        max=20,
                                        value=5
                                    )
                                ),
                                dbc.Col(
                                    daq.NumericInput(
                                        id=num + '-savitzky-rate',
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


# Desativa as exceptions ligadas aos callbacks, permitindo a criação de callbacks envolvendo IDs que ainda não foram criados
app.config['suppress_callback_exceptions'] = True

# Laço para criar todos os callbacks possíveis, de forma a contornar a impossibilidade de criar callbacks dinâmicamente
for num in range(num_max_dados):
    
    num = str(num)
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name ='toggle_collapse'
        ),
        output=Output( num + "-collapse" , "is_open"),
        inputs=[Input(num + "-collapse-button", "n_clicks")],
        state=[State( num + "-collapse" , "is_open")]
    )
 
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name ='disable_inputs_passabanda'
        ),
        output=[Output(num + '-passa-banda-input-inf', 'disabled'), Output(num + '-passa-banda-input-sup', 'disabled')],
        inputs=[Input(num + '-passa-banda-check', 'value')]
    )

    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name ='disable_inputs_savitzky'
        ),
        output = [Output(num + '-savitzky-cut', 'disabled'), Output(num + '-savitzky-rate', 'disabled')],
        inputs= [Input(num + '-savitzky-check', 'value')]
    )

    state_for_apply_callback.extend([
        State(str(num) + '-passa-banda-check', 'value'),
        State(str(num) + '-passa-banda-input-inf', 'value'),
        State(str(num) + '-passa-banda-input-sup', 'value'),
        State(str(num) + '-savitzky-check', 'value'),
        State(str(num) + '-savitzky-cut', 'value'),
        State(str(num) + '-savitzky-rate', 'value')
    ])


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

# Callback que habilita e desabilita as configurações de setar volta ou distancia
@app.callback(
    [Output('divisao-sub-content','display')],
    [Input('switches-input','value')]
)
def able_divisao_volta(switch_value):
    
    if (switch_value != 1):
        return 'none'
    else:
        return 'inline-block'

# Callback para o Upload de arquivos, montagem do dataFrame e do html do modal
@app.callback(
    [Output('index-page', 'style'), 
     Output('main-page', 'style'),
     Output('dropdown-analise-geral-Y', 'options'),
     Output('dropdown-analise-geral-X', 'options'), 
     Output('modal-body','children'), 
     Output('upload-data-loading','children'), 
     Output('upload-files-alert','is_open'), 
     Output('upload-files-alert', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def hide_index_and_read_file(list_of_contents, list_of_names):

    global data
    global num_dados
    global output_for_apply_callback
    global is_loaded

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
                    return [dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, True, "Os arquivos de dados não são do tipo .txt"]
                
                options = []
                modalbody_content = []
                num_dados = len(legenda)
                
                for cont, column_name in enumerate(legenda):
                
                    options.append( {'label' : column_name, 'value' : column_name} )
                    all_data_name[column_name] = cont
                    modalbody_content.extend(generate_element_modal_body(str(cont), column_name))

                    if not is_loaded:
                        output_for_apply_callback.extend([
                            Output(str(cont) + '-modal-element', 'style')
                        ])

                for cont in range(num_dados,num_max_dados):
                    modalbody_content.extend(generate_element_modal_body(str(cont), 'extra'))
                
                is_loaded = True
                return [{'display': 'none'}, {'display':'inline'}, options, options, modalbody_content, [], dash.no_update, dash.no_update]
            else:
                return [dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, True, "É necessário o upload de um arquivo de dados do tipo .txt"]    
        else:
            return [dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, True, "É necessário o upload de um arquivo chamado legenda.txt"]
    else:
        raise PreventUpdate
        
# Callback do botão de plotagem de graficos
@app.callback(
    output_for_apply_callback,
    [Input('plot-button','n_clicks_timestamp'), Input('apply-adv-changes-button','n_clicks_timestamp')],
    state_for_apply_callback
)
def plot_graph_analise_geral(button_plot, button_apply, selected_columns_Y, selected_X, filters, filters_subseq, *args):
    
    global data_copy
    global show_modal_items
    
    if button_plot != 0 or button_apply != 0:

        if int(button_plot) > int(button_apply):

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

            for column in selected_columns_Y:
                data_index = all_data_name[column] * 6
                
                if( 'Passa-Banda' in args[data_index] ):
                    data_copy[column] = butter_bandpass_filter(data_copy[column], 
                                                               args[data_index+1],
                                                               args[data_index+2],
                                                               fs=60
                                                              )

                if( 'Filtro savitzky-golay' in args[data_index+3]):
                    
                    window_length = args[data_index+4]

                    if window_length % 2 == 0:
                        window_length += 1

                    data_copy[column] = signal.savgol_filter(data_copy[column],
                                                             window_length=window_length,
                                                             polyorder=args[data_index+5]
                                                            )

        show_modal_items_copy = show_modal_items[:num_dados]
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

            show_modal_items_copy[all_data_name[column_name]] = {'display':'block'}

        # tempo_voltas = [50, 100, 150]

        # Acresenta traços de divisão de voltas
        for cont, column_name in enumerate(selected_columns_Y):
            for z in range(50, 300, 50):
                fig.add_trace(go.Scatter(y=[min(data_copy[column_name]), max(data_copy[column_name])],   # linha reta do valor minimo ao maximo do dado 
                                         x=[z, z],                                                       # array com os valores dos tempos das voltas 
                                         mode="lines", 
                                         line=go.scatter.Line(color="gray"), 
                                         showlegend=False
                                        ),
                              row=cont+1,
                              col=1
                             )
                        
        fig['layout'].update(height=120*len(selected_columns_Y)+100, margin={'t':50, 'b':50, 'l':100, 'r':100})

        retorno = [
            [],
            dcc.Graph(
                figure=fig,
                id='figure-id',
                config={'autosizable' : False}
            ),
            {'display':'inline'}
        ]
        retorno.extend(show_modal_items_copy)
        
        return retorno
    else:
        #TRATAR ERRO
        raise PreventUpdate



if __name__ == '__main__':
    app.run_server(debug=True)
