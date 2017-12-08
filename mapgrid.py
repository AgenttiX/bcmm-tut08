import numpy as np


def generate_map(height: int, width: int):
    """
    Generate a random 4-color map with the given dimensions
    :param height: grid height
    :param width: grid width
    :return: map (numpy array)
    """

    if width <= 1 or height <= 1:
        raise ValueError("Invalid dimensions")
    return np.random.randint(low=0, high=4, size=(height, width))
