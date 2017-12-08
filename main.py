import matplotlib.pyplot as plt

import plotter
import logger
log = logger.get_logger(__name__, level="DEBUG", disabled=False)  # Root logger
import montecarlo


def plot_monte_carlos(num_runs=20, iterations=1000, use_stored_results=[True,True]):
    
    # first with no error

    gridsizes_0, Prob_MC_matrix_gs_0 = montecarlo.calc_curves_gridsizes(steps=10, 
                                                                        num_runs=num_runs, 
                                                                        iterations=iterations, 
                                                                        use_stored_results=use_stored_results[0],
                                                                        error=False)

    steps_0, Prob_MC_matrix_st_0 = montecarlo.calc_curves_steps(gridsize=20, 
                                                                num_runs=num_runs, 
                                                                iterations=iterations, 
                                                                use_stored_results=use_stored_results[0], 
                                                                error=False)
                                                                
    
    # then with 0.001 error in measurement of color
    gridsizes_1, Prob_MC_matrix_gs_1 = montecarlo.calc_curves_gridsizes(steps=10, 
                                                                        num_runs=num_runs, 
                                                                        iterations=iterations, 
                                                                        use_stored_results=use_stored_results[1], 
                                                                        error=True)
    steps_1, Prob_MC_matrix_st_1 = montecarlo.calc_curves_steps(gridsize=20, 
                                                                num_runs=num_runs, 
                                                                iterations=iterations, 
                                                                use_stored_results=use_stored_results[1], 
                                                                error=True)
    
    plotter.plot_gridsizes_error(gridsizes_0, Prob_MC_matrix_gs_0, gridsizes_1, Prob_MC_matrix_gs_1, num_runs)
    plotter.plot_steps_error(steps_0, Prob_MC_matrix_st_0, steps_1, Prob_MC_matrix_st_1, num_runs)
    
    plt.show()
    
def plot_classification_and_erros():
    
    x_axis, var_map = calc_confusion_mat(gridsize=-1, steps=10, iterations=1000, dirname="variate_map", use_stored_results=False)
    x_axis, var_steps = calc_confusion_mat(gridsize=20, steps=-1, iterations=1000, dirname="variate_steps", use_stored_results=False)
    
    plotter.plot_conf_mat()
    


def main():
    plot_monte_carlos(num_runs=20, iterations=3000, use_stored_results=[True, True])
    #montecarlo.log_stuff()
    #montecarlo.debug_my_stuff()
    

main()
