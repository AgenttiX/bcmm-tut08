import color
import direction

import collections
import numpy as np
import typing

import logger
log = logger.get_logger(__name__, level="DEBUG", disabled=True)


class Vehicle:
    """
    A vehicle that moves on a map
    """

    def __init__(self, map_grid: np.ndarray, max_history=10, start_direction=None, error: float=0.001):
        self.__map = map_grid
        self.__max_history = max_history

        self.__y = np.random.randint(low=0, high=self.__map.shape[0] - 1)
        self.__x = np.random.randint(low=0, high=self.__map.shape[1] - 1)
        self.__rel_y = 0
        self.__rel_x = 0
        self.error = error

        if start_direction is None:
            self.__direction = direction.Direction(np.random.randint(low=0, high=3))
        elif 0 <= start_direction <= 3:
            self.__direction = direction.Direction(start_direction)
        else:
            raise ValueError("Invalid start direction")

        self.__start_direction = self.__direction

        log.info("Starting at direction", self.__direction)

        self.__history = collections.deque(maxlen=self.__max_history)
        self.__history_error = collections.deque(maxlen=self.__max_history)

        self.__history.append((direction.RelativeDirection.FRONT, self.get_color(), 0, 0))
        self.__history_error.append(
            (direction.RelativeDirection.FRONT, self.change_measurement(self.get_color()), 0, 0)
        )

    def start_direction(self):
        """
        Get the absolute start direction of the vehicle
        :return: absolute start direction
        """
        return self.__start_direction

    def location(self) -> typing.Tuple[int, int, int]:
        """
        Get the absolute location and direction of the vehicle
        :return: x, y, direction
        """
        return self.__x, self.__y, self.__direction

    def get_color(self) -> color.Color:
        """
        Get the color of the cell the vehicle is currently on
        :return:
        """
        return color.Color(self.__map[self.__y, self.__x])
    
    #@staticmethod
    def change_measurement(self, measurement: typing.Union[int, color.Color]) -> color.Color:
        """
        Change the given value with the probability of 'self.error'
        :param measurement: color value
        :return: color value
        """

        if np.random.random() < self.error:
            color_change = np.random.randint(1, 4)
            result = (measurement + color_change) % 4
        else:
            result = measurement
        return color.Color(result)

    def history(self) -> np.ndarray:
        """
        Get movement history
        :return: numpy array of (direction, color)
        """
        l = len(self.__history)
        arr = np.zeros(shape=(l, 4))
        for i in range(l):
            snapshot = self.__history[i]
            arr[i, 0] = snapshot[0]
            arr[i, 1] = snapshot[1]
            arr[i, 2] = snapshot[2]
            arr[i, 3] = snapshot[3]
        return arr

    """
    def history(self) -> np.ndarray:
        l = len(self.__history)
        arr = np.zeros(shape=(l, 3))
        for i in range(l):
            snapshot = self.__history[i]
            dx, dy = direction_to_xy(snapshot[0])
            arr[i, 0] = dx
            arr[i, 1] = dy
            arr[i, 2] = snapshot[1]
        return arr
    """
    
    def history_error(self, iteration_for_seed, error: float=0.001) -> np.ndarray:
        """
        Get movement history that has measurement error in it. 
        So therefore it might flip one value out of 10 by change 1%, and two values by 
        chance 0.01% (or something similar).
        
        This uses unique id of the vehicle-object as a seed for random generator, so it is
        allowed to call this method more than once in a single lifetime.
        
        :return: numpy array of (direction, color, garbage, garbage)
        """
        l = len(self.__history)
        arr = np.zeros(shape=(l, 4), dtype=int)
        for i in range(l):
            snapshot = self.__history[i]
            arr[i, 0] = snapshot[0]
            arr[i, 1] = snapshot[1]
            arr[i, 2] = snapshot[2]
            arr[i, 3] = snapshot[3]
        
        np.random.seed(np.mod(int(id(self)), 2**16)+iteration_for_seed) 
        # seed can not be too large (memory address) :P
        # id(object) gives only like two different values
        # --> python uses same memory addresses for object in loop re-initialization
        rnd_colors = np.random.randint(3, size=self.__max_history)+1  # Note: error can not be same color (so therefore 1,2,3)
        rnd_prob = (np.random.random(self.__max_history) < error).astype(int)  # vector [0,0,...0,1,0,..0]
        np.random.seed(None)

        # altered_history
        arr[:, 1] = np.mod(arr[:, 1] + (rnd_colors*rnd_prob)[0 : l], 4)
        
        return arr

    def history_error_one(self) -> np.ndarray:
        """
        Get movement history that has a single measurement error in it
        :return: numpy array of (direction, color, rel_x, rel_y)
        """
        history = self.history()
        change_index = np.random.randint(0, history.shape[0])
        change_value = np.random.randint(1, 4)
        history[change_index, 1] = (history[change_index, 1] + change_value) % 4

        return history

    def history_error_builtin(self) -> np.ndarray:
        """
        Get the movement history that has built-in errors
        :return: numpy array of (direction, color, rel_x, rel_y)
        """
        l = len(self.__history_error)
        arr = np.zeros(shape=(l, 4))
        for i in range(l):
            snapshot = self.__history_error[i]
            arr[i, 0] = snapshot[0]
            arr[i, 1] = snapshot[1]
            arr[i, 2] = snapshot[2]
            arr[i, 3] = snapshot[3]
        return arr

    def map(self) -> np.ndarray:
        """
        Get the map the vehicle is moving on
        :return: map (numpy array)
        """
        return self.__map.copy()

    def move_bounded(self):
        """
        Move in such a way that the borders of the map are not crossed
        :return: -
        """
        d = np.random.randint(low=0, high=3)
        self.__direction = d

        moved_here = False
        if d == direction.Direction.EAST:
            if self.__x < self.__map.shape[1]-1:
                self.__x += 1
                moved_here = True
            else:
                self.move_bounded()
        elif d == direction.Direction.WEST:
            if self.__x > 0:
                self.__x -= 1
                moved_here = True
            else:
                self.move_bounded()
        elif d == direction.Direction.NORTH:
            if self.__y > 0:
                self.__y -= 1
                moved_here = True
            else:
                self.move_bounded()
        elif d == direction.Direction.SOUTH:
            if self.__y < self.__map.shape[0]-1:
                self.__y += 1
                moved_here = True
            else:
                self.move_bounded()
        else:
            raise RuntimeError("Invalid direction in movement")

        if moved_here:
            rel_dir = direction.RelativeDirection((self.__direction - self.__start_direction) % 4)
            rel_dx, rel_dy = rel_dir.xy()
            self.__rel_x += rel_dx
            self.__rel_y += rel_dy
            self.__history.append((rel_dir, self.get_color(), self.__rel_x, self.__rel_y))
            self.__history_error.append((rel_dir, self.change_measurement(self.get_color()), self.__rel_x, self.__rel_y))
            # print("Moving", direction.Direction(self.__direction), direction.RelativeDirection(rel_dir))

    def move_unbound(self):
        """
        Move in a way not bounded by the map edges
        :return: -
        """
        d = direction.Direction(np.random.randint(low=0, high=3))
        self.__direction = d
        
        dx, dy = d.xy()
        
        self.__x = (self.__x+dx) % self.__map.shape[0]  # modulus works with negative numbers -1%10 = 9
        self.__y = (self.__y+dy) % self.__map.shape[1]

        rel_dir = direction.RelativeDirection((self.__direction - self.__start_direction) % 4)
        rel_dx, rel_dy = rel_dir.xy()
        self.__rel_x += rel_dx
        self.__rel_y += rel_dy
        self.__history.append((rel_dir, self.get_color(), self.__rel_x, self.__rel_y))
        self.__history_error.append((rel_dir, self.change_measurement(self.get_color()), self.__rel_x, self.__rel_y))
