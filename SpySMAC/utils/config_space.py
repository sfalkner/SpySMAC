'''
Created on April 02, 2015

output via logging package

:author: Marius Lindauer
:contact: lindauer@cs.uni-freiburg.de
:copyright: GPLv2

'''

import re
import logging
import random
import numpy
import math

class ParameterType(object):
    '''
        class to define numbers for paramter types
    '''
    categorical = 1
    integer = 2
    float = 3
    
class Parameter(object):
    '''
        Parameter
    '''
    
    def __init__(self, name, type_, values, default, logged=False):
        '''
            Constructor
            
            :param name: name of parameter
            :param type_: type of parameter (see ParameterType)
            :param values: list of possible discrete values or min-max bounds for numerical parameters
            :param default: default value
            :param logged: use log scale of value range (bool)
        ''' 
        
        self.name = name #string
        self.type = type_ #categorial, integer, float
        self.values = values #only 2 values in case of integer and float
        self.default = default 
        self.logged = logged # use log scale on value range
        self._converted_def = None # used for imputing default values in non-active parameters
        
        if self.type not in [ParameterType.categorical, ParameterType.integer, ParameterType.float]:
            logging.error("Wrong type of parameter: %s" %(type))
        
        if self.type == ParameterType.categorical and self.default not in self.values:
            logging.error("Default (%s) of %s is not in values (%s)" %(default, name, ",".join(values)))
        elif self.type in [ParameterType.float, ParameterType.integer] and (self.default > self.values[1] or self.default < self.values[0]):
            logging.error("Default (%f) of %s is not in [%s]" %(default, name, ",".values(list(map(str,values))) ))    
        
        if self.type == ParameterType.categorical:
            self._converted_def = self.values.index(self.default)
        elif self.logged:
            min_, max_ = math.log(self.values[0]), math.log(self.values[1])
            self._converted_def = (math.log(self.default) -  min_) / (max_ - min_)
        else:
            min_, max_ = self.values[0], self.values[1]
            self._converted_def = (self.default -  min_) / (max_ - min_)
            
    def __repr__(self):
        return self.name
            
class Condition():
    '''
        parameter condition whether a parameter is active or not
        parameter <cond> is active if <head> was set with a value in <values>
        
    '''
    
    def __init__(self, head, cond, values, values_indx):
        '''
            Constructor; assumed format: <cond> | <head> in {<values>}
            
            :param head: head parameter name
            :param cond: conditioned parameter name
            :param values: values in clause
            :param values_indx: indexes of <values> according to <head> parameter <values> list

        ''' 
        self.head = head
        self.cond = cond
        self.values = values
        self.values_indx = values_indx
        
    def __repr__(self):
        return "%s | %s in {%s} (%s)" %(self.cond, self.head, ",".join(self.values), ",".join(map(str,self.values_indx)))

