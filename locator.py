import color
import direction
import vehicle

import numpy as np
import typing

import logger



def locate(m: np.ndarray, history: np.ndarray, v: vehicle.Vehicle) -> typing.Tuple[bool, int, int]:
    # print(map)
    for y in range(history.shape[0]):
        logger.debug(direction.RelativeDirection(history[y, 0]), color.Color(history[y, 1]))

    possible_end_loc = np.equal(m, history[0, 1])
    possible_loc = np.zeros(m.shape, dtype=bool)

    end_x, end_y, end_dir = v.location()

    # Iterate map
    for y in range(m.shape[0]):
        for x in range(m.shape[1]):

            # If end location is possible
            if possible_end_loc[y, x]:
                logger.debug("Checking last location (x, y):", x, y)

                # Debug
                if x == end_x and y == end_y:
                    logger.debug("----")
                    logger.debug("Checking the correct location")

                # Iterate orientations
                for start_direction in range(0, 4):
                    print("Checking with start direction", direction.Direction(start_direction))

                    if start_direction == v.start_direction():
                        print("Checking correct start direction")

                    check_x = x
                    check_y = y
                    failed = False

                    # Iterate history
                    for hist_ind in range(1, history.shape[0]):
                        relative_dir = direction.RelativeDirection(history[hist_ind, 0])
                        abs_dir = direction.Direction((relative_dir + start_direction) % 4)

                        print("Converting relative direction",
                              relative_dir,
                              "to",
                              abs_dir)

                        dx, dy = abs_dir.xy()
                        check_x -= dx
                        check_y -= dy

                        if not (0 <= check_x < m.shape[1] and 0 <= check_y < m.shape[0]):
                            logger.debug("Locator went outside the map")
                            failed = True
                            break
                        elif m[check_y, check_x] != history[hist_ind, 1]:
                            logger.debug(
                                "History color",
                                hist_ind,
                                "of",
                                check_x,
                                check_y,
                                "didn't match:",
                                color.Color(history[hist_ind, 1])
                            )
                            failed = True
                            break

                        print("Color match", check_x, check_y)

                    if not failed:
                        possible_loc[y, x] = True

    logger.debug(possible_loc)
    possible_y, possible_x = possible_loc.nonzero()

    if possible_y.size == 0:
        logger.debug("No suitable places found")
    if possible_y.size == 1 and possible_x.size == 1:
        logger.debug("Found location", possible_x[0], possible_y[0])
        return True, possible_x[0], possible_y[0]
    else:
        return False, 0, 0
