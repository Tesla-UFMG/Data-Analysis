from dash.exceptions import PreventUpdate

class DivVoltas:

    @staticmethod
    def able_divisao_volta(switch_value):
        
        if (1 in switch_value):
            return {'display':'inline-block'}
        else:
            return {'display':'none'}

    @staticmethod
    def able_tempo_or_distancia(radios_value):
    
        if ('distancia' in radios_value):
            return [{'display':'none'}, {'display':'inline-block'}]
        elif ('tempo' in radios_value):
            return [{'display':'inline-block'}, {'display':'none'}]
        else: 
            raise PreventUpdate