#!/usr/local/bin/python2.7
# encoding: utf-8
'''
clasp_cmd_builder -- commandline call builder script for clasp

@author:     Stefan Falkner, Marius Lindauer

@copyright:  2015 AAD Group Freiburg. All rights reserved.

@license:   GPLv2

@contact:   {sfalkner,lindauer}@cs.uni-freiburg.de
'''

def get_command_line_cmd(runargs, conf_dict):
    '''
    Args:
        runargs = {   
                    "instance": str(instance_names[instance%len(instance_names)]),
                    "seed" : seed,
                    "binary" : cmd.split(" ")[0]
                  }
        conf_dict: mapping param_name -> value
    
    '''
    binary_path = runargs["binary"]
    cmd = "%s -config= " %(binary_path) 
    for name, value in conf_dict.items():
            if value == "yes":
                cmd += " -%s" %(name)
            elif value == "no":
                cmd += " -no-%s" %(name)
            else:
                cmd += " -%s=%s" %(name, value)
    cmd += " %s" %(runargs["instance"])
    return cmd
        
