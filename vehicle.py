import color
import direction

import collections
import enum
import numpy as np
import typing

import logger


class Vehicle:
    __max_history = 10

    def __init__(self, map_grid: np.ndarray):
        self.__map = map_grid
        self.__y = np.random.randint(low=0, high=self.__map.shape[0] - 1)
        self.__x = np.random.randint(low=0, high=self.__map.shape[1] - 1)

        self.__direction = np.random.randint(low=0, high=3)
        self.__start_direction = self.__direction

        logger.info("Starting at direction", direction.Direction(self.__direction))

        self.__history = collections.deque(maxlen=self.__max_history)

        self.__history.append((0, self.color()))

    def start_direction(self):
        return self.__start_direction

    def location(self) -> typing.Tuple[int, int, int]:
        return self.__x, self.__y, self.__direction

    def color(self) -> color.Color:
        return color.Color(self.__map[self.__y, self.__x])

    def history(self) -> np.ndarray:
        """
        Get movement history
        :return: numpy array of (direction, color)
        """
        l = len(self.__history)
        arr = np.zeros(shape=(l, 2))
        for i in range(l):
            snapshot = self.__history[i]
            arr[i, 0] = snapshot[0]
            arr[i, 1] = snapshot[1]
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

    def map(self) -> np.ndarray:
        return self.__map.copy()

    def move(self):
        dir = np.random.randint(low=0, high=3)
        self.__direction = dir

        moved_here = False
        if dir == direction.Direction.EAST:
            if self.__x < self.__map.shape[1]-1:
                self.__x += 1
                moved_here = True
            else:
                self.move()
        elif dir == direction.Direction.WEST:
            if self.__x > 0:
                self.__x -= 1
                moved_here = True
            else:
                self.move()
        elif dir == direction.Direction.NORTH:
            if self.__y > 0:
                self.__y -= 1
                moved_here = True
            else:
                self.move()
        elif dir == direction.Direction.SOUTH:
            if self.__y < self.__map.shape[0]-1:
                self.__y += 1
                moved_here = True
            else:
                self.move()
        else:
            raise RuntimeError("Invalid direction in movement")

        if moved_here:
            rel_dir = (self.__direction - self.__start_direction) % 4
            self.__history.append((rel_dir, self.color()))
            # print("Moving", direction.Direction(self.__direction), direction.RelativeDirection(rel_dir))
    
    def move_unbound(self):
        dir = np.random.randint(low=0, high=3)
        self.__direction = dir
        
        dx, dy = direction.Direction(dir).xy()
        
        self.__x = (self.__x+dx) % self.__map.shape[0] # modulus works with negative numbers -1%10 = 9
        self.__y = (self.__y+dy) % self.__map.shape[1]

        rel_dir = (self.__direction - self.__start_direction) % 4
        self.__history.append((rel_dir, self.color()))
