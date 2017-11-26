import enum


@enum.unique
class Direction(enum.IntEnum):
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
    RIGHT = 3
    FRONT = 0
    LEFT = 1
    BACK = 2


if __name__ == "__main__":
    test = Direction(1)

    print("Reference:", test)
    for i in range(4):
        print(Direction(i), RelativeDirection((i - test) % 4))
