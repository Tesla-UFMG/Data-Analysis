
class Chunks:
    
    @staticmethod
    def Chunks(lista, distance, next_distance):
        yield lista[distance : next_distance]
    