class ConfigSpace(object):
    '''
       configuration space
    '''


    def __init__(self, pcs_file):
        '''
        Constructor - reads the pcs file and converts it to internal data structure
       
        :param pcs_file: path to pcs file (str)
        '''
        
        self.parameters = {} # name -> Parameter()
        self.conditions = [] # objects of Condition
        self.forbiddens = [] # tuples of tuples (name, value)
        
        self.__read_pcs(pcs_file)
        
        #: ordering of parameters for vector
        self.__ordered_params = []
        self._sort_params()
        logging.debug(self.__ordered_params)
        
        #: list with booleans whether a parameter is categorical or not
        self._is_cat_list = []
        for p in self.__ordered_params:
            self._is_cat_list.append(self.parameters[p].type == ParameterType.categorical)
        logging.debug(self._is_cat_list)
        
        #: list of number of discrete values for categorical parameters 
        self._cat_size = []
        for p in self.__ordered_params:
            if self.parameters[p].type == ParameterType.categorical:
                self._cat_size.append(len(self.parameters[p].values))
            else:
                self._cat_size.append(0)
        logging.debug(self._cat_size)
        
        #: number of parameters
        self._n_params = len(self.__ordered_params)
        
        #: encoding of conditionals: at index i, conditional for parameter with index, conditional tuple of (head, values)
        self._map_conds = []
        for _ in range(self._n_params):
            self._map_conds.append([])
        self._get_map_conditionals()
        logging.debug(self._map_conds)
        
    def __read_pcs(self, pcs_file):
        ''' 
            reads PCS file and generates data structure
            
            :param pcs_file: path to pcs_file (str)
        '''
        
        num_regex = "[+\-]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)?"
        FLOAT_REGEX = re.compile("^[ ]*(?P<name>[^ ]+)[ ]*\[[ ]*(?P<range_start>%s)[ ]*,[ ]*(?P<range_end>%s)\][ ]*\[(?P<default>%s)\](?P<misc>.*)$" %(num_regex,num_regex, num_regex))
        CAT_REGEX = re.compile("^[ ]*(?P<name>[^ ]+)[ ]*{[ ]*(?P<values>.+)}[ ]*\[(?P<default>[^#]*)\](?P<misc>.*)$")
        COND_REGEX = re.compile("^[ ]*(?P<cond>[^ ]+)[ ]*\|[ ]*(?P<head>[^ ]+)[ ]*in[ ]*{(?P<values>.+)}(?P<misc>.*)$")
        FORBIDDEN_REGEX = re.compile("^[ ]*{(?P<values>.+)}(?P<misc>.*)*$")
        
        with open(pcs_file) as fp:
            for line in fp:
                #remove line break and white spaces
                line = line.strip("\n").strip(" ")
                
                #remove comments
                if line.find("#") > -1:
                    line = line[:line.find("#")] # remove comments
                
                # skip empty lines
                if line  == "":
                    continue
                
                logging.debug(line)
                
                # categorial parameter
                cat_match = CAT_REGEX.match(line)
                if cat_match:
                    logging.debug("CAT MATCH")
                    name = cat_match.group("name")
                    type_ = ParameterType.categorical
                    values = [x.strip(" ") for x in cat_match.group("values").split(",")]
                    default = cat_match.group("default")
                    
                    #logging.debug("CATEGORIAL: %s %s {%s} (%s)" %(name, default, ",".join(map(str, values)), type_))  
                    param = Parameter(name, type_, values, default)
                    self.parameters[name] = param
                    
                float_match = FLOAT_REGEX.match(line)
                if float_match:
                    logging.debug("FLOAT MATCH")
                    name = float_match.group("name")
                    #TODO: log scaling missing, first log and than normalize
                    if "i" in float_match.group("misc"):
                        type_ = ParameterType.integer
                    else:
                        type_ = ParameterType.float
                    if "l" in float_match.group("misc"):
                        logged = True
                    else:
                        logged = False
                    values = [float(float_match.group("range_start")), float(float_match.group("range_end"))]
                    if type_ == ParameterType.integer:
                        default = int(float_match.group("default"))
                    else:
                        default = float(float_match.group("default"))

                    #logging.debug("PARAMETER: %s %f [%s] (%s)" %(name, default, ",".join(map(str, values)), type_))                    
                    param = Parameter(name, type_, values, default, logged)
                    self.parameters[name] = param
                    
                cond_match = COND_REGEX.match(line)
                if cond_match:
                    head = cond_match.group("head")
                    cond = cond_match.group("cond")
                    values = [x.strip(" ") for x in cond_match.group("values").split(",")]
                    
                    #logging.debug("CONDITIONAL: %s | %s in {%s}" %(cond, head, ",".join(values)))
                    
                    head_param = self.parameters[head]
                    value_indxs = []
                    for v in values:
                        value_indxs.append(head_param.values.index(v))
                    
                    cond = Condition(head, cond, values, value_indxs)
                    #print(cond)
                    self.conditions.append(cond)
                    
                forbidden_match = FORBIDDEN_REGEX.match(line)
                if forbidden_match:
                    values = forbidden_match.group("values")
                    values = [x.strip(" ") for x in values.split(",")]
                    values = [x.split("=") for x in values]
                    
                    #logging.debug("FORBIDDEN: {%s}" %(values))
                    
                    self.forbiddens.append(values)
                
    def _sort_params(self):
        '''
            sorts parameters by their conditional parents (first unconditioned parameters) 
            (saves results in self.__ordered_params)
        '''
        
        params = sorted(self.parameters.keys())
        while params:
            for p in params:
                # get parents
                parents = []
                for cond in self.conditions:
                    if p == cond.cond:
                        parents.append(cond.head)
                if not set(parents).difference(self.__ordered_params):
                    self.__ordered_params.append(p)
                    params.remove(p)
                    
    def _get_map_conditionals(self):
        '''
            generate an array with: at categorical child index [parent, values_indx]
            (saves result in self._map_conds)
        '''
        
        for indx, param_name in enumerate(self.__ordered_params):
            for cond in self.conditions:
                if param_name == cond.cond:
                    parent_indx = self.__ordered_params.index(cond.head)
                    self._map_conds[indx].append((parent_indx, cond.values_indx))
                
    def get_default_config_dict(self):
        '''
            returns a configuration (dict: name, value) of the (active) default parameters 
            
            :return: dictionary with name -> value
        '''
        param_dict = dict((p.name,p.default) for p in self.parameters.values())
        
        #remove non-active parameters
        for param in self.__ordered_params:
            param = self.parameters[param]
            active = True
            for cond in self.conditions:
                if param.name == cond.cond:
                    if not param_dict.get(cond.head) or not param_dict.get(cond.head) in cond.values:
                        active = False
                        break
            if not active:
                del param_dict[param.name]
                         
        return param_dict
                
    def get_random_config_vector(self):
        '''
            generates a random configuration vector; uses rejection sampling (can be slow with too many forbidden constraints);
            the parameters are ordered according to self.__ordered_params
            
            :return: random configuration numpy vector (non-active parameters are encoded as numpy.nan)
        '''
        rejected = True
        while rejected: # rejection sampling
            vec = numpy.zeros(self._n_params)
            is_active = []
            for indx in range(self._n_params):
                active = True
                if self._map_conds[indx]: 
                    for cond in self._map_conds[indx]:
                        parent = cond[0]
                        if not is_active[parent]:
                            active = False
                        elif not int(vec[parent]) in cond[1]:
                            active = False
                is_active.append(active)
                
                if active:
                    if self._is_cat_list[indx]:
                        #DEBUG
                        vec[indx] = random.randint(0,self._cat_size[indx]-1)
                        #vec[indx] = random.randint(1 ,self._cat_size[indx])
                    else:
                        vec[indx] = random.random()
                else:
                    vec[indx] = numpy.nan
            
            rejected = self._check_forbidden(vec)
            
        return vec
        
    def _check_forbidden(self, vec):
        '''
            checks whether a configuration vec is forbidden given the pcs
            
            :param vec: parameter configuration vector
            :return: bool whether configuration is forbidden
        '''
        is_forbidden = False
        for forbidden in self.forbiddens:
            hit = True
            for name, value in forbidden:
                #TODO: inefficient - find another way to get parameter index
                p_index = self.__ordered_params.index(name)
                if self._is_cat_list[p_index]:
                    value = self.parameters[name].values.index(value)
                if value != vec[p_index]:
                    hit = False
                    break
            if hit:
                is_forbidden = True
                break
        return is_forbidden
    
        
    def convert_param_dict(self, param_dict):
        '''
            converts a parameter configuration dict (name,value) to the internal vector representation
            assumption: non-active parameters are not present in param_dict (imputed as numpy.nan)
            
            :param param_dict: parameter configuration dictionary (mapping of active parameters to value)
            :return: configuration numpy vector (non-active encoded as numpy.nan)
        '''
        vec = numpy.zeros(self._n_params)
        for indx, p in enumerate(self.__ordered_params):
            value = param_dict.get(p)
            if value is None:
                value = numpy.nan
            elif self._is_cat_list[indx]:
                #DEBUG
                value = self.parameters[p].values.index(value)
                #value = self.parameters[p].values.index(value) + 1
            else:
                value = float(value)
                param_obj = self.parameters[p]
                min_, max_ = param_obj.values
                if param_obj.logged:
                    min_, max_ = math.log(min_), math.log(max_)
                    value = math.log(value)
                value = (value - min_) / (max_ - min_)
            vec[indx] = value
        return vec
        
    def convert_param_vector(self, param_vec):
        '''
            converts a parameter configuration vector to its original dictionary representation
            WARNING: non-active parameters are not represented in the returned dictionary
            
            :param param_vec: parameter configuration vector (non-active encoded as numpy.nan)
            :return: dictionary with active parameter -> value
        '''
        p_dict = {}
        for param, value in zip(self.__ordered_params, list(param_vec)): 
            param = self.parameters[param]
            if numpy.isnan(value):
                continue
            if param.type == ParameterType.categorical:
                #DEBUG
                value = param.values[int(value)]
                #value = param.values[int(value) - 1]
            elif param.type == ParameterType.integer:
                min_, max_ = param.values
                if param.logged:
                    min_, max_ = math.log(min_), math.log(max_)
                    value = int(round(math.exp(value * (max_ - min_ ) + min_)))
                else:
                    value = int(round(value * (max_ - min_ ) + min_))
                
                #print(param.name, value, value * (max_ - min_ ) + min_)
            elif param.type == ParameterType.float:
                min_, max_ = param.values
                if param.logged:
                    min_, max_ = math.log(min_), math.log(max_)
                    value = math.exp(value * (max_ - min_ ) + min_)
                else:
                    value = value * (max_ - min_ ) + min_
            p_dict[param.name] = value
        return p_dict
            
    def get_random_neighbor(self, param_vec):
        '''
            changes one of the active parameters to a neighbor value
            categorical: random.choice
            int/real : gaussian(x_old, 0.1)
            uses only active parameters of <param_vec> 
            -- using rejection sampling to reject non-active parameters and forbidden configurations
            
            :param param_vec: parameter configuration vector
            :return: neighbor parameter vector (neigborhood size 1)
        '''
        
        rejected = True
        while rejected:
            active = False
            while not active: # rejection sampling of inactive parameters and categorical parameters with only one value
                rand_indx = random.randint(0, self._n_params - 1)
                value = param_vec[rand_indx]
                active = not numpy.isnan(value)
                # exclude categorical parameters with only one value
                if self._is_cat_list[rand_indx] and  self._cat_size[rand_indx] < 2:  
                    active = False
            
            if self._is_cat_list[rand_indx]:
                new_value = value
                while new_value == value:
                    #DEBUG
                    new_value = random.randint(0, self._cat_size[rand_indx] - 1)
                    #new_value = random.randint(1, self._cat_size[rand_indx])
                value = new_value
            else:
                value = max(0, min(1, numpy.random.normal(value, 0.1)))
                
            new_param_vec = numpy.copy(param_vec) 
            new_param_vec[rand_indx] = value
        
            new_param_vec = self._fix_active(new_param_vec)
            rejected = self._check_forbidden(new_param_vec)
        
        return new_param_vec
    
    def _fix_active(self, param_vec):
        '''
            fixes values of non-active parameters in a parameter configuration vector - inplace operation!
            
            :param param_vec: set all non-active parameters to numpy.nan
            :return: param_vec
        '''
        
        is_active = []
        for indx in range(self._n_params):
            active = not numpy.isnan(param_vec[indx])
            if active and self._map_conds[indx]: 
                for cond in self._map_conds[indx]:
                    parent = cond[0]
                    if not is_active[parent]:
                        active = False
                    elif not int(param_vec[parent]) in cond[1]:
                        active = False
            is_active.append(active)
            
            if not active:
                param_vec[indx] = numpy.nan
                
        return param_vec
    
    def impute_non_active(self, vec, value=-512):
        '''
            imputes non active parameter values by value if value is a number (no type check!)
            or if value is
                "def": default value of parameters 
                "mean": mean range of parameters
            WARNING: This function does not check which parameter-values are active
            
            :param vec: parameter vector
            :param value: imputation value (numerical)
            :return: parameter vector with numpy.nan values replaced by <value>
        '''
        new_vec = numpy.copy(vec)
        if value == "def":
            for indx in range(self._n_params):
                if numpy.isnan(vec[indx]):
                    param_name = self.__ordered_params[indx]
                    param = self.parameters[param_name]
                    new_vec[indx] = param._converted_def
                else:  
                    new_vec[indx] = vec[indx]
        elif value == "mean":
            for indx in range(self._n_params):
                if numpy.isnan(vec[indx]):
                    is_cat = self._is_cat_list[indx]
                    if is_cat:
                        new_vec[indx] = int(self._cat_size[indx] / 2)
                    else:
                        new_vec[indx] = 0.5
                else:  
                    new_vec[indx] = vec[indx]
        else:
            new_vec[numpy.isnan(vec)] = value
        return new_vec
            
