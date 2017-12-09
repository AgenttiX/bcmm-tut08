import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

import direction
import vehicle
import logger
log = logger.get_logger(__name__, level="DEBUG", disabled=False, colors=True)

plt2tikZ_is_crappy = False
if not plt2tikZ_is_crappy:
    from matplotlib2tikz import save as tikz_save
    # https://github.com/nschloe/matplotlib2tikz
else:
    def tikz_save(asdf):
        pass


class LocatorPlot:
    """
    A plotting system for locator data
    """

    __colormap = matplotlib.colors.from_levels_and_colors(
        [-0.5, 0.5, 1.5, 2.5, 3.5],
        [(1, 1, 1), (0.9765, 0, 0), (0, 0.9686, 0), (0, 0, 0.9765)]
        # ["w", "r", "g", "b"]
    )[0]

    def __init__(self, v: vehicle.Vehicle):
        self.__vehicle = v

    def plot_map(self):
        plt.imshow(self.__vehicle.map(), cmap=self.__colormap)

    def plot_vehicle(self):
        location = self.__vehicle.location()
        arrow_dir = direction.Direction(location[2]).xy()
        plt.arrow(
            location[0]-arrow_dir[0]*0.7,
            location[1]-arrow_dir[1]*0.7,
            arrow_dir[0]*0.2,
            arrow_dir[1]*0.2,
            head_width=0.3,
            head_length=0.3
        )

    def save(self, filename: str):
        tikz_save(filename + ".tex")
        plt.savefig(filename + ".png")
        plt.savefig(filename + ".eps")

    def show(self):
        plt.show()


# These 5 functions are for tikz saving process

def block_print(): 
    sys.stdout = open(os.devnull, 'w')


def enable_print():
    sys.stdout = sys.__stdout__


def write_lines(filename, contains, insert_this):
    """
    Inserts text 'insert_this' in file 'filename' after the line that contains 'contains'
    """
    with open(filename, 'r') as file:
        data = file.readlines()

    for idx, line in enumerate(data):
        if contains in line:
            data.insert(idx+1, insert_this)
            break

    with open(filename, 'w') as file:
        file.writelines(data)


def fix_labels_in_tikz(*labels) -> str:
    """
    Generates the required insertion for to get line labels working in tikz
    
    The whole insertion looks something like this in a whole:
    
    insertion = \
        "legend entries={{" + label1 + "},{" + label2 + "},{" + label3 + "}},"+ "\n" +\
        "legend cell align={right}," + "\n" +\
        "legend style={draw=white!80.0!black}," + "\n" +\
        "legend style={at={(0.03,1.03)},anchor=south west}" + "\n" +\
        "]  % replace the ending bracket" + "\n" +\
        "\\addlegendimage{no markers, color0}"+ "\n" +\
        "\\addlegendimage{no markers, color1}"+ "\n" +\
        "\\addlegendimage{no markers, color2}%" 
    
    """
    
    insertion = ",\n"  # text insertion in tikz file after line "y grid style=..."
    
    label_entries = "legend entries={"
    for i in range(len(labels)):
        label_entries += "{" + labels[i] + "}"
        if i != len(labels)-1:
            label_entries += ","
    label_entries += "},\n"
    insertion += label_entries
    
    insertion += "legend cell align={right},\n"
    insertion += "legend style={draw=white!80.0!black},\n"
    insertion += "legend style={at={(0.1,1.03)},anchor=south west}\n"
    insertion += "]  % replace the ending bracket\n"
    
    for i in range(len(labels)):
        insertion += "\\addlegendimage{no markers, color" + str(i) + "}"
        
        if i != len(labels)-1:
            insertion += "\n"
        else:
            insertion += "%"
    
    return insertion


def tikz_save_with_labels(pathname, labels):
    
    block_print()
    tikz_save(pathname)
    enable_print()
        
    log.debug("Adding lines to file 'gridsizes.tikz' in part 'begin{axis}['" + "\n")
        
    add_label = fix_labels_in_tikz(*labels)
    write_lines('figures/gridsizes.tikz', "y grid style", add_label)


