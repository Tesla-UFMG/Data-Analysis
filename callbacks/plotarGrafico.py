#------------- Import Library -------------#
import numpy as np
from scipy import signal
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_core_components as dcc
import dash
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc
#------------------------------------------#

converted_data = []

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
    'Hodometro_T': 'm',
    'Dist': 'm'
}

# Função que faz as conversões de unidade nos dados dos arquivos, aplicando cada função da tabela hash de conversão no seu respectivo dado
def trataDados(selected_x, selected_y, data):

    selected_y_copy = selected_y.copy()

    if not(selected_x in selected_y_copy):
        selected_y_copy.append(selected_x)

    for coluna in selected_y_copy:
        if not(coluna in converted_data):
            if(coluna in tratamento_dados_hash):
                data[coluna] = tratamento_dados_hash[coluna](data[coluna])

            converted_data.append(coluna)
        
    return data

# Funçao de Media Movel
def smooth(y, box_pts):

    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')

    return y_smooth

# Corpo de opções avançadas de filtros
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
                                        label={'label': 'limite inferior (Hz)'},
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
                                        label={'label': 'limite superior (Hz)'},
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
                                {'label': 'Filtro savitzky-golay (Passa-baixas)','value': 'Filtro savitzky-golay'},
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
                                        label={'label': 'Tamanho da subsequência'},
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

# Filtro de Passa-Bandas
def element_bandpass_filter(data, lowcut, highcut, fs, order=5):
        
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    y = signal.lfilter(b, a, data)

    return y

# Divide lista
def Chunks(lista, distance, next_distance):
        yield lista[distance : next_distance]

