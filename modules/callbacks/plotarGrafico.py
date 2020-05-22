import numpy as np
from scipy import signal
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_core_components as dcc
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


from modules.functions.trataDados import Trata_dados
from modules.functions.modalBody import modalBody
from modules.functions.bandPass import bandPass
from modules.functions.filtros import Filtros
from modules.functions.Chunks import Chunks
from modules.functions.somaLista import somaLista

dados_tratados = Trata_dados()
filtros = Filtros()
modal_body = modalBody()
bandpass_filter = bandPass()
chunks = Chunks()

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

class plotarGrafico():

    def __init__(self, ploted_figure):
        self.ploted_figure = ploted_figure
        self.debuger = True
        
    def plotar(self, button_plot, button_apply, div_switches_value, div_radios_value, set_div_dist, sobreposicao_button,
               selected_columns_Y, selected_X, filters, filters_subseq,
               identificador, bandpass_check, bandpass_inf, bandpass_sup, savitzky_check, savitzky_cut, savitzky_poly,
               input_div_dist, data, tempo_voltas):

        if button_plot != 0 or button_apply != 0:

            data_copy = data.copy()
            modal_itens = []
            self.debuger = False

            if int(button_plot) > int(button_apply):

                eixoY = selected_columns_Y
                dados_tratados.trataDados(selected_X, selected_columns_Y, data)
                data_copy = data.copy()

                if filters_subseq % 2 == 0:
                    filters_subseq = filters_subseq + 1

                if ('Filtro Mediana' in filters) and ('Média Móvel' in filters):

                    for column in selected_columns_Y:
                        data_copy[column] = filtros.smooth(signal.medfilt(data_copy[column], filters_subseq), filters_subseq)
                elif 'Média Móvel' in filters:

                    for column in selected_columns_Y:
                        data_copy[column] = filtros.smooth(data_copy[column], filters_subseq)
                elif 'Filtro Mediana' in filters:

                    for column in selected_columns_Y:
                        data_copy[column] = signal.medfilt(data_copy[column], np.array(filters_subseq))

            elif(int(button_plot) < int(button_apply)):

                for cont, id in enumerate(identificador):
                    if('Passa-Banda' in bandpass_check[cont]):

                        data_copy[id['index']] = bandpass_filter.element_bandpass_filter(data_copy[id['index']], 
                                                                                         bandpass_inf[cont],
                                                                                         bandpass_sup[cont],
                                                                                         fs=60
                                                                                        )

                    if('Filtro savitzky-golay' in savitzky_check[cont]):

                        window_length = savitzky_cut[cont]
                        if window_length % 2 == 0:
                            window_length += 1

                        data_copy[id['index']] = signal.savgol_filter(data_copy[id['index']],
                                                                      window_length = window_length,
                                                                      polyorder = savitzky_poly[cont]
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

                modal_itens.extend(modal_body.element_modal_body(column_name))

            # Acresenta traços de divisão de voltas
            if(1 in div_switches_value):
                
                # Se for por distância
                if('distancia' in div_radios_value):

                    if set_div_dist:
                        n_voltas = len(data_copy['Dist'])//input_div_dist
                        
                        for cont, column_name in enumerate(selected_columns_Y):
                            for z in range(1, n_voltas+1):
                                fig.add_trace(go.Scatter(y=[min(data_copy[column_name]), max(data_copy[column_name])],
                                                         x=[input_div_dist*z, input_div_dist*z],
                                                         mode="lines", 
                                                         line=go.scatter.Line(color="gray"), 
                                                         showlegend=False
                                                        ),
                                              row=cont+1,
                                              col=1
                                             )
                # Se for por tempo
                elif('tempo' in div_radios_value):

                    for cont, column_name in enumerate(selected_columns_Y):
                        for z in tempo_voltas:
                            fig.add_trace(go.Scatter(y=[min(data_copy[column_name]), max(data_copy[column_name])],
                                                     x=[z, z],
                                                     mode="lines", 
                                                     line=go.scatter.Line(color="gray"), 
                                                     showlegend=False
                                                    ),
                                          row=cont+1,
                                          col=1
                                         )

            # sobreposição de voltas
            if (sobreposicao_button) :
                fig.data = []

                for cont, column_name in enumerate(selected_columns_Y):
                    w = len(data_copy[column_name])/max(data_copy['Dist'])
                    b = w * input_div_dist
                    w = int(b)
                    dist_use = list(chunks.Chunks(data_copy['Dist'], w))
                    data_use = list(chunks.Chunks(data_copy[column_name], w))
                    
                    for i in range(0, n_voltas+1):
                        fig.add_trace(
                            go.Scatter(x=dist_use[0], y=data_use[i], name="Volta {}".format(i+1)),
                            row=cont+1, col=1
                        )

            fig['layout'].update(height=120*len(selected_columns_Y)+35, margin={'t':25, 'b':10, 'l':100, 'r':100}, uirevision='const')

            self.ploted_figure = fig
            self.changes_loading_children = []
            self.graph_content_children = dcc.Graph(
                                                figure=fig,
                                                id='figure-id',
                                                config={'autosizable' : False}
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
            self.configuracao_sobreposicao_style = {'display':'block',
                                                    'border-left-style': 'outset',
                                                    'border-width': '2px',
                                                    'margin-left': '30px',
                                                    'margin-top': '15px'
                                                   }
            return 
        else:
            raise PreventUpdate
