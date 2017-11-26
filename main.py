import color
import locator
import mapgrid
import plotter
import vehicle


height = 10
width = 10

m = mapgrid.generate_map(10, 10)
v = vehicle.Vehicle(m)

plot = plotter.LocatorPlot(v)
plot.plot_map()
plot.plot_vehicle()

print("Start location:", v.location())
print("Start color:", v.color())

for i in range(5):
    v.move()
    plot.plot_vehicle()

locator.locate(v.map(), v.history(), v)

print("End location:", v.location())
print("End color:", v.color())
plot.show()
