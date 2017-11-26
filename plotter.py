import direction
import vehicle

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np


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
        print(location[2], arrow_dir)
        plt.arrow(
            location[0]-arrow_dir[0]*0.2,
            location[1]-arrow_dir[1]*0.2,
            arrow_dir[0]*0.01,
            arrow_dir[1]*0.01,
            head_width=0.4,
            head_length=0.4
        )

    def show(self):
        plt.show()
