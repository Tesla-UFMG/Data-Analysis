
class somaLista:
    @staticmethod
    def somaLista(lista):
        
        if len(lista) == 1:
            return lista[0]
        else:
            return lista[0] + somaLista(lista[1:])