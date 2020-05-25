import pandas as pd
import io
import base64
from dash.exceptions import PreventUpdate
import dash


class lerArquivo:

    def __init__(self, data, num_dados):
        self.data = data
        self.num_dados = num_dados
        self.index_page_style = []
        self.main_page_style = []
        self.analise_Y_options = []
        self.analis_X_options = []
        self.upload_loading_children = []
        self.files_alert_open = False
        self.files_alert_children = []

    def get_data(self, list_of_contents, list_of_names):
        if list_of_contents is not None:
            if ('legenda.txt' in list_of_names):
                if len(list_of_names) >= 2:
                    files = dict(zip(list_of_names, list_of_contents))
                    legenda = pd.read_csv(io.StringIO(base64.b64decode(
                        files['legenda.txt'].split(',')[1]).decode('utf-8')))
                    legenda = [name.split()[0][0].upper() + name.split()[0][1:]
                                          for name in legenda.columns.values]

                    try:
                        for nome_do_arquivo in files:
                            if(nome_do_arquivo != 'legenda.txt'):
                                self.data = pd.read_csv(io.StringIO(base64.b64decode(files[nome_do_arquivo].split(
                                    ',')[1]).decode('utf-8')), delimiter='\t', names=legenda, index_col=False)
                    except:
                        self.index_page_style = dash.no_update
                        self.main_page_style = dash.no_update
                        self.analise_Y_options = dash.no_update
                        self.analis_X_options =  dash.no_update
                        self.upload_loading_children = dash.no_update
                        self.files_alert_open = True
                        self.files_alert_children =  "Os arquivos de dados não são do tipo .txt" 
                        return
                    options= []
                    self.num_dados = len(legenda)

                    for cont, column_name in enumerate(legenda):
                        options.append(
                            {'label': column_name, 'value': column_name})

                    self.index_page_style = {'display': 'none'}
                    self.main_page_style = {'display': 'inline'}
                    self.analise_Y_options = options
                    self.analis_X_options =  options
                    self.upload_loading_children = []
                    self.files_alert_open = dash.no_update
                    self.files_alert_children =  dash.no_update
                    return
                else:
                    self.index_page_style = dash.no_update
                    self.main_page_style = dash.no_update
                    self.analise_Y_options = dash.no_update
                    self.analis_X_options =  dash.no_update
                    self.upload_loading_children = dash.no_update
                    self.files_alert_open = True
                    self.files_alert_children =  "É necessário o upload de um arquivo de dados do tipo .txt"
                    return
            else:
                self.index_page_style = dash.no_update
                self.main_page_style = dash.no_update
                self.analise_Y_options = dash.no_update
                self.analis_X_options =  dash.no_update
                self.upload_loading_children = dash.no_update
                self.files_alert_open = True
                self.files_alert_children = "É necessário o upload de um arquivo chamado legenda.txt"
        else:
            raise PreventUpdate
