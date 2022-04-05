import numpy as np


def string2ascii_array(string):
    ascii_array = [np.int64(ord(char)) for char in string]
    ascii_array.extend([np.int64(0) for _ in range(255 - len(ascii_array))])
    return np.array(ascii_array)
