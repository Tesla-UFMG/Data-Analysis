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
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.scripts.config.serve_locally = True

data = None
data_copy = None
converted_data = []
eixoY = []
eixoX = None

# LAYOUT DA PAGINA
app.layout = html.Div(children=[
    # Layout NavBar
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

    # Layout do Corpo da pagina
    html.Div(
        className="background",
        children=[
            # Layout do Fundo
            html.Div(
                className="overlay"
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
                                                            html.Button(
                                                                id='plot-button',
                                                                children='Plotar',
                                                                className="btn btn-primary btn-lg",
                                                                style={'background-color':'#4ed840', 'margin':'20px 0px 20px 0px', 'border':'solid 1px black', 'color':'black', 'font-weight': '350'}
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            # Conteudo do Grafico
                                            html.Div(
                                                id='Graph-content',
                                                children=[
                                            
                                                ]
                                            ),               
                                            dbc.Button(
                                                children="Opções avançadas",
                                                color="secondary",
                                                className="mr-1 hiden modal-open-button-style",
                                                id='modal-button'
                                            )
                                        ]
                                    )
                                ]
<<<<<<< HEAD
                            )#,
                            #Segundo Tab (Grafico Customizados)
=======
                            )
                            # Segundo Tab (Grafico Customizados)
>>>>>>> f5a9cb1f6788edeb50575f36d8db2157349598a2
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
<<<<<<< HEAD
                            #Terceiro Tab (Configuraçoes)
=======
                            # Terceiro Tab (Grafico Customizados)
>>>>>>> f5a9cb1f6788edeb50575f36d8db2157349598a2
                            # dcc.Tab(
                            #     label='Configurações',
                            #     value='tab-3',
                            #     children=[
                            #         dcc.Graph(
                            #             figure={
                            #                 'data': [
                            #                     {'x': [1, 2, 3], 'y': [2, 4, 3],
                            #                         'type': 'bar', 'name': 'SF'},
                            #                     {'x': [1, 2, 3], 'y': [5, 4, 3],
                            #                     'type': 'bar', 'name': u'Montréal'},
                            #                 ]
                            #             }
                            #         )
                            #     ]
<<<<<<< HEAD
                            #)
=======
                            # )
>>>>>>> f5a9cb1f6788edeb50575f36d8db2157349598a2
                        ]
                    )
                ]
            )
        ]
    ),
    # Layout botãp de Configurações avançadas
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
                    dbc.Button("Aplicar", id=" ", className="tesla-button")
                ],
                className="modal-header-and-footer"
            )
        ],
        id="modal-graph-config",
        scrollable=True
    )
])

<<<<<<< HEAD
#Dicionário(HASH) com todas as unidades dos dados conhecidos
=======
# Definição das unidades dos dados
>>>>>>> f5a9cb1f6788edeb50575f36d8db2157349598a2
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

<<<<<<< HEAD
#Dicionário(HASH) com todas as funções de conversão de unidades de cada dado 
=======
# Tratamento das unidades dos dados
>>>>>>> f5a9cb1f6788edeb50575f36d8db2157349598a2
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

<<<<<<< HEAD
#Lista com todos os possíveis dados a serem analisados no software
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

#Funçao de Media Movel
=======
# Funçao da média móvel
>>>>>>> f5a9cb1f6788edeb50575f36d8db2157349598a2
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

<<<<<<< HEAD
#Função que faz as conversões de unidade nos dados dos arquivos, aplicando cada função da tabela hash de conversão no seu respectivo dado
=======
# 
>>>>>>> f5a9cb1f6788edeb50575f36d8db2157349598a2
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

#Função utilizada nos callbacks de abrir/fechar os bootstrap collapses dentro do modal de config avançadas
def generate_toggle_callback():
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open
    return toggle_collapse

<<<<<<< HEAD
#Função utilizada nos callbacks de habilitar/desabilitar inputs numéricos do filtro passa-banda
def generate_input_passabanda_disable_callback():
    def disable_inputs_passabanda(checkbox):
        if( 'Passa-Banda' in checkbox):
            return [False,False]
        else:
            return [True,True]
    return disable_inputs_passabanda

#Função utilizada nos callbacks de habilitar/desabilitar inputs numéricos do filtro Savitzky-golay
def generate_input_savitzky_disable_callback():
    def disable_inputs_savitzky(checkbox):
        if( 'Filtro savitzky-golay' in checkbox):
            return [False,False]
        else:
            return [True,True]
    return disable_inputs_savitzky

