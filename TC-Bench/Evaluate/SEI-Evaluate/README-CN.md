# 代码概述

本文档提供了四个Python脚本的概述，这些脚本用于计算和分析问题解决数据的SEI（评估指数得分）指标，包括单个问题、分组难度级别、排行榜排名以及比较分析。

## SEI_calculate_only.py
**功能**：计算单个问题的SEI。  
**输入**：  
- `SEI_calculate_only_input.csv`：包含单个问题数据的输入文件。  
**输出**：  
- `{input_base_name}_reciprocals_only_{current_datetime}.csv`：包含计算得到的单个问题SEI的输出文件，文件名包含当前日期和时间戳。

## SEI_calculate_CM.py
**功能**：对实验数据进行SEI计算，分别计算简单（Easy）、中等（Medium）、困难（Hard）三个难度分组以及总体SEI。  
**输入**：  
- `input.csv`：包含单个问题SEI数据的输入文件（可直接使用`SEI_calculate_only.py`的输出文件）。  
**输出**：  
- `output.csv`：包含简单、中等、困难三个分组以及总体SEI的输出文件。

## SEI_calculate_person_CM.py
**功能**：对排行榜上排名1–1000位的数据进行SEI计算。  
**输入**：  
- 排行榜数据（未指定具体来源）。  
**输出**：  
- `leaderboard_data/`：存储从排行榜提取的每个问题数据的文件夹，每个问题单独保存为CSV文件。  
- `output.csv`：包含简单、中等、困难三个分组以及总体SEI的输出文件。

## single_problem_leaderboard.py
**功能**：将实验得到的每个问题的SEI与排行榜上对应问题的SEI进行比较，判断实验结果的排名。  
**输入**：  
- `summary_input.csv`：实验得到的单个问题的SEI数据。  
- `combined_input.csv`：排行榜上单个问题的排名数据。  
**输出**：  
- `output.csv`：包含每个模型在不同性能区间上的问题分布的输出文件。