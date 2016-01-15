#!/usr/local/bin/python2.7
# encoding: utf-8
'''
pySMAC4SAT -- configuration for SAT

@author:     Stefan Falkner, Marius Lindauer

@copyright:  2015 AAD Group Freiburg. All rights reserved.

@license:   GPLv2

@contact:   {sfalkner,lindauer}@cs.uni-freiburg.de
'''


import sys
import logging
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import traceback


#adjust the PYTHON_PATH to find the submodules
spysmac_path = os.path.dirname(os.path.realpath(__file__))
sys.path =[ os.path.join(spysmac_path, "pysmac"),
            os.path.join(spysmac_path, "pynisher"),
            os.path.join(spysmac_path, "fanova")] + sys.path


import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec

import pysmac
import pysmac.analyzer
import pysmac.utils

from SpySMAC.utils.plot_scatter import plot_scatter_plot
from SpySMAC.utils.html_gen import generate_html
from SpySMAC.utils.config_space import ConfigSpace



#logging.basicConfig(level=logging.DEBUG)


__version__ = 0.2
__date__ = '2015-03-18'
__updated__ = '2015-05-20'


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def score(ts, cutoff, factor):
    if len(ts.shape) == 1:
        return(np.mean(ts + factor*ts*(ts>=cutoff)))
    elif len(ts.shape)== 2:
        return(np.mean(ts + factor*ts*(ts>=cutoff), axis=1))
    else:
        raise RuntimeError("The input data is corrupted!")

