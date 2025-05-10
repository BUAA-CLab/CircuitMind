import os
import re
import argparse # Import argparse
from prettytable import PrettyTable

def get_all_v_files(root_dir):
    """遍历目录，获取所有.v文件的路径"""
    v_files = []
    # Check if root_dir exists and is a directory
    if not os.path.isdir(root_dir):
        print(f"Warning: Directory not found or is not a directory: {root_dir}")
        return v_files
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.v'):
                v_files.append(os.path.join(subdir, file))
    return v_files

def read_file_content(file_path):
    """读取文件内容，使用宽松的编码处理方式"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f: # Use errors='ignore' for more robustness
            return f.read().strip()
    except Exception as e:
        print(f"Warning: Could not read file {file_path}: {e}")
        return None # Return None on error

def compare_files(file_paths):
    """比较文件内容，并返回不同内容的数量"""
    contents = {}
    valid_files_read = 0
    for file_path in file_paths:
        content = read_file_content(file_path)
        # Only process if content was read successfully and is not empty
        if content: # Check if content is not None and not empty string
            valid_files_read += 1
            if content not in contents:
                contents[content] = []
            contents[content].append(file_path)

    # Optional: Add a check for minimum valid files if needed
    # if valid_files_read < 2: # Example threshold
    #     print(f"Warning: Less than 2 valid Verilog files found in the set starting with {file_paths[0] if file_paths else 'N/A'}")

    # The subtraction of 2 seems arbitrary without context.
    # Consider removing it or documenting *why* 2 is subtracted.
    # If it's to exclude reference/template files, maybe filter by filename pattern instead?
    # Returning raw diversity count for now. Adjust if the -2 logic is confirmed necessary.
    diversity_count = len(contents)
    # print(f"Debug: Found {diversity_count} unique contents from {valid_files_read} valid files.") # Debug print
    # return max(0, diversity_count - 2) # Original logic (use if needed)
    return diversity_count # Returning raw count


def extract_number_from_folder_name(folder_name):
    """从文件夹名称中提取数字"""
    match = re.match(r"(\d+)", folder_name)
    if match:
        return int(match.group(1))
    # Return a large number for non-numeric prefixes to sort them last/consistently
    return float('inf')

def analyze_subfolders(base_dir):
    """分析base_dir下的每个子文件夹，输出不同内容数量"""
    table = PrettyTable()
    table.field_names = ["子文件夹 (Challenge)", "不同 Verilog 文件内容数量"]
    table.align["子文件夹 (Challenge)"] = "l"
    table.align["不同 Verilog 文件内容数量"] = "r"


    folder_data = []

    if not os.path.isdir(base_dir):
         print(f"Error: Input directory '{base_dir}' not found or is not a directory.")
         return None # Return None to indicate error

    # 遍历base_dir下的每个子文件夹 (challenges)
    for subfolder_name in sorted(os.listdir(base_dir)): # Sort challenge names for consistent order
        subfolder_path = os.path.join(base_dir, subfolder_name)

        # 只处理文件夹
        if os.path.isdir(subfolder_path):
            # 获取该子文件夹下所有（递归）的 .v 文件
            # This will find .v files in attempt folders like 'base_dir/challenge/attempt/*.v'
            v_files = get_all_v_files(subfolder_path)

            # 如果该子文件夹没有 .v 文件，则跳过
            if not v_files:
                # print(f"Info: No .v files found in challenge folder: {subfolder_name}")
                # Optionally add row with 0 count:
                # folder_data.append([subfolder_name, 0])
                continue

            # 计算该子文件夹内的不同内容数量
            num_different_contents = compare_files(v_files)

            # 将结果添加到数据列表中
            folder_data.append([subfolder_name, num_different_contents])

    # 按照文件夹名称中的数字部分从小到大排序
    folder_data.sort(key=lambda x: extract_number_from_folder_name(x[0]))

    # 将排序后的数据添加到表格中
    for row in folder_data:
        table.add_row(row)

    return table

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Verilog Diversity Test: Counts unique .v file contents per challenge subfolder.")
    parser.add_argument("--input-dir", required=True,
                        help="Path to the base directory containing challenge subfolders (e.g., model results directory).")
    args = parser.parse_args()

    # 分析子文件夹，并打印输出
    print(f"Analyzing Verilog diversity in subfolders of: {args.input_dir}")
    table = analyze_subfolders(args.input_dir)

    # 打印表格 if analysis was successful
    if table:
        print("\nDiversity Results:")
        print(table)
    else:
        print("Analysis could not be completed due to errors.")