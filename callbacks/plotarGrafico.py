#------------- Import Library -------------#
import numpy as np
import pandas as pd
from scipy import signal
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_core_components as dcc
import dash
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc
#------------------------------------------#

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
def _trata_dados(selected_x, selected_y, data):
    selected_y_copy = selected_y.copy()

    if not(selected_x in selected_y_copy):
        selected_y_copy.append(selected_x)

    for coluna in selected_y_copy:
        if(coluna in tratamento_dados_hash):
            data[coluna] = tratamento_dados_hash[coluna](data[coluna])
        
    return data
# Funçao de Media Movel
def _smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')

    return y_smooth

# Corpo de opções avançadas de filtros
def _element_modal_body(column_name,file_name):
        
    html_generated = [
        html.Div(
            id={
                'type': 'advconfig-data',
                'index': column_name + "\t" +file_name
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
                        'index': column_name + "\t" +file_name
                    },
                    style={'margin': '5px 0'},
                    n_clicks=0
                ),
                dbc.Collapse(
                    id={
                        'type': 'advchanges-collapse',
                        'index': column_name + "\t" +file_name
                    },
                    children=[
                        html.H4(
                            children='Filtros Adicionais',
                            className='adv-config-subtitle',
                        ),
                        dcc.Checklist(
                            id={
                                'type': 'bandpass-checklist',
                                'index': column_name + "\t" +file_name
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
                                            'index': column_name + "\t" +file_name
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
                                            'index': column_name + "\t" +file_name
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
                                'index': column_name + "\t" +file_name
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
                                            'index': column_name + "\t" +file_name
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
                                            'index': column_name + "\t" +file_name
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
def _element_bandpass_filter(data, lowcut, highcut, fs, order=5):
        
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    y = signal.lfilter(b, a, data)

    return y

# Divide lista
def _chunks(lista, distance, next_distance):
    
    yield lista[distance : next_distance]

def _chunks_overlap(lista, n):

    for i in range(0, len(lista), n):
        yield lista[i:i + n]

# Destaca as voltas dividas, colorindo
def _highlight(Y_axis, selected_X, n_voltas, input_div_dist, ploted_figure, data_copy, file_name, file, number_of_graphs):
        if(Y_axis[file_name]):
            cont = file
            if(file == 0):
                ploted_figure.data = []           
            for column_name in Y_axis[file_name]:
                file = file + 1
                for i in range(0, n_voltas):
                    lap_location =  input_div_dist * i
                    next_lap_location = input_div_dist * (i + 1)
                    while True:
                        if(not(np.where(data_copy[file_name]['Dist'] == lap_location))[0]):
                            lap_location = lap_location + 1
                        else:
                            distance = (np.where(data_copy[file_name]['Dist'] == lap_location)[0])[0]
                            while True:
                                if(not(np.where( data_copy[file_name]['Dist'] == next_lap_location))[0]):
                                    next_lap_location = next_lap_location + 1
                                else:
                                    next_distance = (np.where( data_copy[file_name]['Dist'] == next_lap_location)[0])[0]
                                    break
                            break
                    dist_use = list(_chunks( data_copy[file_name][selected_X], distance, next_distance))
                    data_use = list(_chunks( data_copy[file_name][column_name], distance, next_distance))
                    ploted_figure.add_trace(go.Scatter(x=dist_use[0], 
                                                    y=data_use[0], 
                                                    name="Volta {}".format(i+1)
                                                    ),                                                
                                            row=file, 
                                            col=1,
                                        )
                dist_use = list(_chunks( data_copy[file_name][selected_X], next_distance, len( data_copy[file_name][selected_X])))
                data_use = list(_chunks( data_copy[file_name][column_name], next_distance, len( data_copy[file_name][selected_X])))
                ploted_figure.add_trace(go.Scatter(x=dist_use[0], 
                                                y=data_use[0], 
                                                name="Volta {}".format(i+2)
                                                ),                                                
                                        row=file, 
                                        col=1,
                                    )
            ploted_figure['layout'].update(height=120*number_of_graphs+35, margin={'t':25, 'b':10, 'l':100, 'r':100}, uirevision='const') 
            for column_name in Y_axis[file_name]:
                cont = cont + 1
                for z in range(1, n_voltas+1):
                    lap_location =  input_div_dist * z
                    while True:
                        if(not(np.where(data_copy[file_name]['Dist'] == lap_location))[0]):
                            lap_location = lap_location + 1
                        else:
                            distance = (np.where(data_copy[file_name]['Dist'] == lap_location)[0])[0]
                            break
                    ploted_figure.add_trace(go.Scatter(y=[min(data_copy[file_name][column_name]), max(data_copy[file_name][column_name])],
                                                                            x=[data_copy[file_name][selected_X][distance], data_copy[file_name][selected_X][distance]],
                                                                            mode="lines", 
                                                                            line=go.scatter.Line(color="gray"), 
                                                                            showlegend=False
                                                                            ),
                                                                row=cont,
                                                                col=1
                                                               )
        return file 
        
class plotarGrafico():
    def __init__(self, ploted_figure):
        self.ploted_figure = ploted_figure
        self.data_copy = {}
        self.lap_division_show_or_hide_style = {"display":"none"}
        self.n_voltas = None
        self.number_of_graphs = 0
        self.show_quick_report_style = {"display":"none"}
        
    def _filters(self, button_plot, button_apply, Y_axis, selected_X, filters, filters_subseq, identificador,
                bandpass_check, bandpass_inf, bandpass_sup, savitzky_check, savitzky_cut, savitzky_poly, dataframe_colection, files_names):
        for file_name in files_names:
            self.data_copy[file_name] = dataframe_colection[file_name].copy()
        for fn in files_names:
            if int(button_plot) > int(button_apply):
                if(Y_axis[fn]):
                    if filters_subseq % 2 == 0:
                        filters_subseq += 1                    
                    if ('Filtro Mediana' in filters) and ('Média Móvel' in filters):
                        for file_name in files_names:
                            if(Y_axis[file_name]):
                                for column in Y_axis[file_name]:
                                    self.data_copy[file_name][column] = _smooth(signal.medfilt(self.data_copy[file_name][column], filters_subseq), filters_subseq)
                    elif 'Média Móvel' in filters:
                        for file_name in files_names:
                            if(Y_axis[file_name]):
                                for column in Y_axis[file_name]:
                                    self.data_copy[file_name][column] = _smooth(self.data_copy[file_name][column], filters_subseq)
                    elif 'Filtro Mediana' in filters:
                        for file_name in files_names:
                            if(Y_axis[file_name]):
                                for column in Y_axis[file_name]:
                                    self.data_copy[file_name][column] = signal.medfilt(self.data_copy[file_name][column], np.array(filters_subseq))
                
            elif(int(button_plot) < int(button_apply)):
                    for cont, id in enumerate(identificador):
                        adv_filter = id["index"].split("\t")
                        if('Passa-Banda' in bandpass_check[cont]):
                            self.data_copy[adv_filter[1]][adv_filter[0]] = _element_bandpass_filter(self.data_copy[adv_filter[1]][adv_filter[0]], 
                                                                                bandpass_inf[cont],
                                                                                bandpass_sup[cont],
                                                                                fs=60
                                                                                )

                        if('Filtro savitzky-golay' in savitzky_check[cont]):
                            window_length = savitzky_cut[cont]
                            if window_length % 2 == 0:
                                window_length += 1

                            self.data_copy[adv_filter[1]][adv_filter[0]] = signal.savgol_filter(self.data_copy[adv_filter[1]][adv_filter[0]],
                                                                            window_length = window_length,
                                                                            polyorder = savitzky_poly[cont]
                                                                            )            
            if(Y_axis[fn]):   
                self.data_copy[fn] = _trata_dados(selected_X, Y_axis[fn], self.data_copy[fn])
            
        return

    def _plot(self, Y_axis, selected_X, files_names):

        modal_itens = []
        self.debuger = False
        self.number_of_graphs = 0
        for file_name in files_names:
            if(Y_axis[file_name]):
                for y in Y_axis[file_name]:
                    if(y):
                        self.number_of_graphs = self.number_of_graphs + 1 
        self.ploted_figure = make_subplots(rows=self.number_of_graphs,
                                            cols=1, 
                                            shared_xaxes=True, 
                                            vertical_spacing=0.0
                                            )
        cont = 0
        for file_name in files_names:
            if(Y_axis[file_name]):
                for column_name in Y_axis[file_name]:
                    cont = cont + 1
                    if (column_name in unidades_dados_hash):
                        self.ploted_figure.add_trace(go.Scatter(y=self.data_copy[file_name][column_name], 
                                                                x=self.data_copy[file_name][selected_X], 
                                                                mode="lines", 
                                                                name=column_name + " " + file_name, 
                                                                hovertemplate = "%{y} " + unidades_dados_hash[column_name],
                                                            ), 
                                                    row=cont, 
                                                    col=1
                                                    )
                    else:
                        self.ploted_figure.add_trace(go.Scatter(y=self.data_copy[file_name][column_name], 
                                                                x=self.data_copy[file_name][selected_X],
                                                                mode="lines", 
                                                                name=column_name + " " + file_name, 
                                                                hovertemplate = "%{y}",
                                                            ), 
                                                    row=cont, 
                                                    col=1
                                                    )
                    modal_itens.extend(_element_modal_body(column_name,file_name))
                self.ploted_figure['layout'].update(height=self.number_of_graphs*120+35, margin={'t':25, 'b':10, 'l':100, 'r':100}, uirevision='const')        
        self.changes_loading_children = []
        self.graph_content_children = dcc.Graph(
                                            figure= self.ploted_figure,
                                            id='figure-id',
                                            config={'autosizable' : True}
                                        )                                          
        self.modal_button_style = {'display':'inline'}
        self.modal_body_children = modal_itens
        self.plot_loading_children = []
        self.ref_line_style = {'display':'block',
                               'border-left-style': 'outset',
                               'border-width': '2px',
                               'margin-left': '20px',
                               'margin-top': '15px',
                               'padding': '0.01em 16px 0.01em 10px'
                              }
        self.lap_division_show_or_hide_style = {'display':'block',
                                                'border-left-style': 'outset',
                                                'border-width': '2px',
                                                'margin-left': '20px',
                                                'margin-top': '15px'
                                               }
        self.configuracao_sobreposicao_style = dash.no_update

        return
    
    def _overlap_lines(self, div_radios_value, Y_axis, selected_X, input_div_dist, set_div_dist, lap_highlight, tempo_voltas, files_names):

        if('distancia' in div_radios_value):
            if set_div_dist: 
                cont = 0
                file = 0
                for file_name in files_names:
                    self.configuracao_sobreposicao_style = {'display':'block',
                                                            'border-left-style': 'outset',
                                                            'border-width': '2px',
                                                            'margin-left': '10px',
                                                            'margin-top': '15px',
                                                            'padding': '0.01em 16px'
                                                            }
                    n_voltas = max(self.data_copy[file_name]['Dist'])//input_div_dist
                    if(lap_highlight and Y_axis[file_name]):
                        file = _highlight(Y_axis, selected_X, n_voltas, input_div_dist, self.ploted_figure, self.data_copy, file_name, file,self.number_of_graphs)
                    else:
                        if(Y_axis[file_name]):
                            for column_name in Y_axis[file_name]:
                                cont = cont + 1
                                for z in range(1, n_voltas+1):
                                    lap_location =  input_div_dist * z
                                    while True:
                                        if(not(np.where(self.data_copy[file_name]['Dist'] == lap_location))[0]):
                                            lap_location = lap_location + 1
                                        else:
                                            distance = (np.where(self.data_copy[file_name]['Dist'] == lap_location)[0])[0]
                                            break
                                    self.ploted_figure.add_trace(go.Scatter(y=[min(self.data_copy[file_name][column_name]), max(self.data_copy[file_name][column_name])],
                                                                            x=[self.data_copy[file_name][selected_X][distance], self.data_copy[file_name][selected_X][distance]],
                                                                            mode="lines", 
                                                                            line=go.scatter.Line(color="gray"), 
                                                                            showlegend=False
                                                                            ),
                                                                row=cont,
                                                                col=1
                                                                )
                    self.n_voltas = n_voltas
        elif('tempo' in div_radios_value):
            for file_name in files_names:
                for cont, column_name in enumerate(Y_axis[file_name]):
                    for z in tempo_voltas:
                        self.ploted_figure.add_trace(go.Scatter(y=[min(self.data_copy[file_name][column_name]), max(self.data_copy[file_name][column_name])],
                                                                x=[z, z],
                                                                mode="lines", 
                                                                line=go.scatter.Line(color="gray"), 
                                                                showlegend=False
                                                            ),
                                                    row=cont,
                                                    col=1
                                                    )

    def _overlap(self, sobreposicao_button, Y_axis, input_div_dist, selected_X, files_names):
        if (sobreposicao_button) :
            cont = 0
            self.ploted_figure.data = []
            for file_name in files_names:                                
                # Se for dividido por distancia   ?E se for dividido por tempo?
                n_voltas = max(self.data_copy[file_name]['Dist'])//input_div_dist
                if(Y_axis[file_name]):
                    for column_name in Y_axis[file_name]:
                        cont = cont + 1
                        aux = int(len(self.data_copy[file_name][column_name])/max(self.data_copy[file_name]['Dist']) * input_div_dist)
                        dist_use = list(_chunks_overlap(self.data_copy[file_name][selected_X], aux))
                        data_use = list(_chunks_overlap(self.data_copy[file_name][column_name], aux))
                        for i in range(0, n_voltas+1):
                            self.ploted_figure.add_trace(
                                go.Scatter(x=dist_use[0], y=data_use[i], name=("Volta {}".format(i+1) + " " + column_name)),
                                row=cont, col=1,
                            )
                            
                            
            self.ploted_figure['layout'].update(autosize = True)        