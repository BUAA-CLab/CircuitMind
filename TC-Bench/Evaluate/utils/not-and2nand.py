import argparse

def read_netlist(file_path):
    """从文件中读取网表"""
    with open(file_path, "r") as file:
        lines = file.readlines()
    # 过滤空行和注释行（以 '*' 开头的行）
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("*")]

def write_netlist(file_path, netlist):
    """将优化后的网表写入文件"""
    with open(file_path, "w") as file:
        file.write("\n".join(netlist) + "\n")

def parse_component(line):
    """解析网表的一行并返回元件信息"""
    parts = line.split()
    if len(parts) < 3:
        raise ValueError(f"Invalid netlist line: {line}")
    return {
        "name": parts[0],    # 元件名
        "inputs": parts[1:-2],  # 输入节点列表
        "output": parts[-2], # 输出节点
        "type": parts[-1],   # 元件类型
    }

def find_mergeable_and_not_combinations(components):
    """寻找可合并的AND+NOT组合"""
    mergeable_combinations = []
    for comp in components:
        if comp["type"] == "__AND_":
            # 查找是否存在以AND的输出为输入的NOT
            for other in components:
                if (other["type"] == "__NOT_" and 
                    other["inputs"] == [comp["output"]] and  
                    ("nand" in other["output"] or "y" in other["output"])):
                    mergeable_combinations.append((comp, other))
    return mergeable_combinations

def optimize_components(components):
    """优化元件列表，合并AND+NOT为NAND"""
    mergeable_combinations = find_mergeable_and_not_combinations(components)

    # 合并 AND+NOT 为 NAND
    for and_gate, not_gate in mergeable_combinations:
        and_gate["type"] = "__NAND_"
        and_gate["output"] = not_gate["output"]
        components.remove(not_gate)

    return components

def optimize_netlist(netlist):
    """优化网表"""
    optimized_netlist = []
    components = []
    in_subckt = False  # 是否在子电路中
    current_subckt = []  # 当前子电路的内容

    for line in netlist:
        if line.startswith(".SUBCKT"):
            # 开始子电路
            in_subckt = True
            if components:
                # 先优化主电路部分
                components = optimize_components(components)
                optimized_netlist.extend([f"{comp['name']} {' '.join(comp['inputs'])} {comp['output']} {comp['type']}" for comp in components])
                components = []
            current_subckt = [line]
        elif line.startswith(".ENDS"):
            # 结束子电路
            in_subckt = False
            current_subckt.append(line)
            # 优化子电路
            subckt_components = parse_subckt_components(current_subckt[1:-1])
            subckt_components = optimize_components(subckt_components)
            optimized_netlist.append(current_subckt[0])
            optimized_netlist.extend([f"{comp['name']} {' '.join(comp['inputs'])} {comp['output']} {comp['type']}" for comp in subckt_components])
            optimized_netlist.append(current_subckt[-1])
        elif in_subckt:
            current_subckt.append(line)
        else:
            # 主电路部分
            try:
                components.append(parse_component(line))
            except ValueError as e:
                print(f"Skipping invalid line: {e}")

    if components:
        # 优化剩余主电路部分
        components = optimize_components(components)
        optimized_netlist.extend([f"{comp['name']} {' '.join(comp['inputs'])} {comp['output']} {comp['type']}" for comp in components])

    return optimized_netlist

def parse_subckt_components(subckt_lines):
    """解析子电路的组件"""
    components = []
    for line in subckt_lines:
        try:
            components.append(parse_component(line))
        except ValueError as e:
            print(f"Skipping invalid line in subckt: {e}")
    return components


def main():
    parser = argparse.ArgumentParser(description="Process SPICE netlist and device types files.")
    parser.add_argument(
        "--sp_file", 
        required=True, 
        help="Path to the SPICE netlist file (e.g., counter-small-3-no-delete.sp)."
    )
    
    args = parser.parse_args()
    # 从文件中读取网表
    original_netlist = read_netlist(args.sp_file)

    # 优化网表
    optimized_netlist = optimize_netlist(original_netlist)

    # 将优化后的网表写回文件
    write_netlist(args.sp_file, optimized_netlist)
    print(f"Netlist optimized and written back to {args.sp_file}")

if __name__ == "__main__":
    main()