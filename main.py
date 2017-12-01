import color
import locator
import mapgrid
import plotter
import vehicle
import logger; logger.set_level("INFO") # "DEBUG", "INFO", "WARNING", "ERROR"
import montecarlo

"""
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
if found==0:
    logger.info("Found on location", x, y)
else:
    logger.warning("Location not found!")
"""

# This is temporary (till saturday)
montecarlo.run(gridsize=10, steps=6, MC_iterations=100)
montecarlo.run(gridsize=20, steps=6, MC_iterations=100)
montecarlo.run(gridsize=30, steps=6, MC_iterations=100)
montecarlo.run(gridsize=40, steps=6, MC_iterations=100)
montecarlo.run(gridsize=50, steps=6, MC_iterations=100)

montecarlo.run(gridsize=50, steps=3, MC_iterations=100)
montecarlo.run(gridsize=50, steps=4, MC_iterations=100)
montecarlo.run(gridsize=50, steps=5, MC_iterations=100)
montecarlo.run(gridsize=50, steps=6, MC_iterations=100)
montecarlo.run(gridsize=50, steps=7, MC_iterations=100)





#plot.show()
