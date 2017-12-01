import color
import direction
import vehicle

import numpy as np
import typing

import logger


def locate(m: np.ndarray, history: np.ndarray, v: vehicle.Vehicle = None) -> typing.Tuple[int, int, int]:
    debug = (v is not None)

    if debug:
        end_x, end_y, end_dir = v.location()

    # print(map)
    for y in range(history.shape[0]):
        logger.debug(direction.RelativeDirection(history[y, 0]), color.Color(history[y, 1]))

    possible_end_loc = np.equal(m, history[0, 1])
    possible_loc = np.zeros(m.shape, dtype=bool)

    # Iterate map
    for y in range(m.shape[0]):
        for x in range(m.shape[1]):

            # If end location is possible
            if possible_end_loc[y, x]:
                if debug:
                    logger.debug("Checking last location (x, y):", x, y)

                    if x == end_x and y == end_y:
                        logger.debug("----")
                        logger.debug("Checking the correct location")

                # Iterate orientations
                for start_direction in range(0, 4):
                    if debug:
                        logger.debug("Checking with start direction", direction.Direction(start_direction))

                        if start_direction == v.start_direction():
                            logger.debug("Checking correct start direction")

                    check_x = x
                    check_y = y
                    failed = False

                    # Iterate history
                    for hist_ind in range(1, history.shape[0]):
                        relative_dir = direction.RelativeDirection(history[hist_ind, 0])
                        abs_dir = direction.Direction((relative_dir + start_direction) % 4)

                        if debug:
                            logger.debug("Converting relative direction",
                                  relative_dir,
                                  "to",
                                  abs_dir)

                        dx, dy = abs_dir.xy()
                        check_x -= dx
                        check_y -= dy
                        check_x = check_x % m.shape[1]
                        check_y = check_y % m.shape[0]

                        # No longer a problem since the vehicle is allowed to go outside the map
                        """
                        if not (0 <= check_x < m.shape[1] and 0 <= check_y < m.shape[0]):
                            logger.debug("Locator went outside the map")
                            failed = True
                            break
                        """

                        if m[check_y, check_x] != history[hist_ind, 1]:
                            if debug:
                                logger.debug(
                                    "History color",
                                    hist_ind,
                                    color.Color(history[hist_ind, 1]),
                                    "of",
                                    check_x,
                                    check_y,
                                    "didn't match to",
                                    color.Color(m[check_y, check_x])
                                )
                            failed = True
                            break

                        if debug:
                            logger.debug("Color match", check_x, check_y)

                    if not failed:
                        logger.debug("Found possible loc", x, y)
                        possible_loc[y, x] = True

    logger.debug("Locator results:\n", possible_loc)
    possible_y, possible_x = possible_loc.nonzero()
    
    
    num_matches = possible_y.size
    
    if num_matches == 0:
        logger.debug("No suitable places found")
    if num_matches == 1 and possible_x.size == 1:
        logger.debug("Found location", possible_x[0], possible_y[0])
        return num_matches, possible_x[0], possible_y[0]
    else:
        return num_matches, -9999, -9999
