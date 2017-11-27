import color
import locator
import mapgrid
import plotter
import vehicle

import logger; logger.set_level("DEBUG") # "DEBUG", "INFO" or "WARNING"

height = 10
width = 10

m = mapgrid.generate_map(width=width, height=height)
v = vehicle.Vehicle(m)

plot = plotter.LocatorPlot(v)
plot.plot_map()

# The placement of the vehicle need not be shown
# plot.plot_vehicle()

logger.info("Start location:", str(v.location()))
logger.info("Start color:", v.color())

for i in range(6):
    v.move_unbound()
    plot.plot_vehicle()

# found, x, y = locator.locate(v.map(), v.history(), v)
found, x, y = locator.locate(v.map(), v.history())

logger.info("End location:", v.location())
logger.info("End color:", v.color())
if found:
    logger.info("Found on location", x, y)
else:
    logger.warning("Location not found!")


plot.show()
