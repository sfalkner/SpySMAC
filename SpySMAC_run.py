#!/usr/local/bin/python2.7
# encoding: utf-8
'''
pySMAC4SAT -- configuration for SAT

@author:     Stefan Falkner, Marius Lindauer

@copyright:  2015 AAD Group Freiburg. All rights reserved.

@license:   GPLv2

@contact:   {sfalkner,lindauer}@cs.uni-freiburg.de
'''

import os
import sys
import signal
import resource
import imp
import errno

import logging
import random
import subprocess
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import platform

#adjust the PYTHON_PATH to find the submodules
spysmac_path = os.path.dirname(os.path.realpath(__file__))
sys.path =[ os.path.join(spysmac_path, "pysmac"),
            os.path.join(spysmac_path, "pynisher"),
            os.path.join(spysmac_path, "cpuinfo")] + sys.path

import pysmac
import pysmac.utils

from cpuinfo.cpuinfo import get_cpu_info

__version__ = 0.2
__date__ = '2015-03-18'
__updated__ = '2015-05-20'

# for DEBUG purposes?
random.seed(12345)

instance_names = []
cmd = ''
parameter_string_template = ''


def sat_function(instance=None, seed=None,  **kwargs):
    # construct the command for the run
    global instance_names
    global cmd
    global parameter_string_template
    global cmd_builder_script

    if cmd_builder_script is None:
        cmd = cmd.replace("<instance>", str(instance_names[instance%len(instance_names)]))
        cmd = cmd.replace("<seed>", str(seed))
        cmd = cmd.replace('<params>', ' '.join(
            [parameter_string_template % (k, kwargs[k]) for k in kwargs]))
            
        logging.info("Issuing algorithm run with command\n{}".format(cmd))
    
    else: 
        loaded_script = imp.load_source("cmd_builder", cmd_builder_script)
        runargs = {   "instance": str(instance_names[instance%len(instance_names)]),
                      "seed" : seed,
                      "binary" : cmd.split(" ")[0]
                   }
        cmd = loaded_script.get_command_line_cmd(runargs, kwargs)
        
    cmd = cmd.split()

    # set up the signal handle to catch all the signals for proper
    # cleaning up, i.e. killing the SAT solver.
    p = None

    def signal_handler(signum, frame):
        try:
            p.terminate()
        except:
            logging.debug("Killing the SAT solver failed. "
                          "It probably finished already.")
        logging.debug('Exiting because signal %d was received' % signum)
        exit(1)

    signal.signal(signal.SIGALRM, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGXCPU, signal_handler)

    # actually run the solver in a separate process and grab its output
    logging.debug("CALL: " +" ".join(cmd))

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    logging.debug("Solver output:\n%s\n"%stdout)

    # record cpu time with ('arbitrary') lower cutoff
    cpu_time =  resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime +\
                 resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime
    rt = max(cpu_time, 0.05)

    return_dict = {'value':1, 'runtime':rt}
    if b'UNSATISFIABLE' in stdout:  return_dict['status'] = b'UNSAT'
    elif b'SATISFIABLE' in stdout:  return_dict['status'] = b'SAT'
    else: return_dict['status'] = b'TIMEOUT'
    return(return_dict)

def find_instances(instance_ref):
    logging.info("Read Files from {}".format(instance_ref))
    instances = []
    if os.path.isfile(instance_ref):
        with open(instance_ref) as fp:
            for inst in fp:
                inst = inst.rstrip("\n")
                if os.path.isfile(inst):
                    instances.append(inst)
                else:
                    logging.warn("Not found: %s" % inst)

    elif os.path.isdir(instance_ref):
        for root, dirs, files in os.walk(instance_ref):
            for file_ in files:
                if file_.endswith(".cnf") or file_.endswith(".cnf.gz"):
                    instances.append(os.path.join(root, file_))

    if not instances:
        logging.error("No instances found!")
        sys.exit(1)
    return(instances)


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

    req_params.add_argument("-i", "--training-instances", required=True,
                            help="problem instance directory or file with list"
                                "of instances (only cnf supported)")

    req_params.add_argument("-b", "--binary", required=True,
                            help="binary of solver")

    req_params.add_argument("-p", "--pcs", required=True, help="pcs file")

    req_params.add_argument("-o", "--outputdir", required=True,
                            help="output directory",
                            default='.')

    opt_params = parser.add_argument_group("Optional")

    opt_params.add_argument("-B", "--budget", default=None, type=int,
                            help="configuration budget per SMAC run "
                            "(default: 200* cutoff)")

    opt_params.add_argument("-c", "--cutoff", default=900, type=int,
                            help="runtime cutoff of target algorithm (sec)")

    opt_params.add_argument("-r", "--repetitions", default=1, type=int,
                            help="number of independent runs of SMAC")

    opt_params.add_argument("-s", "--seed", default=1, type=int,
                            help="initial seed used for the first run. "
                            "Additional runs use consecutive values. Use 0 to "
                            "validate the default configuration.")

    opt_params.add_argument("-f", "--validation-fraction", default=0.5,
                            type=float,
                            help="fraction of instances used for validation"
                            "; The rest is used for configuration.")

    opt_params.add_argument("-I", "--validation-instances", default=None,
                            help="problem  instances that are used for "
                            "tuning, the rest will be used for validation.")

    opt_params.add_argument("-n", "--num-procs", default=1, type=int,
                            help="number of available processors/cores to run "
                            "SMAC in parallel")

    opt_params.add_argument("-m", "--memory", default=2000, type=int,
                            help="memory cutoff of target algorithm (mb)")

    opt_params.add_argument("-P", "--prefix",           default="--",
                            help="parameter name prefix")

    opt_params.add_argument("-S", "--separator", default="=",
                            help="separator between parameter name and value "
                            "(e.g., --<name>=<value>")

    opt_params.add_argument("-C", "--callstring", default="<params> <instance>",
                            help="call string of your solver - use the place "
                            "holder: <instance>, <tempdir>, <seed>, <params>")
    
    opt_params.add_argument("--cmd_builder_script", default=None,
                            help="your own Python script with a function "
                            "get_command_line_cmd(runargs, config) "
                            "to implement your own cmd call builder")

    opt_params.add_argument("-v", "--verbosity", default="INFO",
                            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                            help="verbosity level")

    opt_params.add_argument('-V', '--version',  action='version',
                            version=program_version_message)

    # Process arguments
    args = parser.parse_args(argv[1:])

    if args.verbosity == "INFO":
        logging.basicConfig(level=logging.INFO,
                            format="[%(levelname)s]: %(message)s")
    elif args.verbosity == "DEBUG":
        logging.basicConfig(level=logging.DEBUG,
                            format="[%(levelname)s]: %(message)s")
    elif args.verbosity == "WARNING":
        logging.basicConfig(level=logging.WARNING,
                            format="[%(levelname)s]: %(message)s")
    elif args.verbosity == "ERROR":
        logging.basicConfig(level=logging.ERROR,
                            format="[%(levelname)s]: %(message)s")

    if not args.budget:
        args.budget = args.cutoff * 200

    if not os.path.isfile(args.binary):
        logging.error("Could not find the binary: %s" %(args.binary))
        sys.exit(3)

    logging.debug(str(vars(args)))

    return(vars(args))


