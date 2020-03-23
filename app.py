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
converted_data = []

#LAYOUT DA PAGINA
app.layout = html.Div(children=[
    #Layout NavBar
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

    #Layout do Corpo da pagina
    html.Div(
        className="background",
        children=[
            #Layout do Fundo
            html.Div(
                className="overlay"
            ),

            #Layout da parte central, com o escrito e botao
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
                                    #Definiçao dos escritos
                                    html.Div(
                                        className="text",
                                        children=[
                                            #H1 = Fonte maior, Título
                                            html.H1(
                                                children='Análise de dados NK319'
                                            ),
                                            #H4 = Fonte menor, subtítulo
                                            html.H4(
                                                className="mb-5",
                                                children='Fórmula Tesla UFMG'
                                            ),
                                            #Layout botão
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

            #Segunda pagina, com graficos e configuraçoes
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
                            #Divisão da pagina em tres Tabs
                            dcc.Tab(
                                #Primeiro Tab (Analise Geral)
                                label='Análise Geral',
                                value='tab-1',
                                children=[
                                    #Conteudo do primeiro tab
                                    html.Div(
                                        className="form-plot-config",
                                        children=[
                                            #Título
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
                                            #Conteudo abaixo do titulo
                                            html.Div(
                                                className='container-form',
                                                children=[
                                                    #Configuraçao Eixo X
                                                    html.H4(
                                                        children='EIXO X',
                                                        className='form-label'
                                                    ),
                                                    #Dropdown para selecionar coluna de dados para o eixo X
                                                    dcc.Dropdown(
                                                        id='dropdown-analise-geral-X',
                                                        value='Timer',
                                                        className='',
                                                        multi=False,
                                                        placeholder='Selecione as grandezas do eixo X'
                                                    ),
                                                    #Configuraçao Eixo Y
                                                    html.H4(
                                                        children='EIXO Y',
                                                        className='form-label'
                                                    ),
                                                    html.Div(
                                                        className='row-drop',
                                                        children=[
                                                            #Dropdown para selecionar coluna de dados para o eixo Y
                                                            dcc.Dropdown(
                                                                id='dropdown-analise-geral-Y',
                                                                className='',
                                                                multi=True,
                                                                placeholder='Selecione as grandezas do eixo Y'
                                                            ),
                                                            #Configuraçao Filtros
                                                            html.H4(
                                                                children='Filtros',
                                                                className='form-label'
                                                            ),
                                                            #Checklist de filtros
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
                                                            #Selecionar valor de subsequencia do filtro
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
                                                            #Botão de Plotagem
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
                                            #Conteudo do Grafico
                                            html.Div(
                                                id='Graph-content',
                                                children=[
                                            
                                                ]
                                            ),               
                                            dbc.Button(
                                                children="Opções avançadas",
                                                color="secondary",
                                                className="mr-1 hiden modal-button-style",
                                                id='modal-button'
                                            )
                                        ]
                                    )
                                ]
<<<<<<< HEAD
                            )#,
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
                            # )
=======
                            ),
                            #Segundo Tab (Grafico Customizados)
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
                            #Terceiro Tab (Configuraçoes)
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
>>>>>>> 8273c057233bf5c50aa53ee9aff5c4b6e32dee37
                        ]
                    )
                ]
            )
        ]
    ),
    dbc.Modal(
        children = [
            dbc.ModalHeader("Configurações de plotagem avançadas"),
            dbc.ModalBody(
                children=[

                ]
            ),
            dbc.ModalFooter(
                dbc.Button("Fechar", id="close-modal", className="ml-auto")
            )
        ],
        id="modal-graph-config",
        size="sm",
    )
])

<<<<<<< HEAD
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

=======
#Funçao de Media Movel
>>>>>>> 8273c057233bf5c50aa53ee9aff5c4b6e32dee37
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

<<<<<<< HEAD
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


#Upload de arquivos e montagem do dataFrame
=======
#Funçao do Botao da pigina inicial
>>>>>>> 8273c057233bf5c50aa53ee9aff5c4b6e32dee37
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
#Habilita e desabilita o INPUT de média móvel
=======

#Funçao do botao de filtros
>>>>>>> 8273c057233bf5c50aa53ee9aff5c4b6e32dee37
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

#Plota os gráficos da análise geral
=======
#Funçao do botao de plotagem de graficos
>>>>>>> 8273c057233bf5c50aa53ee9aff5c4b6e32dee37
@app.callback(
    [Output('Graph-content','children'), Output('modal-button','style')],
    [Input('plot-button','n_clicks')],
    [State('dropdown-analise-geral-Y','value'),State('dropdown-analise-geral-X','value'), State('filtros-checklist','value'), State('media-movel-input','value')]
)
def plot_graph_analise_geral(button_clicks, selected_columns_Y, selected_X, filters, filters_subseq):
    if button_clicks != 0 and button_clicks != None:
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
        for cont, column_name in enumerate(selected_columns_Y):
            if (column_name in unidades_dados_hash):
                fig.add_trace(go.Scatter(y=data_copy[column_name], x=data_copy[selected_X], mode="lines", name=column_name, hovertemplate = "%{y} " + unidades_dados_hash[column_name]), row=cont+1, col=1)
            else:
                fig.add_trace(go.Scatter(y=data_copy[column_name], x=data_copy[selected_X], mode="lines", name=column_name, hovertemplate = "%{y}"), row=cont+1, col=1)               
        
        fig['layout'].update(height=120*len(selected_columns_Y)+100, margin={'t':50, 'b':50, 'l':100, 'r':100})
        return [
            dcc.Graph(
                figure=fig,
                id='figure-id',
                config={'autosizable' : False}
            ),
            {'display':'inline'}
        ]
    else:
        #TRATAR ERRO
        raise PreventUpdate


@app.callback(
    Output("modal-graph-config", "is_open"),
    [Input("modal-button", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("modal-graph-config", "is_open")],
)
def toggle_modal(open_button, close_button, is_open):
    if open_button or close_button:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(debug=True)