def plot_gridsizes_error(gridsizes0, single_matches0, gridsizes1, single_matches1, num_runs):
    """
    Plots for probabilities as function of gridsizes
    
    arguments
        gridsizes0          -  vector
        single_matches0     -  probability-matrix to find single match (no 0.001 error)
        gridsizes1          -  vec
        single_matches1     -  probability-matrix to find single match with 0.001 error. 
                               Includes both correct and incorrect matches
        num_runs            -  number of run-sets, is about 10
    """
    # Matrix excepted values and errorbars
    mean_mat0 = np.mean(single_matches0, axis=0)                        # (no 0.001 error)
    mean_mat1 = np.mean(single_matches1, axis=0)                        # with 0.001 error
    err_mat0 = np.std(single_matches0, axis=0) / np.sqrt(num_runs)      # (no 0.001 error)
    err_mat1 = np.std(single_matches1, axis=0) / np.sqrt(num_runs)      # with 0.001 error
    
    # Excepted values and errorbars for probability-values of correctly found cases
    mean_correct0 = mean_mat0[:,0]
    mean_correct1 = mean_mat1[:,0]
    err_correct0 = err_mat0[:,0]
    err_correct1 = err_mat1[:,0]
    
    # Excepted values and errorbars for probability-values of incorrectly found cases
    mean_incorrect1 = mean_mat1[:,1]
    err_incorrect1 = err_mat1[:,1]
    if (np.sum(mean_mat0[:,1]) > 0):# There should be no incorrect matches without the 0.001 error!
        log.warning("Map locator has located wrong location! This message should not be printed.")
    
    mean_not_found1 = mean_mat1[:,2]
    err_not_found1 = err_mat1[:,2]
    if (np.sum(mean_mat0[:,2]) > 0):
        log.warning("Map locator has not found location when it should have! This message should not be printed.")

    
    plt.figure("gridsizes oikea tulos")
    label1 = "Löytyi, aina tarkka mittaus"
    label2 = "Löytyi, mittausvirhe"
    label3 = "Ei löytynyt, mittausvirhe"
    plt.errorbar(gridsizes0, mean_correct0, yerr=err_correct0, capsize=5, label=label1)
    plt.errorbar(gridsizes1, mean_correct1, yerr=err_correct1, capsize=5, label=label2)
    plt.errorbar(gridsizes1, mean_not_found1, yerr=err_not_found1, capsize=5, label=label3)
    plt.xlabel("kartan koko")
    plt.ylabel("P")
    plt.ylim([0.5,1])
    #plt.legend()
    
    """
    matplotlib2tikz is buggy and can not draw legends and errorbars at the same time.
    To add legends by hand, add following lines at the end of block "\begin{axis}[...""
    
    , % notice to add a colon at the end of last line before ']'!
    legend entries={{asdf},{asdf2}},
    legend cell align={left},
    legend style={draw=white!80.0!black}
    ] % this
    """
    
    
    if not plt2tikZ_is_crappy:
        block_print()
        tikz_save('figures/gridsizes.tikz')
        enable_print()
        
        log.debug("Adding lines to file 'gridsizes.tikz' after 'begin{axis}['" + "\n")
        
        add_label = fix_labels_in_tikz(label1,label2)
        write_lines('figures/gridsizes.tikz', "y grid style", add_label)
        
    else:
        plt.savefig('figures/gridsizes.pgf')
        
    plt.legend()
    
    
    plt.figure("gridsizes väärä tulos")
    plt.errorbar(gridsizes1, mean_incorrect1, yerr=err_incorrect1, capsize=5)
    plt.xlabel("kartan koko")
    plt.ylabel("P")
    
    if not plt2tikZ_is_crappy:
        block_print()
        tikz_save('figures/gridsizes_incorrect_result.tikz')
        enable_print()
    else:
        plt.savefig('figures/gridsizes_incorrect_result.pgf')


