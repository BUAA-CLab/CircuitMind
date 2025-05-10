# Code Overview

This document provides an overview of four Python scripts designed for calculating and analyzing SEI (Score of Evaluation Index) metrics for problem-solving data, including individual problems, grouped difficulty levels, leaderboard rankings, and comparative analysis.

## SEI_calculate_only.py
**Purpose**: Calculates the SEI for a single problem.  
**Input**:  
- `SEI_calculate_only_input.csv`: Input file containing data for a single problem.  
**Output**:  
- `{input_base_name}_reciprocals_only_{current_datetime}.csv`: Output file containing the calculated SEI for the problem, timestamped with the current date and time.

## SEI_calculate_CM.py
**Purpose**: Computes SEI for experimental data, calculating metrics for Easy, Medium, Hard difficulty groups, as well as an overall SEI.  
**Input**:  
- `input.csv`: Input file containing SEI data for individual problems (can directly use the output from `SEI_calculate_only.py`).  
**Output**:  
- `output.csv`: Output file containing SEI results for Easy, Medium, Hard groups, and the overall SEI.

## SEI_calculate_person_CM.py
**Purpose**: Calculates SEI for the top 1–1000 ranked individuals on a leaderboard.  
**Input**:  
- Leaderboard data (source not specified).  
**Output**:  
- `leaderboard_data/`: Directory containing individual CSV files, each storing data for a single problem extracted from the leaderboard.  
- `output.csv`: Output file containing SEI results for Easy, Medium, Hard groups, and the overall SEI.

## single_problem_leaderboard.py
**Purpose**: Compares the SEI of experimentally obtained problems with the corresponding SEI from leaderboard data to determine the ranking of experimental results.  
**Input**:  
- `summary_input.csv`: Experimental SEI data for individual problems.  
- `combined_input.csv`: Leaderboard data containing rankings for individual problems.  
**Output**:  
- `output.csv`: Output file detailing the distribution of problems across different performance intervals for each model.