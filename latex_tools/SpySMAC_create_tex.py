#!/usr/local/bin/python2.7
# encoding: utf-8

'''
APGMFAC -- Automated Paper-Generation Machine for Algorithm Configuration

@author:     Julian Kunzelmann
'''

import os
import json

def SpySMAC_create_tex(solver_name, meta, incumbent, test_perf, training_perf,
                   param_imp_def, param_imp_not, plots, out_dir, tex_style,
                   baseline_train,baseline_test, incumbent_train, incumbent_test,
		   cdf_values_baseline_training, cdf_values_incumbent_training,
		   cdf_values_baseline_test, cdf_values_incumbent_test):
    """
	Generates automatically a paper out of the analysed data of SpySMAC.

	Args:
		solver_name (str):	The name of the used solver.

		meta (list):	A list of tuples containing the title and the specific
				value for the meta information. Both as str.

		incumbent (dict):	This dictionary represents each parameter of the
					solver and the corresponding optimized configuration.
					Both as str.

		test_perf (dict):	In this dictionary are the PAR10 scores, average runtimes,
					and timeout for the test instances. Inside this dictionary 
					are two further dictionaries. One for the base configuration
					and one for the optimized configuration. And furthermore 
					the key-value pair for the amount of test instances. 	

		training_perf (dict):	In this dictionary are the PAR10 scores, average runtimes,
					and timeout for the training instances. Inside this dictionary 
					are two further dictionaries. One for the base configuration
					and one for the optimized configuration. And furthermore 
					the key-value pair for the amount of training instances.

		param_imp_def (list):   Contains the importance of each parameter estimated by fANOVA. 
					Therefore fANOVA only considered parameter settings, which were
					able to outperform the default configuration. Each list entry is
					a tuple with the importance of the parameter and parameter name.

		param_imp_not (list):	Contains the importance of each parameter estimated by fANOVA.
					Each list entry is a tuple with the importance of the parameter
					and parameter name.

		plots (dict):		The name of the plots. The keys are the types of the plots and
					the values are dictionaries for the corresponding training and
					test plots.

		out_dir (str):		The path to the output directory

		tex_style (str):	Name of the template to use. Possible templates are ijcai13,
					aaai or llncs. Else the article class will be used.

		baseline_train (numpy.ndarray):	Runtime list for the training instances achieved with
						the default configuration.

		baseline_test (numpy.ndarray):	Runtime list for the test instances achieved with
						the default configuration.

		incumbent_train	(numpy.ndarray):	Runtime list for the training instances 
							achieved with the optimized configuration.

		incumbent_test (numpy.ndarray):	Runtime list for the test instances achieved with
						the optimized configuration.

		cdf_values_baseline_training (tuple):	Runtime list and percentage of solved instances
							list. Within the runtime of entry i of the
							runtime list the solver was able to solve the
							percentage of entry i of the percentage of
							solved instances list. Here for the default
							configuration and the training instances.

		cdf_values_incumbent_training (tuple):	Runtime list and percentage of solved instances
							list. Within the runtime of entry i of the
							runtime list the solver was able to solve the
							percentage of entry i of the percentage of
							solved instances list. Here for the optimized
							configuration and the training instances.

		cdf_values_baseline_test (tuple):	Runtime list and percentage of solved instances
							list. Within the runtime of entry i of the
							runtime list the solver was able to solve the
							percentage of entry i of the percentage of
							solved instances list. Here for the default
							configuration and the test instances.

		cdf_values_incumbent_test (tuple):	Runtime list and percentage of solved instances
							list. Within the runtime of entry i of the
							runtime list the solver was able to solve the
							percentage of entry i of the percentage of
							solved instances list. Here for the optimized
							configuration and the test instances.

	Returns:
		Nothing

    """

    # Load the text dictionary out of the json file
    with open("latex_tools/text_dictionary.json") as json_file:
        json_data = json.load(json_file)

    # Generates the tex file
    with open("%s/SpySMACReport.tex" % (out_dir), "wb") as texfile:

        tex_template_processing(texfile=texfile, tex_style=tex_style, json_data=json_data, solver_name=solver_name)
        
	texfile.write("\\usepackage{hyperref} \n")

        texfile.write("\\title{\\textbf{%s}}\n" % (json_data["title"].replace("$<$SOLVER$>$",solver_name)))
        texfile.write("\\author{%s\\\\ \n" % (json_data["author"]))
        texfile.write("%s}\n" % (json_data["institution"]))
        texfile.write("\\date{%s} \n" % (json_data["date"]))

        texfile.write("\\begin{document}  \n")
        texfile.write("\\maketitle \n")

        texfile.write("\\section{%s} \n" %  (json_data["sections"]["introduction"]))
        texfile.write("%s \n" % (json_data["introduction_text"]))
        texfile.write("\\FloatBarrier \n")
 
        texfile.write("\\section{%s} \n" % (json_data["sections"]["algorithm_description"]))
        texfile.write("%s" % (json_data["algorithm_description_placeholder"]))
        texfile.write("\\FloatBarrier \n")

        texfile.write("\\section{%s} \n" % (json_data["sections"]["benchmark"]))
	
        # Meta data processing
        texfile.write("\\subsection{%s} \n" % (json_data["sections"]["setup"]))
        texfile.write("\\begin{table}[thbH!] \n")
        texfile.write("\\centering \n")
        texfile.write("\\caption{%s} \n" % (json_data["captions"]["meta_data"]))
        texfile.write("\\begin{tabular}{ p{0.45\\columnwidth} | p{0.45\\columnwidth} }  \n")

        # Reads meta data and transforms it into LaTeX style
        texfile.write("Solver &	%s \\\\ \n" % (solver_name))
	texfile.write("\\hline \n")
	
	texfile.write("Number of training instances & %s \\\\ \n" % (meta[1][1]))
	texfile.write("\\hline \n")

	texfile.write("Number of test instances & %s \\\\ \n" % (meta[0][1]))
        texfile.write("\\hline \n")	

	texfile.write("Operating System & %s %s \\\\ \n" % (meta[2][1], meta[3][1]))
        texfile.write("\\hline \n")

	texfile.write("CPU & %s \\\\ \n" % (meta[5][1]))
        texfile.write("\\hline \n")

	texfile.write("Number of CPU cores & %s \\\\ \n" % (meta[8][1]))
        texfile.write("\\hline \n")

	texfile.write("Runtime cutoff of target algorithm run in seconds & %s \\\\ \n" % (meta[10][1]))
        texfile.write("\\hline \n")

	texfile.write("Memory limit of target algorithm run in megabytes & %s \\\\ \n" % (meta[9][1]))
	texfile.write("\\hline \n")

	texfile.write("Independent SMAC runs & %s  \\\\ \n" % (meta[16][1]))
	texfile.write("\\hline \n")

	texfile.write("Configuration budget in seconds & %s \\\\ \n" % (meta[17][1]))
	texfile.write("\\hline \n")

	texfile.write("Used CPU cores & %s \\\\ \n" % (meta[18][1]))
	texfile.write("\\hline \n")

        texfile.write("\\end{tabular} \n")
        texfile.write("\\end{table} \n")

        texfile.write("\\FloatBarrier \n")

        texfile.write("\\subsection{%s} \n" % (json_data["sections"]["problem_instances"]))

        texfile.write("%s \n" % (json_data["description_of_instances"]))
        texfile.write("\\FloatBarrier \n")

        texfile.write("\\section{%s} \n" % (json_data["sections"]["configuration"]))

        # Algorithm Peformance
        texfile.write("\\subsection{%s} \n" % (json_data["sections"]["performance_overview"]))

        texfile.write("\\begin{table}[thbH!] \n")
        texfile.write("\\centering \n")
        texfile.write("\\caption{%s} \n" % (json_data["captions"]["parameter_configuration"]))
        texfile.write("\\begin{tabular}{ p{0.3\\columnwidth} | p{0.3\\columnwidth} | p{0.3\\columnwidth} } \n")
        texfile.write(" %s & %s & %s \\\\ \n" % (json_data["table_entries"]["parameter"],
                                              json_data["table_entries"]["parameter_setting_default"],
					      json_data["table_entries"]["parameter_setting_configured"]))

        for key, value in list(incumbent.items()):
	  for meta_key, meta_value in meta:
		if meta_key == key:
			metavalue = meta_value

          # Read the parameter settings
          texfile.write("\\hline \n")
	  if (metavalue != value):
          	texfile.write("\\textbf{%s} & $\\textbf{%.15s}$ & $\\textbf{%.15s}$\\\\ \n" % (key, metavalue, value))
	  else:
		texfile.write("%s & $%.15s$ & $%.15s$\\\\ \n" % (key, metavalue, value))

        
        texfile.write("\\end{tabular} \n")
        texfile.write("\\end{table} \n")

        texfile.write("\\FloatBarrier \n")

        # Quantity calculation
        baseline_train_greater_than_incumbent_train = 0
        baseline_train_equal_incumbent_train = 0
        baseline_train_less_than_incumbent_train = 0

        baseline_test_greater_than_incumbent_test = 0
        baseline_test_equal_incumbent_test = 0
        baseline_test_less_than_incumbent_test = 0

        for i in range(len(baseline_train)):
          if baseline_train[i] > incumbent_train[i]:
            baseline_train_greater_than_incumbent_train += 1
          elif baseline_train[i] == incumbent_train[i]:
            baseline_train_equal_incumbent_train += 1
          else:
            baseline_train_less_than_incumbent_train += 1

        for i in range(len(baseline_test)):
          if baseline_test[i] > incumbent_test[i]:
            baseline_test_greater_than_incumbent_test += 1
          elif baseline_test[i] == incumbent_test[i]:
            baseline_test_equal_incumbent_test += 1
          else:
            baseline_test_less_than_incumbent_test += 1
      
	if baseline_train_equal_incumbent_train > 0:
        	texfile.write("%s \\\\ \n" % (json_data["quantity_result_train"].replace("$<$baseline_train_less_than_incumbent_train$>$",
                	                                                 str(baseline_train_less_than_incumbent_train)).replace(
	        	                                                 "$<$baseline_train_equal_incumbent_train$>$",
									 str(baseline_train_equal_incumbent_train)).replace(
									 "$<$baseline_train_greater_than_incumbent_train$>$",
									 str(baseline_train_greater_than_incumbent_train))))
	else:
        	texfile.write("%s \\\\ \n" % (json_data["quantity_result_train"].replace("$<$baseline_train_less_than_incumbent_train$>$",
                	                                                 str(baseline_train_less_than_incumbent_train)).replace(
					      ", equally fast for $<$baseline_train_equal_incumbent_train$>$ training instances","").replace(
									 "$<$baseline_train_greater_than_incumbent_train$>$",
									 str(baseline_train_greater_than_incumbent_train))))

	if baseline_test_equal_incumbent_test > 0:	
        	texfile.write("%s \\\\ \n" % (json_data["quantity_result_test"].replace("$<$baseline_test_less_than_incumbent_test$>$",
                                                                 str(baseline_test_less_than_incumbent_test)).replace(
	                                                         "$<$baseline_test_equal_incumbent_test$>$",
								 str(baseline_test_equal_incumbent_test)).replace(
								 "$<$baseline_test_greater_than_incumbent_test$>$",
								 str(baseline_test_greater_than_incumbent_test))))
	else:
        	texfile.write("%s \\\\ \n" % (json_data["quantity_result_test"].replace("$<$baseline_test_less_than_incumbent_test$>$",
                	                                                 str(baseline_test_less_than_incumbent_test)).replace(
					      ", equally fast for $<$baseline_test_equal_incumbent_test$>$ test instances","").replace(
									 "$<$baseline_test_greater_than_incumbent_test$>$",
									 str(baseline_test_greater_than_incumbent_test))))

        # Training Performance (Table)
        texfile.write("\\begin{table}[thbH!] \n")
        texfile.write("\\centering \n")
        texfile.write("\\caption{%s} \n" % (json_data["captions"]["training_performance"]))
        texfile.write("\\begin{tabular}{ p{0.3\\columnwidth} | p{0.3\\columnwidth} | p{0.3\\columnwidth} } \n")
        texfile.write(" & %s & %s \\\\ \n" % (json_data["table_entries"]["default_parameters"],
                                              json_data["table_entries"]["configured_parameters"]))
        texfile.write("\\hline \n")

        # Read the performance data
        texfile.write("%s & $%.2f$ & $%.2f$ \\\\ \n" % (json_data["table_entries"]["average_runtime"],
                                                        training_perf['base']['par1'],
                                                        training_perf['conf']['par1']))
        texfile.write("\\hline \n")
        texfile.write("%s & $%.2f$ & $%.2f$ \\\\ \n" % (json_data["table_entries"]["par10_score"],
                                                        training_perf['base']['par10'],
                                                        training_perf['conf']['par10']))
        texfile.write("\\hline \n")
        texfile.write("%s & $%s$ & $%s$ \n" % (json_data["table_entries"]["algorithm_timeouts"],
                                               str(training_perf['base']['tos']) +
                                               "/" + str(meta[0][1]),
                                               str(training_perf['conf']['tos']) +
                                               "/" + str(meta[1][1])))
        texfile.write("\\end{tabular} \n")
        texfile.write("\\end{table} \n")

        # Test Performance (Table)
        texfile.write("\\begin{table}[thbH!] \n")
        texfile.write("\\centering \n")
        texfile.write("\\caption{%s} \n" % (json_data["captions"]["test_performance"]))
        texfile.write("\\begin{tabular}{ c | c | c } \n")
        texfile.write(" & %s & %s \\\\ \n" % (json_data["table_entries"]["default_parameters"],
                                              json_data["table_entries"]["configured_parameters"]))
        texfile.write("\\hline \n")

        # Read the performance data
        texfile.write("%s & $%.2f$ & $%.2f$ \\\\ \n" % (json_data["table_entries"]["average_runtime"],
                                                        test_perf['base']['par1'],
                                                        test_perf['conf']['par1']))
        texfile.write("\\hline \n")
        texfile.write("%s & $%.2f$ & $%.2f$ \\\\ \n" % (json_data["table_entries"]["par10_score"],
                                                        test_perf['base']['par10'],
                                                        test_perf['conf']['par10']))
        texfile.write("\\hline \n")
        texfile.write("%s & $%s$ & $%s$ \n" % (json_data["table_entries"]["algorithm_timeouts"],
                                               str(test_perf['base']['tos']) + "/" +
                                               str(meta[0][1]), str(test_perf['conf']['tos']) +
                                               "/" + str(meta[1][1])))
        texfile.write("\\end{tabular} \n")
        texfile.write("\\end{table} \n")

        texfile.write("\\FloatBarrier \n")

        # Scatter Plots
        texfile.write("\\subsection{%s} \n" % (json_data["sections"]["scatter_plots"]))
        texfile.write("%s \n" % (json_data["description_of_scatter_plots"]))

        # Scatter Plot for the training instances
        texfile.write("\\begin{figure}[thbH!] \n")
        texfile.write("\\centering \n")
        texfile.write("\\includegraphics[width=0.8\\columnwidth] " +
                     "{Plots/scatter_train.png} \n")
        texfile.write("\\caption{Scatter Plot for the training instances} \n")
        texfile.write("\\end{figure} \n")

        # Scatter Plot for the test instances
        texfile.write("\\begin{figure}[thbH!] \n")
        texfile.write("\\centering \n")
        texfile.write("\\includegraphics[width=0.8\\columnwidth] " +
                     "{Plots/scatter_test.png} \n")
        texfile.write("\\caption{Scatter Plot for the test instances} \n")
        texfile.write("\\end{figure} \n")

        texfile.write("\\FloatBarrier \n")

        # Cumulative Distribution Function Plots
        texfile.write("\\subsection{%s} \n" % (json_data["sections"]["cdf_plots"]))
	texfile.write("%s \\\\ \n" % (json_data["description_of_cumulative_distribution_function"]))

        # Plot for the training instances
        texfile.write("\\begin{figure}[thbH!] \n")
        texfile.write("\\centering \n")
        texfile.write("\\includegraphics[width=0.8\\columnwidth]{Plots/cdf_train.png} \n")
        texfile.write("\\caption{%s} \n" % (json_data["captions"]["cumulative_distribution_training"]))
        texfile.write("\\end{figure} \n")

	i = 0
	j = 0
	betterOneListTraining = [("start", 0, 0)]
	while (i != len(cdf_values_baseline_training[0]) - 1 or j != len(cdf_values_incumbent_training[0]) - 1):
		if (i == len(cdf_values_baseline_training[0]) - 1):
			j = j + 1
		elif (j == len(cdf_values_incumbent_training[0]) - 1 ):
			i = i + 1
		elif (cdf_values_baseline_training[0][i + 1] < cdf_values_incumbent_training[0][j + 1]):
			i = i + 1
		elif (cdf_values_baseline_training[0][i + 1] > cdf_values_incumbent_training[0][j + 1]):
			j = j + 1
		elif (cdf_values_baseline_training[0][i + 1] == cdf_values_incumbent_training[0][j + 1]):
			i = i + 1
			j = j + 1
		if (i < j):
			if (float(cdf_values_incumbent_training[0][j]) == float(meta[10][1])):
				break
			if (betterOneListTraining[len(betterOneListTraining) - 1][0] != "optimized"):
				betterOneListTraining.append(("optimized", cdf_values_baseline_training[0][i], cdf_values_incumbent_training[0][j]))
			
		elif (i > j):
			if (float(cdf_values_baseline_training[0][j]) == float(meta[10][1])):
				break
			if (betterOneListTraining[len(betterOneListTraining) - 1][0] != "default"):
				betterOneListTraining.append(("default", cdf_values_baseline_training[0][i], cdf_values_incumbent_training[0][j]))
		else:
			if (float(min(cdf_values_baseline_training[0][i], cdf_values_incumbent_training[0][j])) == float(meta[10][1])):
				break

	i = 0
	j = 0
	betterOneListTest = [("start", 0, 0)]
	while (i != len(cdf_values_baseline_test[0]) - 1 or j != len(cdf_values_incumbent_test[0]) - 1):
		if (i == len(cdf_values_baseline_test[0]) - 1):
			j = j + 1
		elif (j == len(cdf_values_incumbent_test[0]) - 1 ):
			i = i + 1
		elif (cdf_values_baseline_test[0][i + 1] < cdf_values_incumbent_test[0][j + 1]):
			i = i + 1
		elif (cdf_values_baseline_test[0][i + 1] > cdf_values_incumbent_test[0][j + 1]):
			j = j + 1
		elif (cdf_values_baseline_test[0][i + 1] == cdf_values_incumbent_test[0][j + 1]):
			i = i + 1
			j = j + 1
		if (i < j):
			if (float(cdf_values_incumbent_test[0][j]) == float(meta[10][1])):
				break
			if (betterOneListTest[len(betterOneListTest) - 1][0] != "optimized"):
				betterOneListTest.append(("optimized", cdf_values_baseline_test[0][i], cdf_values_incumbent_test[0][j]))
			
		elif (i > j):
			if (float(cdf_values_baseline_test[0][j]) == float(meta[10][1])):
				break
			if (betterOneListTest[len(betterOneListTest) - 1][0] != "default"):
				betterOneListTest.append(("default", cdf_values_baseline_test[0][i], cdf_values_incumbent_test[0][j]))
		else:
			if (float(min(cdf_values_baseline_test[0][i], cdf_values_incumbent_test[0][j])) == float(meta[10][1])):
				break

        # Cumulative Distribution Function Plot for the test instances
        texfile.write("\\begin{figure}[thbH!] \n")
        texfile.write("\\centering \n")
        texfile.write("\\includegraphics[width=0.8\\columnwidth]{Plots/cdf_test.png} \n")
        texfile.write("\\caption{%s} \n" % (json_data["captions"]["cumulative_distribution_test"]))
        texfile.write("\\end{figure} \n")


	for i in range(1, len(betterOneListTraining)):
		if (i == len(betterOneListTraining) - 1):
			texfile.write("%s" % (json_data["runtime_distribution_comparison_training_cutoff"].replace("<Solver>", solver_name).replace("<better>", betterOneListTraining[i][0]).replace("<first_time>", str(betterOneListTraining[i][2])))) 

		else:
			texfile.write("%s" % (json_data["runtime_distribution_comparison_training"].replace("<Solver>", solver_name).replace("<better>", betterOneListTraining[i][0]).replace("<first_time>", str(betterOneListTraining[i][2])).replace("<second_time>", str(betterOneListTraining[i + 1][2]))))

	texfile.write("\\\\ \n")


	for i in range(1, len(betterOneListTest)):
		if (i == len(betterOneListTest) - 1):
			texfile.write("%s" % (json_data["runtime_distribution_comparison_test_cutoff"].replace("<Solver>", solver_name).replace("<better>", betterOneListTest[i][0]).replace("<first_time>", str(betterOneListTest[i][2]))))

		else:
			texfile.write("%s" % (json_data["runtime_distribution_comparison_test"].replace("<Solver>", solver_name).replace("<better>", betterOneListTest[i][0]).replace("<first_time>", str(betterOneListTest[i][2])).replace("<second_time>", str(betterOneListTest[i + 1][2]))))			
        
	texfile.write("\n")
	texfile.write("\\FloatBarrier \n")

	# Writes the fANOVA part, depending on the command line arguments
	if param_imp_def != []:

		texfile.write("\\section{%s} \n" % (json_data["sections"]["fanova"]))

		texfile.write("\\subsection{%s} \n" % (json_data["sections"]["parameter_importance"]))


		texfile.write("%s \n" % (json_data["description_of_fanova"]))

		# Parameter Performance marginalized over all settings
		texfile.write("\\begin{table}[thbH!] \n")
		texfile.write("\\centering \n")
		texfile.write("\\caption{%s} \n" % (json_data["captions"]["parameter_importance_over_nothing"]))
		texfile.write("\\begin{tabular}{ c | c } \n")
		texfile.write("\\label{tab:parameter_importance}")
		texfile.write("%s & %s \\\\ \n" % (json_data["table_entries"]["parameter"],
		                                   json_data["table_entries"]["parameter_importance"]))

		important_parameters_over_nothing = []

		for marginal, parameter in param_imp_not:
		        texfile.write("\\hline \n")
		        texfile.write("%s & $%.2f$ \\\\ \n" % (parameter, marginal))
		        if marginal > 1:
		          important_parameters_over_nothing.append(parameter)
		texfile.write("\\end{tabular} \n")
		texfile.write("\\end{table} \n")

		if len(important_parameters_over_nothing) > 0:
		  texfile.write("The parameters ")
		  for i in range(len(important_parameters_over_nothing)):
		    texfile.write(str(important_parameters_over_nothing[i]))
		    if i == len(important_parameters_over_nothing) - 2 and len(important_parameters_over_nothing) > 1:
		      texfile.write(" and ")
		    elif i != len(important_parameters_over_nothing) - 1:
		      texfile.write(", ")
		  texfile.write(" explain at least $1\%$ of the performance variance. \n")


		for j in range(len(param_imp_not)):
		        texfile.write("\\begin{figure}[thbH!] \n")
		        texfile.write("\\centering \n")
		        texfile.write("\\includegraphics[width=0.8\\columnwidth]" +
		                     "{Plots/%s_fanova_over_NOTHING.png} " % (param_imp_not[j][1]) +
		                      "\n")
		        texfile.write("\\caption{%s %s} \n" % (json_data["captions"]["parameter_importance_plot_over_nothing"],
		                                               param_imp_not[j][1]))
		        texfile.write("\\end{figure} \n")
			texfile.write("\\FloatBarrier \n")

		texfile.write("\\FloatBarrier \n")

		texfile.write("\\subsection{%s} \n" % (json_data["sections"]["parameter_importance_good_configurations"]))

		# Parameter Performance marginalized over the good performing settings
		texfile.write("\\begin{table}[thbH!] \n")
		texfile.write("\\centering \n")
		texfile.write("\\caption{%s} \n" % (json_data["captions"]["parameter_importance_over_default"]))
		texfile.write("\\begin{tabular}{ p{0.45\\columnwidth} | p{0.45\\columnwidth} } \n")
		texfile.write("%s & %s \\\\ \n" % (json_data["table_entries"]["parameter"],
		                                   json_data["table_entries"]["parameter_importance"]))

		important_parameters_over_default = []

		for marginal, parameter in param_imp_def:
		  texfile.write("\\hline \n")
		  texfile.write("%s & $%.2f$ \\\\ \n" % (parameter, marginal))
		  if marginal > 1:
		    important_parameters_over_default.append(parameter)

		texfile.write("\\end{tabular} \n")
		texfile.write("\\end{table} \n")

		if len(important_parameters_over_default) > 0:
		  texfile.write("The parameters ")
		  for i in range(len(important_parameters_over_default)):
		    texfile.write(str(important_parameters_over_default[i]))
		    if i == len(important_parameters_over_default) - 2 and len(important_parameters_over_default) > 1:
		      texfile.write(" and ")
		    elif i != len(important_parameters_over_default) - 1:
		      texfile.write(", ")
		  texfile.write(" explain at least $1\%$ of the performance variance, for the configurations who are better than the default. \n")

		for j in range(len(param_imp_not)):
		        texfile.write("\\begin{figure}[thbH!] \n")
		        texfile.write("\\centering \n")
		        texfile.write("\\includegraphics[width=0.8\\columnwidth]" +
		                     "{Plots/%s_fanova_over_DEFAULT.png} \n" % (
		                      param_imp_def[j][1]))
		        texfile.write("\\caption{%s %s %s} \n" % 
		                     (json_data["captions"]["parameter_importance_plot_over_default"],
		                      param_imp_def[j][1], 
		                      json_data["captions"]["parameter_importance_plot_over_default_2"]))
		        texfile.write("\\end{figure} \n")
		        texfile.write("\\FloatBarrier \n")

		texfile.write("\\FloatBarrier \n")

	texfile.write("\\bibliography{SpySMACReport} \n")

        # Style decision for the bibtex
        if tex_style == "ijcai13":
                texfile.write("\\bibliographystyle{TeXTemplates/ijcai13/named} \n")
	elif tex_style == "aaai":
		texfile.write("\\bibliographystyle{TeXTemplates/aaai/aaai} \n")
	else:
		texfile.write("\\bibliographystyle{ieeetr} \n")

        texfile.write("\\end{document}")
        texfile.close()

        os.system("cp -r latex_tools/TeXTemplates %s" % (out_dir))


	os.system("cp -r latex_tools/SpySMACReport.bib %s" % (out_dir))
        os.chdir("%s" % (out_dir))

        os.system("pdflatex SpySMACReport.tex")
	os.system("bibtex SpySMACReport")
	os.system("pdflatex SpySMACReport.tex")
	os.system("pdflatex SpySMACReport.tex")


