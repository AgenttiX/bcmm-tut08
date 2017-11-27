import direction
import vehicle

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import logger


class LocatorPlot:
    """
    A plotting system for locator data
    """

    __colormap = matplotlib.colors.from_levels_and_colors(
        [-0.5, 0.5, 1.5, 2.5, 3.5],
        ["w", "r", "g", "b"]
    )[0]

    def __init__(self, vehicle):
        self.__vehicle = vehicle

    def plot_map(self):
        plt.imshow(self.__vehicle.map(), cmap=self.__colormap)

    def plot_vehicle(self):
        location = self.__vehicle.location()
        arrow_dir = direction.Direction(location[2]).xy()
        plt.arrow(
            location[0]-arrow_dir[0]*0.7,
            location[1]-arrow_dir[1]*0.7,
            arrow_dir[0]*0.2,
            arrow_dir[1]*0.2,
            head_width=0.3,
            head_length=0.3
        )

    def show(self):
        plt.show()