class plotarGrafico():

    def __init__(self, ploted_figure):
        self.ploted_figure = ploted_figure
        self.data_copy = None
        self.lap_division_show_or_hide_style = {"display":"none"}
        
    def filtros(self, button_plot, button_apply, selected_columns_Y, selected_X, filters, filters_subseq, identificador,
                bandpass_check, bandpass_inf, bandpass_sup, savitzky_check, savitzky_cut, savitzky_poly, data):

        self.data_copy = data.copy()

        if int(button_plot) > int(button_apply):

            if filters_subseq % 2 == 0:
                filters_subseq += 1

            if ('Filtro Mediana' in filters) and ('Média Móvel' in filters):

                for column in selected_columns_Y:
                    self.data_copy[column] = smooth(signal.medfilt(self.data_copy[column], filters_subseq), filters_subseq)
            elif 'Média Móvel' in filters:

                for column in selected_columns_Y:
                    self.data_copy[column] = smooth(self.data_copy[column], filters_subseq)
            elif 'Filtro Mediana' in filters:

                for column in selected_columns_Y:
                    self.data_copy[column] = signal.medfilt(self.data_copy[column], np.array(filters_subseq))
        
        elif(int(button_plot) < int(button_apply)):

            for cont, id in enumerate(identificador):
                if('Passa-Banda' in bandpass_check[cont]):

                    self.data_copy[id['index']] = element_bandpass_filter(self.data_copy[id['index']], 
                                                                          bandpass_inf[cont],
                                                                          bandpass_sup[cont],
                                                                          fs=60
                                                                         )

                if('Filtro savitzky-golay' in savitzky_check[cont]):

                    window_length = savitzky_cut[cont]
                    if window_length % 2 == 0:
                        window_length += 1

                    self.data_copy[id['index']] = signal.savgol_filter(self.data_copy[id['index']],
                                                                       window_length = window_length,
                                                                       polyorder = savitzky_poly[cont]
                                                                      )

        trataDados(selected_X, selected_columns_Y, self.data_copy)

        return

    def plotar(self, selected_columns_Y, selected_X):

        modal_itens = []
        self.debuger = False

        self.ploted_figure = make_subplots(rows=len(selected_columns_Y),
                                           cols=1, 
                                           shared_xaxes=True, 
                                           vertical_spacing=0.0
                                          )

        for cont, column_name in enumerate(selected_columns_Y):
            if (column_name in unidades_dados_hash):
                self.ploted_figure.add_trace(go.Scatter(y=self.data_copy[column_name], 
                                                        x=self.data_copy[selected_X], 
                                                        mode="lines", 
                                                        name=column_name, 
                                                        hovertemplate = "%{y} " + unidades_dados_hash[column_name]
                                                       ), 
                                             row=cont+1, 
                                             col=1
                                            )
            else:
                self.ploted_figure.add_trace(go.Scatter(y=self.data_copy[column_name], 
                                                        x=self.data_copy[selected_X],
                                                        mode="lines", 
                                                        name=column_name, 
                                                        hovertemplate = "%{y}"
                                                       ), 
                                             row=cont+1, 
                                             col=1
                                            )

            modal_itens.extend(element_modal_body(column_name))

        self.ploted_figure['layout'].update(height=120*len(selected_columns_Y)+35, margin={'t':25, 'b':10, 'l':100, 'r':100}, uirevision='const')
        self.changes_loading_children = []
        self.graph_content_children = dcc.Graph(
                                            figure= self.ploted_figure,
                                            id='figure-id',
                                            config={'autosizable' : True}
                                        ),
        self.modal_button_style = {'display':'inline'}
        self.modal_body_children = modal_itens
        self.plot_loading_children = []
        self.ref_line_style = {'display':'block',
                               'border-left-style': 'outset',
                               'border-width': '2px',
                               'margin-left': '20px',
                               'margin-top': '15px'
                              }
        self.lap_division_show_or_hide_style = {'display':'block',
                                                'border-left-style': 'outset',
                                                'border-width': '2px',
                                                'margin-left': '20px'
                                               }
        self.configuracao_sobreposicao_style = dash.no_update

        return
    
    def _overlap_lines(self, div_radios_value, selected_columns_Y, selected_X, input_div_dist, set_div_dist):

        if('distancia' in div_radios_value):

            if set_div_dist:

                if (input_div_dist and input_div_dist != 0):

                    n_voltas = max(self.data_copy['Dist'])//input_div_dist

                    self.configuracao_sobreposicao_style = {'display':'block',
                                                            'border-left-style': 'outset',
                                                            'border-width': '2px',
                                                            'margin-left': '30px',
                                                            'margin-top': '15px'
                                                           }
                    self.ploted_figure.data = []

                    for cont, column_name in enumerate(selected_columns_Y):
                        for i in range(0, n_voltas):

                            lap_location =  input_div_dist * i
                            next_lap_location = input_div_dist * (i + 1)

                            while True:
                                if(not(np.where(self.data_copy['Dist'] == lap_location))[0]):
                                    lap_location = lap_location + 1
                                else:
                                    distance = (np.where(self.data_copy['Dist'] == lap_location)[0])[0]

                                    while True:
                                        if(not(np.where(self.data_copy['Dist'] == next_lap_location))[0]):
                                            next_lap_location = next_lap_location + 1
                                        else:
                                            next_distance = (np.where(self.data_copy['Dist'] == next_lap_location)[0])[0]
                                            break
                                    break

                            dist_use = list(Chunks(self.data_copy[selected_X], distance, next_distance))
                            data_use = list(Chunks(self.data_copy[column_name], distance, next_distance))
                
                            self.ploted_figure.add_trace(go.Scatter(x=dist_use[0], 
                                                                    y=data_use[0], 
                                                                    name="Volta {}".format(i+1)
                                                                   ),                                                
                                                         row=cont+1, 
                                                         col=1,
                                                        )

                        dist_use = list(Chunks(self.data_copy[selected_X], next_distance, max(self.data_copy[selected_X])))
                        data_use = list(Chunks(self.data_copy[column_name], next_distance, max(self.data_copy[selected_X])))                      
                        self.ploted_figure.add_trace(go.Scatter(x=dist_use[0], 
                                                                y=data_use[0], 
                                                                name="Volta {}".format(i+2 )
                                                               ),
                                                     row=cont+1, 
                                                     col=1, 
                                                    )

                    self.ploted_figure['layout'].update(height=120*len(selected_columns_Y)+35, margin={'t':25, 'b':10, 'l':100, 'r':100}, uirevision='const')
                    
                    for cont, column_name in enumerate(selected_columns_Y):
                        for z in range(1, n_voltas+1):
                            lap_location =  input_div_dist * z

                            while True:
                                if(not(np.where(self.data_copy['Dist'] == lap_location))[0]):
                                    lap_location = lap_location + 1
                                else:
                                    distance = (np.where(self.data_copy['Dist'] == lap_location)[0])[0]
                                    break

                            self.ploted_figure.add_trace(go.Scatter(y=[min(self.data_copy[column_name]), max(self.data_copy[column_name])],
                                                                    x=[self.data_copy[selected_X][distance], self.data_copy[selected_X][distance]],
                                                                    mode="lines", 
                                                                    line=go.scatter.Line(color="gray"), 
                                                                    showlegend=False
                                                                   ),
                                                         row=cont+1,
                                                         col=1
                                                        )
                
                self.ploted_figure['layout'].update(height=120*len(selected_columns_Y)+35, margin={'t':25, 'b':10, 'l':100, 'r':100}, uirevision='const')

    def _overlap(self, sobreposicao_button, selected_columns_Y, input_div_dist, selected_X):

        if (sobreposicao_button):

            n_voltas = max(self.data_copy['Dist'])//input_div_dist
            self.ploted_figure.data = []

            for cont, column_name in enumerate(selected_columns_Y):

                for i in range(0, n_voltas):
                    lap_location =  input_div_dist * i
                    next_lap_location = input_div_dist * (i + 1)

                    while True:
                        if(not(np.where(self.data_copy['Dist'] == lap_location))[0]):
                            lap_location = lap_location + 1
                        else:
                            distance = (np.where(self.data_copy['Dist'] == lap_location)[0])[0]

                            while True:
                                if(not(np.where(self.data_copy['Dist'] == next_lap_location))[0]):
                                    next_lap_location = next_lap_location + 1
                                else:
                                    next_distance = (np.where(self.data_copy['Dist'] == next_lap_location)[0])[0]
                                    break
                            break

                    dist_use = list(Chunks(self.data_copy[selected_X], distance, next_distance))
                    data_use = list(Chunks(self.data_copy[column_name], distance, next_distance))
                    offset = self.data_copy[selected_X][distance]
                    self.ploted_figure.add_trace(go.Scatter(x=(dist_use[0]-offset), 
                                                            y=data_use[0], 
                                                            name="Volta {}".format(i+1)
                                                           ),                                                
                                                 row=cont+1, 
                                                 col=1,
                                                )
                
                dist_use = list(Chunks(self.data_copy[selected_X], next_distance, max(self.data_copy[selected_X])))
                data_use = list(Chunks(self.data_copy[column_name], next_distance, max(self.data_copy[selected_X])))
                offset = self.data_copy[selected_X][next_distance]                      
                self.ploted_figure.add_trace(
                    go.Scatter(x=(dist_use[0]-offset), y=data_use[0], name="Volta {}".format(i+2 )),
                    row=cont+1, col=1,
                )

            self.ploted_figure['layout'].update(height=120*len(selected_columns_Y)+35, margin={'t':25, 'b':10, 'l':100, 'r':100}, uirevision='const')
        