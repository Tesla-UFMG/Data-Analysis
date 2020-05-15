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

class Trata_dados:      

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