def run_simulations(args):

    global instance_names
    global cmd
    global parameter_string_template
    global cmd_builder_script
    
    # parse the arguments, find the instances and read the pcs file
    options = parse_args(args)

    cmd_builder_script = options['cmd_builder_script']

    logging.info("Setting up simulations in '%s'"%options['outputdir'])

    instance_names = find_instances(options['training_instances'])
    # in case the validation-fraction option is used    
    if options['validation_instances'] is None:
        instance_names = find_instances(options['training_instances'])
        random.shuffle(instance_names)

        num_test_instances = int(len(instance_names) * options['validation_fraction'])
        num_train_instances= len(instance_names) - num_test_instances
    else: # if a specific set of validation instances was specified
        test_instances = find_instances(options['validation_instances'])
        num_train_instances = len(instance_names)
        num_test_instances  = len(test_instances)
        instance_names = instance_names + test_instances

    if (num_train_instances < 1 or num_test_instances <1):
        logging.error("Unable to create a training-test split from "
                      "the instances you provided!")
        sys.exit(2)


    param_dict, conditions, forbiddens = pysmac.utils.read_pcs(options['pcs'])

    logging.debug("Params: %s" % (str(list(param_dict.keys()))))
    logging.debug("Params: %s" % (str(param_dict)))

    parameter_string_template = ("%s" % options['prefix']) +\
        '%s' + ('%s' % options['separator']) + '%s'
    cmd = "%s %s" % (options['binary'], options['callstring'])

    smac_debug = False if options['verbosity'] != 'DEBUG' else True

    # for the special seed 0, 
    if options['seed'] == 0:

        # make sure that the output directory exists
        try:
            os.makedirs(options['outputdir'])
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        # store meta information in a file for the report        
        with open(os.path.join(options['outputdir'], 'spysmac.meta'),'w') as fh:
            
            # os information
            fh.write("os system = {}\n".format(platform.system()))
            fh.write("os release = {}\n".format(platform.release()))
            
            # cpu info
            info = get_cpu_info()
            fh.write("cpu vendor = {}\n".format(info['vendor_id']))
            fh.write("cpu brand = {}\n".format(info['brand']))
            fh.write("cpu hz = {}\n".format(info['hz_advertised']))
            fh.write("cpu arch = {}\n".format(info['arch']))
            fh.write("cpu count = {}\n".format(info['count']))
            
            # spysmacs run options
            for (k,v) in list(options.items()):
                fh.write("{} = {}\n".format(k,v))

	    # pcs information
	    for key in param_dict.keys():
	    	fh.write("%s = %s\n" % (key, param_dict[key][1]))
        
        # make sure no time is wasted and go directly to the validation
        options['repetitions'] = 1
        options['budget'] = 1

    smac = pysmac.optimizer.SMAC_optimizer(deterministic=False,
                                 t_limit_total_s=options['budget'],
                                 mem_limit_smac_mb=1024,
                                 working_directory=options['outputdir'],
                                 persistent_files=True, debug=smac_debug)

    # adjust some advanced SMAC options here
    smac.smac_options['wallclock-limit'] = options['budget']
    smac.smac_options['run-obj'] = 'RUNTIME'
    smac.smac_options['overall_obj']='MEAN10'
    if options['seed'] == 0:
        smac.smac_options['scenario_fn'] = 'default_validation_scenario.dat'


    with open(os.path.join(options['outputdir'],'shuffled_instances.txt'),'w') as fh:
        fh.write('\n'.join(instance_names))

    logging.info('Starting SMAC...')
    num_evals = 2**31-1 if options['seed'] > 0 else 1
    
    smac.minimize(sat_function, num_evals, param_dict, conditions,
                        forbiddens, num_instances=num_train_instances,
                        num_test_instances=num_train_instances+num_test_instances,
                        seed=options['seed'], num_procs=options['num_procs'],
                        num_runs=options['repetitions'],
                        mem_limit_function_mb=options['memory'],
                        t_limit_function_s=options['cutoff'])

if __name__ == "__main__":
    sys.exit(run_simulations(sys.argv))
