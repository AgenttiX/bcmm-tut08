import numpy as np


def generate_map(height: int, width: int):
    if width <= 1 or height <= 1:
        raise ValueError("Invalid dimensions")
    return np.random.randint(low=0, high=4, size=(height, width))