def parse_args(argv):
    '''Command line options.'''

    # program_name = os.path.basename(argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version,
                                                     program_build_date)
    program_shortdesc = 'SpySMAC - A Sat Solver configurator using pySMAC'

    program_license = '''%s

  Created by user_name on %s.
  Copyright 2015 AAD Group Freiburg. All rights reserved.

  Licensed under GPLv2
  http://www.gnu.org/licenses/gpl-2.0.html

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    # Setup argument parser
    parser = ArgumentParser(description=program_license,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    req_params = parser.add_argument_group("Required")

    req_params.add_argument("-i", "--inputdir", required=True,
                            help="input directory, use the directory you\
                            specified as output for SpySMAC_run.py")

    req_params.add_argument("-o", "--outputdir", required=True,
                            help="output directory")
    
    opt_params = parser.add_argument_group("Optional")
    
    opt_params.add_argument("-d", "--disable_fanova", action="store_true", default=False,
                            help="disables fANOVA")
    
    opt_params.add_argument("-m", "--memlimit_fanova", default=2024,
                            help="sets memory limit in MB for fANOVA")

    # Process arguments
    args = parser.parse_args(argv[1:])

    return(vars(args))


def analyze_simulations(args):
    '''
        analyze a run of SpySMAC 
        Args:
            args: command line arguments 
    '''

    options = parse_args(args)
    #print(options)
    
    if not os.path.isdir(options['outputdir']):
        os.makedirs(options['outputdir'])
    else:
        logging.warn("Output directory (%s) already exists; it will be overwritten." %(options['outputdir']))
    
    
    # find the number of trainings and test instances
    num_train_instances = file_len(os.path.join(options['inputdir'], 'instances.dat'))
    num_test_instances = file_len(os.path.join(options['inputdir'], 'test_instances.dat')) - \
                            num_train_instances
    
    train_indices = list(range(num_train_instances+num_test_instances,2*num_train_instances+num_test_instances))
    test_indices  =  list(range(num_train_instances, num_train_instances+num_test_instances))
 
    
    
    # get default performance data            
    try:
        obj = pysmac.analyzer.SMAC_analyzer(os.path.join(options['inputdir'],'default_validation_scenario.dat'))      
    except:
        traceback.print_exc()
        print("Loading the evaluation of the default configuration failed. "
              "Most likely you did not run SpySMAC_run with --seed 0.")

    tmp = obj.data[0]['test_performances']
    baseline_train = np.array([list(tmp[j]) for j in train_indices]).flatten()
    baseline_test  = np.array([list(tmp[j]) for j in test_indices]).flatten()
    

    # import the data for the configuration runs
    obj = pysmac.analyzer.SMAC_analyzer(options['inputdir'])    
   
    run_ids = []
    train_performances = []
    test_performances  = []
    
    # get performance for each run
    for i in list(obj.data.keys()):
        tmp = obj.data[i]['test_performances']
        
        tmp_train = np.array([list(tmp[j]) for j in train_indices]).flatten()
        tmp_test  = np.array([list(tmp[j]) for j in test_indices]).flatten()
        run_ids.append(i)
        train_performances.append(tmp_train)
        test_performances.append(tmp_test)
    
    # each ROW contains the measured performance for the instances
    train_performances = np.array(train_performances)
    test_performances  = np.array(test_performances)

    # pick best run (note: it might be possible SMAC does not find anything better!)
    #timeouts = (train_performances > obj.cutoff_time)
    
    if obj.overall_objective == "MEAN10":
        factor = 9
    else:
        raise NotImplementedError("Please contact the authors to implement the overall objective {}".format(obj.overall_objective))
    
    scores = score(train_performances, obj.cutoff_time, factor)
    best_train_run_num = np.argmin(scores)
    best_train_run_score = scores[best_train_run_num]
    
    baseline_score = score(baseline_test, obj.cutoff_time, factor)
    
    incumbent_test  = test_performances[best_train_run_num]
    incumbent_train = train_performances[best_train_run_num]
    
    # compare best run and default

    test_stats = get_stats(baseline_test, incumbent_test, obj.cutoff_time)
    training_stats = get_stats(baseline_train, incumbent_train, obj.cutoff_time)

    #print(json.dumps(stats, indent=2))
    
    test_scatter_plot = get_scatter_plot(baseline_test, incumbent_test, options['outputdir'], obj.cutoff_time, True)
    train_scatter_plot = get_scatter_plot(baseline_train, incumbent_train, options['outputdir'], obj.cutoff_time, False)

    test_cactus_plot = get_cactus_plot(baseline_test, incumbent_test, options['outputdir'], obj.cutoff_time, True)
    train_cactus_plot = get_cactus_plot(baseline_train, incumbent_train, options['outputdir'], obj.cutoff_time, False)

    test_cdf_plot = get_cdf_plot(baseline_test, incumbent_test, options['outputdir'], obj.cutoff_time, True)
    train_cdf_plot = get_cdf_plot(baseline_train, incumbent_train, options['outputdir'], obj.cutoff_time, False)

    if options["disable_fanova"]:
        p_not_imps, p_def_imps, fanova_def_plots, fanova_not_plots = [], [], [], []
    else:
        # read configspace
        cs = ConfigSpace(obj.pcs_fn)

        # fANOVA        
        try:
            p_not_imps, fanova_not_plots = get_fanova(obj.get_pyfanova_obj(check_scenario_files = False, improvement_over="NOTHING", heap_size = options['memlimit_fanova']), 
                                      cs, options['outputdir'], improvement_over="NOTHING")
        except:
            traceback.print_exc()
            logging.warn("fANOVA (without capping) failed")
            p_not_imps, fanova_not_plots = [],[]
    
        try:
            p_def_imps, fanova_def_plots = get_fanova(obj.get_pyfanova_obj(check_scenario_files = False, improvement_over="DEFAULT", heap_size = options['memlimit_fanova']), 
                                      cs, options['outputdir'], improvement_over="DEFAULT")
        except:
            traceback.print_exc()
            logging.warn("fANOVA (with capping at default performance) failed")
            p_def_imps, fanova_def_plots = [],[]
    
    plots = {"scatter": {"test" : test_scatter_plot, "train" : train_scatter_plot}, 
             "cactus": {"test" : test_cactus_plot, "train" : train_cactus_plot},
             "cdf": {"test" : test_cdf_plot, "train" : train_cdf_plot},
             "fanova": {"DEFAULT": fanova_def_plots, "NOTHING": fanova_not_plots}}
    
    
    meta = [("#Instances (Test)", "%d" %(len(baseline_test))),
            ("#Instances (Train)", "%d" %(len(baseline_train)))
            ]
    
    read_meta, solver_name = get_meta_data(options['inputdir'])
    meta.extend(read_meta)

    if solver_name is None:
        solver_name = "UNKNOWN"
    
    generate_html(solver_name=solver_name, 
                  meta=meta, 
                  incumbent=obj.data[i]['parameters'][0],
                  test_perf=test_stats,
                  training_perf=training_stats, 
                  param_imp_def=p_def_imps,
                  param_imp_not=p_not_imps, 
                  plots=plots, 
                  out_dir=options['outputdir'])
                 
    try:
        import SpySMAC.utils.pdf_generator
    
        SpySMAC.utils.pdf_generator.generate_pdf(
            solver_name=solver_name, 
            meta=meta, 
            incumbent=obj.data[i]['parameters'][0],
            test_perf=test_stats,
            training_perf=training_stats, 
            param_imp_def=p_def_imps,
            param_imp_not=p_not_imps, 
            plots=plots, 
            out_dir=options['outputdir'])
    except ImportError:
        print("please install ReportLab if you want SpySMAC to generate also a PDF version of the final report.")
    except:
        print("failed generating the pdf")
        traceback.print_exc(file=sys.stdout)
    
    
def get_stats(baseline, configured, cutoff=300):
    '''
         generates a dictionary with par1", "par10", "tos" for "base" and "conf"
    '''
    stats = {"base": {
                      "par1": sum([cutoff if x >= cutoff else x for x in baseline]) / len(baseline),
                      "par10": sum([10*cutoff if x >= cutoff else x for x in baseline]) / len(baseline),
                      "tos": sum([1 if x >= cutoff else 0 for x in baseline]),
                      },
             "conf": {
                      "par1": sum([cutoff if x >= cutoff else x for x in configured]) / len(configured),
                      "par10": sum([10*cutoff if x >= cutoff else x for x in configured]) / len(configured),
                      "tos": sum([1 if x >= cutoff else 0 for x in configured]),
                      },
             "n" :  len(configured)
             }
    return stats

def get_scatter_plot(baseline, configured, out_dir, cutoff, test=True):
    '''
        generate scatter plot
    '''
    if test:
        out_file = os.path.join(out_dir, "scatter_test.png")
        title = "Test Instances"
    else:
        out_file = os.path.join(out_dir, "scatter_train.png")
        title = "Training Instances"
    plot_scatter_plot(baseline, configured, ["Default [sec]", "Configured [sec]"], 
                      max_val=cutoff, linefactors=[2,10,100], title=title,
                      save=out_file)
    if test:
        return "scatter_test.png"
    else:
        return "scatter_train.png"
        
def get_cactus_plot(baseline, configured, out_dir, cutoff, test=True):
    '''
        generate cactus plot
    '''
    #TODO: READ cutoff from somewhere
    
    user_fontsize=20
    
    font = {'size'   : user_fontsize}

    matplotlib.rc('font', **font)
    
    gs = matplotlib.gridspec.GridSpec(1, 1)
    
    fig = plt.figure()
    ax1 = plt.subplot(gs[0:1, :])
    
    #remove timeouts
    baseline = list(filter(lambda x: True if x < cutoff else False, baseline))
    configured = list(filter (lambda x: True if x < cutoff else False, configured))
    
    ax1.plot(np.sort(baseline), marker="x", label="Default")
    ax1.plot(np.sort(configured),color='r', marker="x", label="Configured")

    ax1.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    ax1.set_xlabel("#solved instances")
    ax1.set_ylabel("Runtime [sec]")
    ax1.set_ylim([0,cutoff])

    ax1.legend(loc='upper left')

    if test:
        out_file = os.path.join(out_dir, "cactus_test.png")
        plt.title("Test Instances")
    else:
        out_file = os.path.join(out_dir, "cactus_train.png")
        plt.title("Training Instances")
        
    plt.savefig(out_file, dpi=100, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, pad_inches=0.02, bbox_inches='tight')
    plt.close()
    if test:
        return "cactus_test.png"
    else:
        return "cactus_train.png" 
    
def get_cdf_plot(baseline, configured, out_dir, cutoff, test=True):
    '''
        generate cactus plot
    '''
    #TODO: READ cutoff from somewhere
    
    user_fontsize=20
    
    font = {'size'   : user_fontsize}

    matplotlib.rc('font', **font)
    
    gs = matplotlib.gridspec.GridSpec(1, 1)
    
    fig = plt.figure()
    ax1 = plt.subplot(gs[0:1, :])
    
    #remove timeouts
    #baseline = filter(lambda x: True if x < cutoff else False, baseline)
    #configured = filter(lambda x: True if x < cutoff else False, configured)
    
    def get_x_y(data):
        b_x, b_y, i_s = [], [], 0
        for i, x in enumerate(np.sort(data)):
            b_x.append(x)
            if x < cutoff:
                b_y.append(float(i) /len(data))
                i_s = i
            else: 
                b_y.append(float(i_s) /len(data))
        return b_x, b_y
                
    #print(get_x_y(baseline))
    #print(get_x_y(configured))
                
    #print(get_x_y(baseline)[1])
    #print(get_x_y(baseline)[0])
    ax1.step(get_x_y(baseline)[0], get_x_y(baseline)[1], label="Default")
    ax1.step(get_x_y(configured)[0], get_x_y(configured)[1], color='r', label="Configured")

    ax1.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    ax1.set_xlabel("Runtime [sec]")
    ax1.set_ylabel("P(x<t)")
    #ax1.set_ylim([0,cutoff])
    ax1.set_xscale('log')

    ax1.legend(loc='lower right')

    if test:
        out_file = os.path.join(out_dir, "cdf_test.png")
        plt.title("Test Instances")
    else:
        out_file = os.path.join(out_dir, "cdf_train.png")
        plt.title("Training Instances")
        
    plt.savefig(out_file, dpi=100, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, pad_inches=0.02, bbox_inches='tight')
    if test:
        return "cdf_test.png"
    else:
        return "cdf_train.png"     

def get_fanova(pyfanova, cs, out_dir, improvement_over="DEFAULT"):
    ''' generate parameter importance via fANOVA 
        Args:
            pyfanova: pyFanova object
            cs: ConfigSpac object
            out_dir: Output directory
            improvement_over: capping of fANOVA ("DEFAUL" or "NONE")
    '''
    
    from pyfanova.visualizer import Visualizer
    
    most_important = get_fanova_marginals(pyfanova)
    
    
    vis = Visualizer(pyfanova)
    
    config_space = pyfanova.get_config_space()
    cat_params = config_space.get_categorical_parameters()
    int_params = config_space.get_integer_parameters()
    cont_params = config_space.get_continuous_parameters()
    
    plots = []
    #print(most_important)
    for _,p in most_important:
        
        fig = plt.figure()
        
        log_scale = cs.parameters[p].logged
        
        if p in cat_params:
            logging.info("creating plot for categorical parameter {}".format(p))
            f = vis.plot_categorical_marginal(p)
        elif p in int_params:
            logging.info("creating plot for integer parameter {}".format(p))
            f = vis.plot_marginal(p, is_int=True, log_scale=log_scale)
        elif p in cont_params:
            logging.info("creating plot for continuous parameter {}".format(p))
            f = vis.plot_marginal(p, log_scale=log_scale)
        else:
            logging.error("something went wrong with {}".format(p))
        
        out_name = "%s_fanova_over_%s.png" %(p, improvement_over)
        out_file = os.path.join(out_dir, out_name)
        
        f.savefig(out_file, dpi=100, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, pad_inches=0.02, bbox_inches='tight')
        f.close()
        plots.append(out_name)
    
    return most_important, plots

def get_fanova_marginals(pyfanova, max_num=10):
    '''
        get fanova results and plots for the <max_num> most important parameters
    '''
    
    param_names = pyfanova._config_space.get_parameter_names()
    num_params = len(param_names)

    main_marginal_performances = [pyfanova.get_marginal(i) for i in range(num_params)]
    labelled_performances = []

    for marginal, param_name in zip(main_marginal_performances, param_names):
        labelled_performances.append((marginal, "%.2f%% due to main effect: %s" % (marginal, param_name), param_name))

    sorted_performances = sorted(labelled_performances, reverse=True)
    return_values = []
    if max_num is not None:
        sorted_performances = sorted_performances[:max_num]
    for marginal, label, name in sorted_performances:
        return_values.append((marginal, name))
    return return_values


def get_meta_data(inputdir):
    '''
        read meta data from inputdir and returns a list of tuples with the meta information and the solver binary name
    '''
    meta_data_file = os.path.join(inputdir, "spysmac.meta")
    if not os.path.isfile(meta_data_file):
        logging.warn("Have not found meta data file: %s" %(meta_data_file))
        return [], None
    
    meta_info = []
    solver_name = None
    with open(meta_data_file) as fp:
        for line in fp:
            line = line.replace("\n","").split("=")
            meta_info.append((line[0].strip(" "),line[1].strip(" ")))
            if "binary" in line[0].strip(" "):
                solver_name = os.path.split(line[1].strip(" "))[1]
            
    return meta_info, solver_name

if __name__ == "__main__":
    sys.exit(analyze_simulations(sys.argv))
