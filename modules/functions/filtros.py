import numpy as np
from scipy import signal

class Filtros:

    @staticmethod
    # Funçao de Media Movel
    def smooth(y, box_pts):

        box = np.ones(box_pts)/box_pts
        y_smooth = np.convolve(y, box, mode='same')

        return y_smooth