def tex_template_processing(texfile, tex_style, json_data, solver_name):
	"""
	Args:
		texfile (file):	The texfile to create the paper.

		tex_style (str):	Name of the template to use. Possible templates are ijcai13,
					aaai or llncs. Else the article class will be used.

		json_data (dict):	Text phrases for the paper callable via the corresponding keys.

		solver_name (str):	The name of the used solver.

	Returns:
		Nothing


	"""

        # Tex file pre processing
        if tex_style == "llncs":
                texfile.write("\\documentclass{TeXTemplates/llncs2e/llncs} \n")
        elif tex_style == "aaai":
                
		texfile.write("\\documentclass[letterpaper]{article} \n")
        else:
                texfile.write("\\documentclass{article}\n")

        texfile.write("\\usepackage{booktabs}\n")
        texfile.write("\\usepackage{graphicx} \n")
        texfile.write("\\usepackage{placeins} \n")

        # Style decision for the article
        if tex_style == "ijcai13":
                texfile.write("\\usepackage{TeXTemplates/ijcai13/ijcai13} \n")
                texfile.write("\\usepackage{times} \n")
        elif tex_style == "aaai":
                texfile.write("\\usepackage{TeXTemplates/aaai/aaai} \n")
                texfile.write("\\usepackage{times} \n")
                texfile.write("\\usepackage{helvet} \n")
                texfile.write("\\usepackage{courier} \n")
                texfile.write("\\frenchspacing \n")
                texfile.write("\\setlength{\\pdfpagewidth}{8.5in} \n")
                texfile.write("\\setlength{\\pdfpageheigthbH!}{11in} \n")
                texfile.write("\\pdfinfo{ \n")
                texfile.write("/Title (%s) \n" % (json_data["title"].replace("$<$SOLVER$>$", solver_name)))
                texfile.write("/Author (Put All Your Authors Here, \
                              Seperated by Commas)} \n")
                texfile.write("\\setcounter{secnumdepth}{0} \n")
