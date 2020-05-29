#------------- Import Library -------------#
import numpy as np
from scipy import signal
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_core_components as dcc
import dash
#------------------------------------------#

#-------------- Import Pages --------------#
from modules.functions.trataDados import Trata_dados
from modules.functions.modalBody import modalBody
from modules.functions.bandPass import bandPass
from modules.functions.filtros import Filtros
from modules.functions.Chunks import Chunks
#------------------------------------------#

#---------- Instanciando Objetos ----------#
dados_tratados = Trata_dados()
filtros = Filtros()
modal_body = modalBody()
bandpass_filter = bandPass()
chunks = Chunks()
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

class plotarGrafico():

    @staticmethod
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

    @staticmethod
    # Funçao de Media Movel
    def smooth(y, box_pts):

        box = np.ones(box_pts)/box_pts
        y_smooth = np.convolve(y, box, mode='same')

        return y_smooth

    def __init__(self, ploted_figure):
        self.ploted_figure = ploted_figure
        self.data_copy = None
        self.sobreposicao_switch = False
    def filtros(self, button_plot, button_apply, selected_columns_Y, selected_X, filters, filters_subseq, identificador,
                bandpass_check, bandpass_inf, bandpass_sup, savitzky_check, savitzky_cut, savitzky_poly, data):

        self.data_copy = data.copy()

        if int(button_plot) > int(button_apply):

            if filters_subseq % 2 == 0:
                filters_subseq += 1

            if ('Filtro Mediana' in filters) and ('Média Móvel' in filters):

                for column in selected_columns_Y:
                    self.data_copy[column] = filtros.smooth(signal.medfilt(self.data_copy[column], filters_subseq), filters_subseq)
            elif 'Média Móvel' in filters:

                for column in selected_columns_Y:
                    self.data_copy[column] = filtros.smooth(self.data_copy[column], filters_subseq)
            elif 'Filtro Mediana' in filters:

                for column in selected_columns_Y:
                    self.data_copy[column] = signal.medfilt(self.data_copy[column], np.array(filters_subseq))
        
        elif(int(button_plot) < int(button_apply)):

            for cont, id in enumerate(identificador):
                if('Passa-Banda' in bandpass_check[cont]):

                    self.data_copy[id['index']] = bandpass_filter.element_bandpass_filter(self.data_copy[id['index']], 
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

        dados_tratados.trataDados(selected_X, selected_columns_Y, self.data_copy)

        return

    def plotar(self, div_switches_value, div_radios_value, set_div_dist, sobreposicao_button,
               selected_columns_Y, selected_X, input_div_dist, tempo_voltas):
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

            modal_itens.extend(modal_body.element_modal_body(column_name))

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
        self.configuracao_sobreposicao_style = dash.no_update
        return
    

    def _overlap_lines(self,div_radios_value,selected_columns_Y,selected_X,input_div_dist, set_div_dist):
        if('distancia' in div_radios_value):
            
                if set_div_dist:
                    n_voltas = max(self.data_copy['Dist'])//input_div_dist
                    self.configuracao_sobreposicao_style = {'display':'block',
                                                'border-left-style': 'outset',
                                                'border-width': '2px',
                                                'margin-left': '30px',
                                                'margin-top': '15px'
                                               }
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

    def _overlap(self,sobreposicao_button,selected_columns_Y, input_div_dist):
        # sobreposição de voltas
        if (sobreposicao_button) :
            n_voltas = max(self.data_copy['Dist'])//input_div_dist
            self.ploted_figure.data = []
            for cont, column_name in enumerate(selected_columns_Y):
                w = len(self.data_copy[column_name])/max(self.data_copy['Dist'])
                b = w * input_div_dist
                w = int(b)
                dist_use = list(chunks.Chunks(self.data_copy['Dist'], w))
                data_use = list(chunks.Chunks(self.data_copy[column_name], w))
                    
                for i in range(0, n_voltas+1):
                    self.ploted_figure.add_trace(
                        go.Scatter(x=dist_use[0], y=data_use[i], name="Volta {}".format(i+1)),
                        row=cont+1, col=1
                    )
        self.ploted_figure['layout'].update(height=120*len(selected_columns_Y)+35, margin={'t':25, 'b':10, 'l':100, 'r':100}, uirevision='const')
        