def plot_steps_error(steps0, single_matches0, steps1, single_matches1, num_runs):
    """
    Plots for probabilities as function of gridsizes
    
    arguments
        steps0              -  
        single_matches0     -  probability-matrix to find single match (no 0.001 error)
        steps1              -
        single_matches1     -  probability-matrix to find single match with 0.001 error. 
                               Includes both correct and incorrect matches
        num_runs            -  number of run-sets, is about 10. Used in calculation of error in mean
                       
    """
    # Matrix excepted values and errorbars
    mean_mat0 = np.mean(single_matches0, axis=0)                        # (no 0.001 error)
    mean_mat1 = np.mean(single_matches1, axis=0)                        # with 0.001 error
    err_mat0 = np.std(single_matches0, axis=0) / np.sqrt(num_runs)      # (no 0.001 error)
    err_mat1 = np.std(single_matches1, axis=0) / np.sqrt(num_runs)      # with 0.001 error Used in calculation of error in mean
    
    
    # Excepted values and errorbars for probability-values of correctly found cases
    mean_correct0 = mean_mat0[:,0]
    mean_correct1 = mean_mat1[:,0]
    err_correct0 = err_mat0[:,0]
    err_correct1 = err_mat1[:,0]
    
    # Excepted values and errorbars for probability-values of incorrectly found cases
    mean_incorrect1 = mean_mat1[:,1]
    err_incorrect1 = err_mat1[:,1]
    if (np.sum(mean_mat0[:,1]) > 0):# There should be no incorrect matches without the 0.001 error!
        log.warning("Map locator has located wrong location! This message should not be printed.")
    
    mean_not_found1 = mean_mat1[:,2]
    err_not_found1 = err_mat1[:,2]
    if (np.sum(mean_mat0[:,2]) > 0):
        log.warning("Map locator has not found location when it should have! This message should not be printed.")

    
    plt.figure("steps oikea tulos")
    label1 = "Löytyi, aina tarkka mittaus"
    label2 = "Löytyi, mittausvirhe"
    label3 = "Ei löytynyt, mittausvirhe"
    plt.errorbar(steps0, mean_correct0, yerr=err_correct0, capsize=5, label=label1)
    plt.errorbar(steps1, mean_correct1, yerr=err_correct1, capsize=5, label=label2)
    plt.errorbar(steps1, mean_not_found1, yerr=err_not_found1, capsize=5, label=label3)
    plt.xlabel("askelten lukumäärä")
    plt.ylabel("P")
    plt.ylim([0,1])
    #plt.legend()
    
    if not plt2tikZ_is_crappy:
        block_print()
        tikz_save('figures/steps.tikz')
        enable_print()
        
        log.debug("Adding lines to file 'steps.tikz' after 'begin{axis}['" + "\n")
                 
        add_label = fix_labels_in_tikz(label1,label2,label3)
        write_lines('figures/steps.tikz', "y grid style", add_label)
    else:
        plt.savefig('figures/steps.pgf')
    
    plt.legend()
    
    
    plt.figure("steps väärä tulos")
    plt.errorbar(steps1, mean_incorrect1, yerr=err_incorrect1, capsize=5)
    plt.xlabel("askelten lukumäärä")
    plt.ylabel("P")

    if not plt2tikZ_is_crappy:
        block_print()
        tikz_save('figures/steps_incorrect_result.tikz')
        enable_print()
        
    else:
        plt.savefig('figures/steps_incorrect_result.pgf')


def plot_conf_mat(x_axis, mat, xlabel="", ylim=None):
    # Labels 
    TP_l = "TP"
    FN_l = "FN"
    FP_l = "FP"
    TN_l = "TN"
    
    TP_mean = mat[:,0,0,0]
    FN_mean = mat[:,0,1,0]
    FP_mean = mat[:,0,0,1]
    TN_mean = mat[:,0,1,1]
    
    TP_err = mat[:,1,0,0]
    FN_err = mat[:,1,1,0]
    FP_err = mat[:,1,0,1]
    TN_err = mat[:,1,1,1]
    
    
    fig_corr = plt.figure(xlabel+" Correct precentages TP, TN")
        
    plt.errorbar(x_axis, TP_mean, yerr=TP_err, capsize=4, label=TP_l)
    plt.errorbar(x_axis, TN_mean, yerr=TN_err, capsize=4, label=TN_l)
    
    plt.xlabel(xlabel)
    plt.ylabel("P")
    plt.ylim(ylim)
            
    
    fig_incorr = plt.figure(xlabel+" Incorrect precentages FN, FP")
    
    plt.errorbar(x_axis, FN_mean, yerr=FN_err, capsize=4, label=FN_l)
    plt.errorbar(x_axis, FP_mean, yerr=FP_err, capsize=4, label=FP_l)

    plt.xlabel(xlabel)
    plt.ylabel("P")
    plt.ylim(ylim)
    
    save_name_corr = 'figures/' + xlabel+"_correct"
    save_name_incorr = 'figures/' + xlabel+"_incorrect"
    
    if not plt2tikZ_is_crappy:
        block_print()
        
        plt.figure(xlabel+" Correct precentages TP, TN")
        tikz_save(save_name_corr + '.tikz')
        plt.legend()
        
        plt.figure(xlabel+" Incorrect precentages FN, FP")
        tikz_save(save_name_incorr + '.tikz')
        plt.legend()
        
        enable_print()
        
        
        log.debug("Adding lines to files '" + 'figures/' + xlabel + "_XXX.tikz' after 'begin{axis}['" + "\n")
                 
        add_label_corr = fix_labels_in_tikz(TP_l, TN_l)
        add_label_incorr = fix_labels_in_tikz(FN_l, FP_l)
        write_lines(save_name_corr + '.tikz', "y grid style", add_label_corr)
        write_lines(save_name_incorr + '.tikz', "y grid style", add_label_incorr)

    else:
        plt.figure(xlabel+" Correct precentages TP, TN")
        plt.legend()
        
        plt.figure(xlabel+" Incorrect precentages FN, FP")
        plt.legend()
        
        fig_corr.savefig(save_name_corr + '.pgf')
        fig_incorr.savefig(save_name_incorr + '.pgf')
    
    
    
    
        
    
    
    
