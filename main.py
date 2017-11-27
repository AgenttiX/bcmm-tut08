import color
import locator
import mapgrid
import plotter
import vehicle

import logger; logger.set_level("DEBUG") # "DEBUG", "INFO" or "WARNING"

height = 10
width = 10

m = mapgrid.generate_map(10, 10)
v = vehicle.Vehicle(m)

plot = plotter.LocatorPlot(v)
plot.plot_map()
plot.plot_vehicle()

logger.info("Start location:", str(v.location()))
logger.info("Start color:", v.color())

for i in range(5):
    v.move_unbound()
    plot.plot_vehicle()

found, x, y = locator.locate(v.map(), v.history(), v)

logger.info("End location:", v.location())
logger.info("End color:", v.color())
if found:
    logger.info("Found on location", x, y)
else:
    logger.warning("Location not found!")
    

plot.show()
