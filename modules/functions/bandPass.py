from scipy import signal

class bandPass:
    @staticmethod
    def element_bandpass_filter(data, lowcut, highcut, fs, order=5):
        
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = signal.butter(order, [low, high], btype='band')
        y = signal.lfilter(b, a, data)
        return y