# Sweep-Loop-Mutate, a Novel Algorithm for the Multiple Traveling Salesmen Problem

The Multiple Traveling Salesmen Problem (MTSP) is a variation of the Traveling Salesman Problem used in many real-world applications involving travel distance optimization. Many existing solutions further divide this problem into two parts: clustering and routing. My novel approach here is a radial clustering and routing algorithm that takes advantage of geometric properties of datasets to efficiently select subsets of points, create partial routes, and optimize them to form a complete solution. More details about the algorithm and initial results are explained in my write-up, as well as some ideas for future works.

This code and write-up were part of my final project submission for CSC 705 "Design and Analysis of Computer Algorithms", Dakota State University, Fall 2024. The class was taught by Prof. Youssef Harrath. Two additional algorithms adapted for the project for comparison are included as well; sourced from Sedighpour, Yousefikhoshbakht, and Darani's genetic algorithm (https://github.com/N0vel/Multiple-travelling-salesman-mTSP-GA-approach) and Pan and Wang's ant colony optimization algorithm (https://github.com/ganyariya/MTSP_ACO).

## Contents

- Project write-up
- Python code, including algorithms, testing framework, and a dataset list
- Jupyter notebook used for creating graphics for a presentation
- a subset of datasets from http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/

## How to Use

Install the tsplib95 Python library. Execute tester.py with a dataset file (or a text file listing datasets), one or more algorithms to run, and one or more numbers of salesmen to simulate. There are also options for plotting routes and generating CSV files. See commandline examples below:

```
python .\tester.py -f ..\datasets\eil76.tsp -a slm -n 6 -p

python .\tester.py -l dataset_list.txt -o output_final.csv -a aco,ga,slm -n 3,5,10
```