#Função que cria o corpo HTML do modal. Cada Chamada dessa função retorna um Bootstrap collapse para o dado passado como parâmetro
def generate_element_modal_body(column_name):
    html_generated = [
        dbc.Button(
            children=[
                column_name,
                html.I(className='dropdown-triangle')
            ],
            color="secondary", 
            block=True,
            id=column_name + '-collapse-button',
            style={'margin':'5px 0'}
        ),
        dbc.Collapse(
            id= column_name + '-collapse',
            children=[
                html.H4(
                    children='Filtros Adicionais',
                    className='adv-config-subtitle',
                ),
                dcc.Checklist(
                    id=column_name + '-passa-banda-check',
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
                                id=column_name + '-passa-banda-input-inf',
                                label={'label':'limite inferior (Hz)'},
                                min=0,
                                max=10000,
                                value=1
                            )
                        ),
                        dbc.Col(
                            daq.NumericInput(
                                id=column_name + '-passa-banda-input-sup',
                                label={'label':'limite superior (Hz)'},
                                min=0,
                                max=10000,
                                value=100
                            )
                        )
                    ]
                ),
                dcc.Checklist(
                    id=column_name + '-savitzky-check',
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
                                id=column_name + '-savitzky-cut',
                                label={'label':'limite superior (Hz)'},
                                min=0,
                                max=10000,
                                value=100
                            )
                        ),
                        dbc.Col(
                            daq.NumericInput(
                                id=column_name + '-savitzky-rate',
                                label={'label':'Frequência de Nyquist'},
                                min=0,
                                max=10000,
                                value=120
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
    return html_generated

# Callback para o Upload de arquivos e montagem do dataFrame
=======
# Upload de arquivos e montagem do dataFrame
>>>>>>> f5a9cb1f6788edeb50575f36d8db2157349598a2
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
            legenda = [name.split()[0][0].upper() + name.split()[0][1:] for name in legenda.columns.values]

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
            

<<<<<<< HEAD
#Callback que habilita e desabilita o INPUT de média móvel
=======
# Habilita e desabilita o INPUT de média móvel
>>>>>>> f5a9cb1f6788edeb50575f36d8db2157349598a2
@app.callback(
    Output('media-movel-input','disabled'),
    [Input('filtros-checklist','value')]
)
def disable_media_movel_input(selected_filters):
    if ('Média Móvel' in selected_filters) or ('Filtro Mediana' in selected_filters):
        return False
    else:
        return True

<<<<<<< HEAD
#Callback do botão de plotagem de graficos
=======

# Plota os gráficos da análise geral
>>>>>>> f5a9cb1f6788edeb50575f36d8db2157349598a2
@app.callback(
    [Output('Graph-content','children'), Output('modal-button','style'), Output('modal-body','children')],
    [Input('plot-button','n_clicks')],
    [State('dropdown-analise-geral-Y','value'),State('dropdown-analise-geral-X','value'), State('filtros-checklist','value'), State('media-movel-input','value')]
)
def plot_graph_analise_geral(button_clicks, selected_columns_Y, selected_X, filters, filters_subseq):
    if button_clicks != 0 and button_clicks != None:
        global data_copy
        eixoY = selected_columns_Y.copy()
        eixoX = selected_X
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


        fig = make_subplots(rows=len(selected_columns_Y), cols=1, shared_xaxes=True, vertical_spacing=0.0)
        modal_body_content = []
        for cont, column_name in enumerate(selected_columns_Y):
            if (column_name in unidades_dados_hash):
                fig.add_trace(go.Scatter(y=data_copy[column_name], x=data_copy[selected_X], mode="lines", name=column_name, hovertemplate = "%{y} " + unidades_dados_hash[column_name]), row=cont+1, col=1)
            else:
                fig.add_trace(go.Scatter(y=data_copy[column_name], x=data_copy[selected_X], mode="lines", name=column_name, hovertemplate = "%{y}"), row=cont+1, col=1)               
            modal_body_content.extend(generate_element_modal_body(column_name))
        fig['layout'].update(height=120*len(selected_columns_Y)+100, margin={'t':50, 'b':50, 'l':100, 'r':100})

        
        return [
            dcc.Graph(
                figure=fig,
                id='figure-id',
                config={'autosizable' : False}
            ),
            {'display':'inline'},
            modal_body_content
        ]
    else:
        #TRATAR ERRO
        raise PreventUpdate

#Callback de abrir/fechar o modal de configurações avançadas
@app.callback(
    Output("modal-graph-config", "is_open"),
    [Input("modal-button", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("modal-graph-config", "is_open")],
)
def toggle_modal(open_button, close_button, is_open):
    if open_button or close_button:
        return not is_open
    return is_open

#Desativa as exceptions ligadas aos callbacks, permitindo a criação de callbacks envolvendo IDs que ainda não foram criados
app.config['suppress_callback_exceptions'] = True

#Laço para criar todos os callbacks possíveis, de forma a contornar a impossibilidade de criar callbacks dinâmicamente
for nome in data_name:
    app.callback(
        Output( nome + "-collapse" , "is_open"),
        [Input(nome + "-collapse-button", "n_clicks")],
        [State( nome + "-collapse" , "is_open")]
    ) (generate_toggle_callback())

    app.callback(
        [Output(nome + '-passa-banda-input-inf', 'disabled'), Output(nome + '-passa-banda-input-sup', 'disabled')],
        [Input(nome + '-passa-banda-check', 'value')]
    ) (generate_input_passabanda_disable_callback())

    app.callback(
        [Output(nome + '-savitzky-cut', 'disabled'), Output(nome + '-savitzky-rate', 'disabled')],
        [Input(nome + '-savitzky-check', 'value')]
    ) (generate_input_savitzky_disable_callback())

if __name__ == '__main__':
    app.run_server(debug=True)
