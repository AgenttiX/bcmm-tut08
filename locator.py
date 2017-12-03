import color
import direction
import vehicle

import numpy as np
import typing

import logger
log = logger.getLogger(__name__, level="DEBUG", disabled=False)


def locate(m: np.ndarray, history: np.ndarray, v: vehicle.Vehicle = None) -> typing.Tuple[int, int, int]:
    # Enable debug output if the vehicle is given
    debug = (v is not None)

    if debug:
        end_x, end_y, end_dir = v.location()

    # print(map)
    log.debug("History:")
    for y in range(history.shape[0]):
        log.debug(direction.RelativeDirection(history[y, 0]), color.Color(history[y, 1]))

    possible_end_loc = np.equal(m, history[0, 1])
    possible_loc = np.zeros(m.shape, dtype=bool)

    # Iterate map
    for y in range(m.shape[0]):
        for x in range(m.shape[1]):

            # If end location is possible
            if possible_end_loc[y, x]:
                if debug:
                    log.debug("Checking last location (x, y):", x, y)

                    if x == end_x and y == end_y:
                        log.debug("----")
                        log.debug("Checking the correct location", x, y)

                # Iterate orientations
                for start_direction in range(0, 4):
                    if debug:
                        log.debug("Checking with start direction", direction.Direction(start_direction))

                        if start_direction == v.start_direction():
                            log.debug("Checking correct start direction")

                    check_x = x
                    check_y = y
                    failed = False

                    # Iterate history
                    for hist_ind in range(1, history.shape[0]):
                        # history_dir = direction.RelativeDirection(history[hist_ind, 0])
                        # relative_dir = history_dir.reverse()
                        relative_dir = direction.RelativeDirection(history[hist_ind, 0])
                        abs_dir = direction.Direction((relative_dir + start_direction) % 4)

                        if debug:
                            log.debug(
                                "Converting history dir",
                                hist_ind,
                                ":",
                                relative_dir,
                                "to",
                                abs_dir
                            )

                        dx, dy = abs_dir.xy()
                        check_x -= dx
                        check_y -= dy
                        check_x = check_x % m.shape[1]
                        check_y = check_y % m.shape[0]

                        # No longer a problem since the vehicle is allowed to go outside the map
                        """
                        if not (0 <= check_x < m.shape[1] and 0 <= check_y < m.shape[0]):
                            log.debug("Locator went outside the map")
                            failed = True
                            break
                        """

                        if m[check_y, check_x] != history[hist_ind, 1]:
                            if debug:
                                log.debug(
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
                            log.debug("Color match", color.Color(m[check_x, check_y]), check_x, check_y)

                    if not failed:
                        log.debug("Found possible loc", x, y)
                        possible_loc[check_y, check_x] = True

    log.debug("Locator results:\n", possible_loc)
    possible_y, possible_x = possible_loc.nonzero()

    num_matches = possible_y.size
    
    if num_matches == 0:
        log.debug("No suitable places found")
        return num_matches, -9999, -9999
    if num_matches == 1 and possible_x.size == 1:
        log.debug("Found location", possible_x[0], possible_y[0])
        return num_matches, possible_x[0], possible_y[0]
    else:
        log.debug("Multiple possible locations found")
        return num_matches, -9999, -9999
