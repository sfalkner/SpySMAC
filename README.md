#SpySMAC 
SpySMAC is an algorithm configuration tool based on SMAC for SAT solvers

#LICENSE
  It is distributed under the GNU Public License. See COPYING for
  details regarding the license. Please note that SMAC (shipped with SpySMAC
  
  
#OVERVIEW
  SpySMAC is an algorithm configuration and analyzing tool. 
  It is written in Python and uses SMAC (Java).

#REQUIREMENTS

  * Python 2.7 (or 3.4 soon)
  * [numpy](http://www.numpy.org/)
  * [matplotlib](http://matplotlib.org/)
    
  
#PACKAGE CONTENTS
  COPYING      - GNU Public License
  CHANGELOG    - Major changes between versions
  README.md    - This file
  SpySMAC_run.py - script to run configuration 
  SpySMAC_analyze.py - script to analyze confiuration runs
  
#USAGE
  See:
  
```bash
$ python SpySMAC/SpySMAC_run.py -h
```
  
#Mini Example with MiniSAT
  
  Here is a small example for the well known SAT solver MiniSAT.
  First, let us have look at the input:
  
```bash
$ cd examples/ && ls -l .
minisat/
swv-inst/
```  
  
  In "swv-inst", you will find the some compressed software verification instances.
  Please extract them with:
  
```bash
$ cd swv-inst
$ tar xvfz SWV-GZIP.tar.gz
```
  
  Now, we have to compile minisat:
  
```bash
$ cd ../minisat/
$ export MROOT=`pwd`
$ cd core && make
```
  
  Last but not least, we can start SpySMAC on minisat and the SWV instances:
  
```bash
python ../SpySMAC_run.py -i ./swv-inst/SWV-GZIP/ -b minisat/core/minisat -p minisat/pcs.txt --prefix "-" -o ./spysmac_logs/ -B 60 -c 2
```
  
```
'-i ./swv-inst/SWV-GZIP/'	: SWV instances 
'-b minisat/core/minisat'	: MiniSAT binary
'-p minisat/pcs.txt'		: PCS file of MiniSAT
'--prefix "-"'				: Prefix of parameters 
'-o ./spysmac_logs/'		: Output directory of log files
'-B 60'						: configuration budget in sec 
'-c 2' 						: runtime cutoff of an individual algorithm run
```
    
  After approx. 1 minute, you will find all generated data during configuration in "./spysmac_logs/".
  To compare against the default configuration of MiniSAT, we have also to evaluate the default configuration, which is done by running SpySMAC with seed 0:

```bash
python ../SpySMAC_run.py -i ./swv-inst/SWV-GZIP/ -b minisat/core/minisat -p minisat/pcs.txt --prefix "-" -o ./spysmac_logs/ -c 2 --seed 0
```
  
  
  If you run now the analyzing script, a report of the configuration run will generated:
  
```bash
python ../SpySMAC_analyze.py -i spysmac_logs/ -o spysmac_report/
```
  
  You can see the report by opening "spysmac_report/index.html" with a web browser of your choice.
  
  Please note that the configuration run was very short and SMAC could not collect a lot of data.
  Therefore, we don't expect a large improvement on this mini example 
  and also the parameter importance results may be very vague.
 
#RECOMMENDATIONS

  We recommend the following things to improve the results of SpySMAC:
  
  * use at least 200 SAT formulas as instances (the more the better)
  * use a homogeneous instance set (i.e., all instances from one application); 
    on heterogeneous instance sets, configuration gets a lot harder
  * the default configuration of your solver should solve at least 50% with the given runtime cutoff
  * as configuration budget, you should be at least 200 times the runtime cutoff (more is better)
  * since SMAC is a stochastic process and the configuration space has many local minima, 
    several indepent runs of SMAC will improve also the result (use option -r);
    we recommend at leat 10 SMAC runs
     

#Examples

###minisat-HACK-999ED-CSSC
  * [CSSC-K3-300s-2day](http://aclib.net/spysmac/random_CSSC-K3-300s-2day_smac_minisat-HACK-999ED-CSSC)
  * [CSSC-CircuitFuzz-300s-2day](http://aclib.net/spysmac/industrial_CSSC-CircuitFuzz-300s-2day_smac_minisat-HACK-999ED-CSSC)
  * [CSSC-3cnf-v350-300s-2day](http://aclib.net/spysmac/random_CSSC-3cnf-v350-300s-2day_smac_minisat-HACK-999ED-CSSC)
  * [CSSC-Queens-300s-2day](http://aclib.net/spysmac/crafted_CSSC-Queens-300s-2day_smac_minisat-HACK-999ED-CSSC)
  * [CSSC-unsat-unif-k5-300s-2day](http://aclib.net/spysmac/random_CSSC-unsat-unif-k5-300s-2day_smac_minisat-HACK-999ED-CSSC)
  * [CSSC-GI-300s-2day](http://aclib.net/spysmac/crafted_CSSC-GI-300s-2day_smac_minisat-HACK-999ED-CSSC)
  * [CSSC-LABS-300s-2day](http://aclib.net/spysmac/crafted_CSSC-LABS-300s-2day_smac_minisat-HACK-999ED-CSSC)
  * [CSSC-IBM-300s-2day](http://aclib.net/spysmac/industrial_CSSC-IBM-300s-2day_smac_minisat-HACK-999ED-CSSC)
  * [CSSC-BMC08-300s-2day](http://aclib.net/spysmac/industrial_CSSC-BMC08-300s-2day_smac_minisat-HACK-999ED-CSSC)
  
###probSAT
  * [CSSC-3SAT1k-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-3SAT1k-sat-300s-2day_smac_probSAT)
  * [CSSC-5SAT500-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-5SAT500-sat-300s-2day_smac_probSAT)
  * [CSSC-7SAT90-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-7SAT90-sat-300s-2day_smac_probSAT)
  
###Riss-4.27
  * [CSSC-GI-300s-2day](http://aclib.net/spysmac/crafted_CSSC-GI-300s-2day_smac_Riss-4.27)
  * [CSSC-BMC08-300s-2day](http://aclib.net/spysmac/industrial_CSSC-BMC08-300s-2day_smac_Riss-4.27)
  * [CSSC-K3-300s-2day](http://aclib.net/spysmac/random_CSSC-K3-300s-2day_smac_Riss-4.27)
  * [CSSC-Queens-300s-2day](http://aclib.net/spysmac/crafted_CSSC-Queens-300s-2day_smac_Riss-4.27)
  * [CSSC-CircuitFuzz-300s-2day](http://aclib.net/spysmac/industrial_CSSC-CircuitFuzz-300s-2day_smac_Riss-4.27)
  * [CSSC-3cnf-v350-300s-2day](http://aclib.net/spysmac/random_CSSC-3cnf-v350-300s-2day_smac_Riss-4.27)
  * [CSSC-LABS-300s-2day](http://aclib.net/spysmac/crafted_CSSC-LABS-300s-2day_smac_Riss-4.27)
  
###YalSAT
  * [CSSC-3SAT1k-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-3SAT1k-sat-300s-2day_smac_YalSAT)
  * [CSSC-LABS-300s-2day](http://aclib.net/spysmac/crafted_CSSC-LABS-300s-2day_smac_YalSAT)
  * [CSSC-5SAT500-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-5SAT500-sat-300s-2day_smac_YalSAT)
  * [CSSC-GI-300s-2day](http://aclib.net/spysmac/crafted_CSSC-GI-300s-2day_smac_YalSAT)
  * [CSSC-7SAT90-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-7SAT90-sat-300s-2day_smac_YalSAT)
  
###clasp-3.0.4-p8
  * [CSSC-Queens-300s-2day](http://aclib.net/spysmac/crafted_CSSC-Queens-300s-2day_smac_clasp-3.0.4-p8)
  * [CSSC-GI-300s-2day](http://aclib.net/spysmac/crafted_CSSC-GI-300s-2day_smac_clasp-3.0.4-p8)
  * [CSSC-BMC08-300s-2day](http://aclib.net/spysmac/industrial_CSSC-BMC08-300s-2day_smac_clasp-3.0.4-p8)
  * [CSSC-3cnf-v350-300s-2day](http://aclib.net/spysmac/random_CSSC-3cnf-v350-300s-2day_smac_clasp-3.0.4-p8)
  * [CSSC-CircuitFuzz-300s-2day](http://aclib.net/spysmac/industrial_CSSC-CircuitFuzz-300s-2day_smac_clasp-3.0.4-p8)
  * [CSSC-K3-300s-2day](http://aclib.net/spysmac/random_CSSC-K3-300s-2day_smac_clasp-3.0.4-p8)
  
###cryptominisat
  * [CSSC-GI-300s-2day](http://aclib.net/spysmac/crafted_CSSC-GI-300s-2day_smac_cryptominisat)
  * [CSSC-CircuitFuzz-300s-2day](http://aclib.net/spysmac/industrial_CSSC-CircuitFuzz-300s-2day_smac_cryptominisat)
  * [CSSC-LABS-300s-2day](http://aclib.net/spysmac/crafted_CSSC-LABS-300s-2day_smac_cryptominisat)
  * [CSSC-IBM-300s-2day](http://aclib.net/spysmac/industrial_CSSC-IBM-300s-2day_smac_cryptominisat)
  * [CSSC-Queens-300s-2day](http://aclib.net/spysmac/crafted_CSSC-Queens-300s-2day_smac_cryptominisat)
  * [CSSC-BMC08-300s-2day](http://aclib.net/spysmac/industrial_CSSC-BMC08-300s-2day_smac_cryptominisat)
  
###CSCCSat2014
  * [CSSC-5SAT500-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-5SAT500-sat-300s-2day_smac_CSCCSat2014)
  * [CSSC-7SAT90-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-7SAT90-sat-300s-2day_smac_CSCCSat2014)
  * [CSSC-3SAT1k-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-3SAT1k-sat-300s-2day_smac_CSCCSat2014)
  
###DCCASat+march-rw
  * [CSSC-K3-300s-2day](http://aclib.net/spysmac/random_CSSC-K3-300s-2day_smac_DCCASat+march-rw)
  * [CSSC-3cnf-v350-300s-2day](http://aclib.net/spysmac/random_CSSC-3cnf-v350-300s-2day_smac_DCCASat+march-rw)
  * [CSSC-unsat-unif-k5-300s-2day](http://aclib.net/spysmac/random_CSSC-unsat-unif-k5-300s-2day_smac_DCCASat+march-rw)
  
###lingeling
  * [CSSC-Queens-300s-2day](http://aclib.net/spysmac/crafted_CSSC-Queens-300s-2day_smac_lingeling)
  * [CSSC-GI-300s-2day](http://aclib.net/spysmac/crafted_CSSC-GI-300s-2day_smac_lingeling)
  * [CSSC-LABS-300s-2day](http://aclib.net/spysmac/crafted_CSSC-LABS-300s-2day_smac_lingeling)
  * [CSSC-CircuitFuzz-300s-2day](http://aclib.net/spysmac/industrial_CSSC-CircuitFuzz-300s-2day_smac_lingeling)
  
###SparrowToRiss
  * [CSSC-3cnf-v350-300s-2day](http://aclib.net/spysmac/random_CSSC-3cnf-v350-300s-2day_smac_SparrowToRiss)
  * [CSSC-IBM-300s-2day](http://aclib.net/spysmac/industrial_CSSC-IBM-300s-2day_smac_SparrowToRiss)
  * [CSSC-GI-300s-2day](http://aclib.net/spysmac/crafted_CSSC-GI-300s-2day_smac_SparrowToRiss)
  * [CSSC-3SAT1k-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-3SAT1k-sat-300s-2day_smac_SparrowToRiss)
  * [CSSC-CircuitFuzz-300s-2day](http://aclib.net/spysmac/industrial_CSSC-CircuitFuzz-300s-2day_smac_SparrowToRiss)
  * [CSSC-Queens-300s-2day](http://aclib.net/spysmac/crafted_CSSC-Queens-300s-2day_smac_SparrowToRiss)
  * [CSSC-LABS-300s-2day](http://aclib.net/spysmac/crafted_CSSC-LABS-300s-2day_smac_SparrowToRiss)
  * [CSSC-K3-300s-2day](http://aclib.net/spysmac/random_CSSC-K3-300s-2day_smac_SparrowToRiss)
  * [CSSC-BMC08-300s-2day](http://aclib.net/spysmac/industrial_CSSC-BMC08-300s-2day_smac_SparrowToRiss)
  * [CSSC-5SAT500-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-5SAT500-sat-300s-2day_smac_SparrowToRiss)
  * [CSSC-7SAT90-sat-300s-2day](http://aclib.net/spysmac/randomSAT_CSSC-7SAT90-sat-300s-2day_smac_SparrowToRiss)


 
#CONTACT

	Stefan Falkner
 	Marius Lindauer
 	Frank Hutter
 	University of Freiburg
 	{sfalkner,lindauer,fh}@cs.uni-freiburg.de
 	
  
