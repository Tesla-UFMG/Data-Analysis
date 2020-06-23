#------------- Import Library -------------#
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
#------------------------------------------#

def _soma_lista(lista):
        
    if len(lista) == 1:
        return lista[0]
    else:
        return lista[0] + _soma_lista(lista[1:])

class processingPOSGraphic:

    def __init__(self):
        self.figure_id_figure = None
        self.add_line_button_value = None
        self.tempo_voltas = []
        self.lap_division_style = {'display':'none'}
        self.time_division_style = {'display':'none'}
        self.distance_division_style =  {'display': 'none'}
        self.time_input_children = []
    
    def _display_reference_lines(self, clickData, checklist_horizontal, radios_value, n1, add_line, input_value, lap_highlight, div_radios_value, 
                                 numero_voltas, sobreposicao_button, selected_X, selected_columns_Y, ploted_figure, n_voltas):
        
        if clickData is not None:

            # HORIZONTAL
            if("Horizontal" in checklist_horizontal):

                if('horizontal-grafico' in radios_value):

                    if("Line" in add_line):
                        
                        if (lap_highlight or sobreposicao_button):

                            yref = "y"
                            clean_yref = yref
                            curveNumber = clickData['points'][0]['curveNumber']

                            if('distancia' in div_radios_value):
                                x_voltas = n_voltas
                            elif('tempo' in div_radios_value):
                                x_voltas = numero_voltas

                            new_curveNumber = curveNumber // (x_voltas + 1)

                            if(curveNumber != 0):
                                if (curveNumber % (x_voltas + 1) == 0):
                                    yref = yref + str(new_curveNumber)
                                else:
                                    yref = yref + str(new_curveNumber + 1)

                            print(yref)

                            for i in range(1, len(selected_columns_Y)):
                                if (curveNumber == i * (x_voltas + 1)):
                                    yref = clean_yref + str(new_curveNumber + 1)

                            if (yref == "y0"):
                                yref = "y1"

                            print(yref)

                            ploted_figure.add_shape(type="line",
                                                    xref="paper", yref=yref,
                                                    y0=clickData['points'][0]['y'], y1=clickData['points'][0]['y'],
                                                    x0=0, x1=1,
                                                    line=dict(
                                                        color="black",
                                                        dash="dot",
                                                        width=1
                                                    ),
                                                )

                            ploted_figure['layout'].update(height=120*len(selected_columns_Y)+35, margin={'t':25, 'b':10, 'l':100, 'r':100}, uirevision='const')
                            
                            self.figure_id_figure = ploted_figure
                            self.add_line_button_value = []
                        else:
                            yref = "y"
                            curveNumber = clickData['points'][0]['curveNumber']
                            if(curveNumber != 0):
                                yref = yref + str(curveNumber+1)

                            ploted_figure.add_shape(type="line",
                                                    xref="paper", yref=yref,
                                                    y0=clickData['points'][0]['y'], y1=clickData['points'][0]['y'],
                                                    x0=0, x1=1,
                                                    line=dict(
                                                        color="black",
                                                        dash="dot",
                                                        width=1
                                                    ),
                                                )

                            ploted_figure['layout'].update(height=120*len(selected_columns_Y)+35, margin={'t':25, 'b':10, 'l':100, 'r':100}, uirevision='const')
                            
                            self.figure_id_figure = ploted_figure
                            self.add_line_button_value = []
                        
                        return
                    else:
                        raise PreventUpdate
                else:
                    raise PreventUpdate
            # VERTICAL
            else:

                last_figure = go.Figure(ploted_figure)
                last_figure.add_shape(type="line",
                                      yref="paper",
                                      x0=clickData['points'][0]['x'], x1=clickData['points'][0]['x'],
                                      y0=0, y1=1,
                                      line=dict(
                                          color="#505050",
                                          width=1.5
                                      )
                                     )
                                     
                self.figure_id_figure = last_figure
                self.add_line_button_value = dash.no_update

                return
        elif clickData is None:

            # Horizontal definido no input
            if('horizontal-value' in radios_value) and ("Horizontal" in checklist_horizontal):

                if n1:

                    ploted_figure.add_shape(type="line",
                                            xref="paper", yref="y",
                                            y0=input_value, y1=input_value,
                                            x0=0, x1=1,
                                            line=dict(
                                                color="black",
                                                dash="dot",
                                                width=1
                                            ),
                                           )

                    self.figure_id_figure = ploted_figure
                    self.add_line_button_value = []

                    return
            else:
                raise PreventUpdate
    
    def _able_lap_division(self, radios_value, numero_voltas, n1, input_value):

        if ('distancia' == radios_value):

            self.time_division_style = {'display': 'none'}
            self.distance_division_style = {'display': 'inline-block'}
        elif ('tempo' == radios_value):

            self.time_division_style = {'display': 'inline-block'}
            self.distance_division_style =  {'display': 'none'}

            new_input = html.Div([
                dbc.InputGroup(
                    [dbc.InputGroupAddon(("Volta {}:".format(i)), addon_type="prepend"),
                        dbc.Input(
                            id={
                                'type': 'input-tempo',
                                'index': 'input-volta-{}'
                            },
                            type="number",
                            min=0,
                            step=0.001,
                            value = 0
                        )
                    ]
                )
                for i in range(1, numero_voltas+1)
            ])

            self.time_input_children.insert(0, new_input)

            for i in range(1, len(self.time_input_children)):
                self.time_input_children.pop(i)

            tempo_div_voltas = [0]
            if n1:
                tempo_div_voltas = input_value

                # Seta o array com os valores das voltas somados
                self.tempo_voltas = np.zeros(len(tempo_div_voltas))

                for i in range(0, len(self.tempo_voltas)-1):
                    self.tempo_voltas[i] = _soma_lista(tempo_div_voltas[:i+1])

                self.tempo_voltas[len(tempo_div_voltas)-1] = _soma_lista(tempo_div_voltas)
                
        return