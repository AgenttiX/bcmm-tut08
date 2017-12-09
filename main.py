import matplotlib.pyplot as plt

import plotter
import logger
log = logger.get_logger(__name__, level="DEBUG", disabled=False)  # Root logger
import montecarlo




    


def main():
    #montecarlo.plot_monte_carlos(num_runs=20, iterations=3000, use_stored_results=[True, True])
    montecarlo.plot_classification_and_erros(iterations=1000, use_stored_results=True)
    #montecarlo.single_four_table(iterations=100)
    #montecarlo.log_stuff()
    #montecarlo.debug_my_stuff()
    

main()
