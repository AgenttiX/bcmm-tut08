import matplotlib.pyplot as plt

import plotter
import logger
log = logger.get_logger(__name__, level="DEBUG", disabled=False)  # Root logger
import montecarlo
import montecarlo_2
import movement




    


def main():
    #montecarlo.plot_monte_carlos(num_runs=20, iterations=3000, use_stored_results=[True, True])
    #montecarlo.plot_classification_and_erros(iterations=10000, use_stored_results=True, map_steps_err=[False, False, True])
    
    #montecarlo_2.plot_TP_error(iterations=10000, use_stored_results=True)
    #montecarlo_2.compare_algorithms_var_error(iterations=1000)
    
    #movement.movement_monte_carlo()
    movement.movement_monte_carlo_plot_movenents()
    
    
    #montecarlo.single_four_table(iterations=10000)
    #montecarlo.log_stuff()
    #montecarlo.debug_my_stuff()
    
    plt.show()
    

main()
