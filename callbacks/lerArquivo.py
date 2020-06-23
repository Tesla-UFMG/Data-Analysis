#------------- Import Library -------------#
import pandas as pd
import io
import base64
from dash.exceptions import PreventUpdate
import dash
import logging
import itertools
import platform
import serial
import serial.tools.list_ports
import time
import dash_bootstrap_components as dbc
import os                                                                       
import multiprocessing 
#------------------------------------------#
def comp(linha,arquivo):
    for i in range(0,7):
        if not linha:
            return -1
        if linha[i] != arquivo[i]:
            return -1
        else:
            print(linha[i], arquivo[i])
    return 1
def sd_read():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(p[0])
    stm = serial.Serial(str(p[0]),baudrate = 115200, timeout = 0.5)
    c_file = "text3.txt"
    a = "1".encode('utf-8')
    stm.write(a)
    test_flag = []
    garbage = open(c_file,"w")
    while (1):
            line = stm.readline().decode("ascii").translate({ord('\x00'): None})   
            print(line)             
            if comp(line,"Arquivo") == 1:
                c_file =  line.rstrip("\r\n")
                if(not test_flag or test_flag == c_file[-1]):
                    test_flag = c_file[-1]
                    c_file = c_file[:-1]
                    c_file =  c_file.rstrip("\tCodigo do  Teste ") + ".txt"
                    print(c_file,test_flag) 
                    garbage = open(c_file,"w")
                else:
                    print("end")
                    break
            else:
                if(not test_flag or test_flag == line[-2]):
                    garbage.write(line)
                else:
                    garbage.close()
                    print("end")
                    break

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
        self.txt_index_page_hide_style = {}
        self.txt_creation_tab = {"display":"none"}
        self.txt_button_n_clicks = None
        self.txt_button_cancel_n_clicks = None
        self.txt_button_init_n_clicks = None
        self.txt_button_back_style = {"display":"none"}
        self.restriction = False
        self.txt_alert_children = []
        self.txt_alert_open = False

    def _get_data(self, list_of_contents, list_of_names):

        if list_of_contents is not None:

            if ('legenda.txt' in list_of_names):
            
                if len(list_of_names) >= 2:
            
                    files = dict(zip(list_of_names, list_of_contents))
                    legenda = pd.read_csv(io.StringIO(base64.b64decode(files['legenda.txt'].split(',')[1]).decode('utf-8')))

                    legenda = [name.split()[0][0].upper() + name.split()[0][1:]for name in legenda.columns.values]

                    try:
                        for nome_do_arquivo in files:
                            if(nome_do_arquivo != 'legenda.txt'):
                                self.data = pd.read_csv(io.StringIO(base64.b64decode(files[nome_do_arquivo].split(',')[1]).decode('utf-8')), 
                                                        delimiter='\t', names=legenda, index_col=False)
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
                        options.append({'label': column_name, 'value': column_name})

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
    

    def _txt_create(self,txt_button_n_clicks,txt_button_cancel_n_clicks):
        if(self.restriction and (txt_button_n_clicks != self.txt_button_n_clicks)):
            self.txt_alert_children = "Nenhum PORT Detectado"
            self.txt_alert_open = True
            self.txt_index_page_hide_style = {}
            self.txt_creation_tab = {"display":"none"}
            self.txt_button_n_clicks = txt_button_n_clicks
        else:
            self.txt_alert_children = []
            self.txt_alert_open = False
        if(txt_button_n_clicks != self.txt_button_n_clicks):
            self.txt_index_page_hide_style = {"display":"none"}
            self.txt_creation_tab = {"top": "15px"}
        self.txt_button_n_clicks = txt_button_n_clicks
        if(txt_button_cancel_n_clicks != self.txt_button_cancel_n_clicks):
            self.txt_index_page_hide_style = {}
            self.txt_creation_tab = {"display":"none"}
        self.txt_button_cancel_n_clicks = txt_button_cancel_n_clicks

    def _read_sd_card(self,txt_button_init_n_clicks):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            print(p[0])
        if(ports):
            self.restriction = False
            if(txt_button_init_n_clicks != self.txt_button_init_n_clicks):
                print("a")
                p = multiprocessing.Process(target = sd_read)
                p.start()
                self.txt_button_back_style = []
                self.txt_index_page_hide_style = {}
                self.txt_creation_tab = {"display":"none"}
        else:
            self.restriction = True
        self.txt_button_init_n_clicks = txt_button_init_n_clicks