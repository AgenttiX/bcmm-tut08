import enum
import logger
log = logger.get_logger(__name__, level="DEBUG", disabled=True)


@enum.unique
class Direction(enum.IntEnum):
    """
    Absolute directions based on compass points
    """

    EAST = 0
    NORTH = 1
    WEST = 2
    SOUTH = 3

    def xy(self):
        if self.value == Direction.EAST:
            return 1, 0
        elif self.value == Direction.NORTH:
            return 0, -1
        elif self.value == Direction.WEST:
            return -1, 0
        elif self.value == Direction.SOUTH:
            return 0, 1
        else:
            raise ValueError("Invalid direction")


@enum.unique
class RelativeDirection(enum.IntEnum):
    """
    Directions relative to a reference point (such as the rotation of a vehicle)
    """

    RIGHT = 3
    FRONT = 0
    LEFT = 1
    BACK = 2

    def reverse(self):
        return RelativeDirection((self + 2) % 4)

    def xy(self):
        if self.value == RelativeDirection.RIGHT:
            return 1, 0
        elif self.value == RelativeDirection.FRONT:
            return 0, 1
        elif self.value == RelativeDirection.LEFT:
            return -1, 0
        elif self.value == RelativeDirection.BACK:
            return 0, -1
        else:
            raise ValueError("Invalid relative direction")


# Usage examples
if __name__ == "__main__":
    test = Direction(1)

    log.debug("Reference:", test)
    for i in range(4):
        print(Direction(i), RelativeDirection((i - test) % 4))

    log.debug("Reversing")
    for i in range(4):
        print(RelativeDirection(i), RelativeDirection(i).reverse())
