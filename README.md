# Synthesizing Linked Data Under Cardinality and Integrity Constraints 

[Link to the paper](https://dl.acm.org/doi/pdf/10.1145/3448016.3457242)

## Framework

### Data

We perform experiments on a [dataset](https://www.openicpsr.org/openicpsr/project/100274/version/V1/view) that is derived from the 2010 U.S. Decennial Census.

### File structure
- coloring.py - Code for Phase II. Execution of our system begins here. It starts by calling the main function in cc_sol_ver2.py and builds on the returned intermediate solution (from Phase I).
  - DCs - See S_DC list variable.
- cc_sol_ver2.py - Code to complete the join view in Phase I. It calls the main function in lp.py on the set of CCs that are intersecting.
- lp.py - Code to handle intersecting CCs, which require an ILP solver, in Phase I.
- CCs - see input directory.
- Include person and household relations as .csv files in the input directory.
- Create directories "output" and "viewComp" for the log files, which are parsed and used in the experimental analysis.

The given files correspond to data scale 1x.

### Environment
We implemented our solution and baseline in Python 3.6.9 and Pandas DataFrame interface on Tensor TXR231-1000R D126 Intel(R) Xeon(R) CPU E5-2640 v4 2.40GHz CPU with 512 GB (40 cores) of RAM. We use the standard PuLP and NumPy Libraries for the ILP, and NetworkX to construct and color conflict graphs.
