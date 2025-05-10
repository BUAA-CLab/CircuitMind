import re
import json
import argparse
from collections import defaultdict
from graphviz import Digraph

def preprocess_sp_file(file_path):
    """预处理 SPICE 文件，去除注释和多余字符"""
    with open(file_path, 'r') as file:
        lines = file.readlines()

    preprocessed_lines = []
    for line in lines:
        # 去掉注释（假设注释以 '*' 开始）和空行
        line = line.split('*')[0].strip()
        if line:
            preprocessed_lines.append(line)
    return '\n'.join(preprocessed_lines)

def parse_netlist(netlist, device_types):
    """解析网表字符串，提取实例和信号映射"""
    instances = []
    signals = defaultdict(list)
    external_ports = set()

    # 每行一个实例，格式: X0 clk state dout rst __SDFF_PP1_
    # 假设实例名称以 'X' 开头，后面跟随实例名、连接信号和设备类型
    instance_pattern = re.compile(r'^X(\S+)\s+(.+)\s+(\S+)$', re.IGNORECASE)

    for line in netlist.strip().split('\n'):
        line = line.strip()
        if not line or not line.startswith('X'):
            continue  # 跳过非实例行

        match = instance_pattern.match(line)
        if not match:
            print(f"Invalid line format: {line}")
            continue

        instance_name, connections_str, device_type = match.groups()
        connections = connections_str.split()

        device_info = device_types.get(device_type)
        if not device_info:
            print(f"Unknown device type: {device_type}")
            continue

        port_order = device_info.get('port_order', [])
        if len(connections) != len(port_order):
            print(f"Error in {instance_name}: Number of connections ({len(connections)}) does not match ports ({len(port_order)}).")
            continue

        port_mapping = dict(zip(port_order, connections))

        instance = {
            'name': instance_name,
            'device_type': device_type,
            'port_mapping': port_mapping,
            'inputs': device_info.get('inputs', []),
            'outputs': device_info.get('outputs', []),
            'delay': device_info.get('delay', 0),
            'gate_num': device_info.get('gate_num', 1)  # 默认为1
        }
        instances.append(instance)

        for port, net in port_mapping.items():
            direction = 'input' if port in instance['inputs'] else 'output'
            signals[net].append({'instance': instance_name, 'port': port, 'direction': direction})

    # 识别外部端口（仅作为输出的信号）
    for net, conns in signals.items():
        outputs = [conn for conn in conns if conn['direction'] == 'output']
        inputs = [conn for conn in conns if conn['direction'] == 'input']
        if outputs and not inputs:
            external_ports.add(net)
            print(f"External port identified: {net}")

    return instances, signals, external_ports

def detect_cycles(graph):
    """检测图中的所有组合环路"""
    visited = set()
    stack = set()  # 当前递归堆栈中的节点
    cycle_path = []  # 用于记录环路路径

    def dfs(node, path):
        if node in stack:  # 回边，存在环路
            cycle_start_index = path.index(node)
            cycle_path.extend(path[cycle_start_index:])
            return True
        if node in visited:
            return False
        visited.add(node)
        stack.add(node)
        path.append(node)
        for neighbor in graph[node]:
            if dfs(neighbor, path):
                return True
        stack.remove(node)
        path.pop()
        return False

    for node in list(graph.keys()):
        if dfs(node, []):
            return True, cycle_path
    return False, []

def build_graph(instances, signals, external_ports, node_delay):
    """构建DAG图，检测环路并递归移除以避免死循环，同时处理孤立的输出信号（寄存器）"""
    graph = defaultdict(list)
    nodes = set()

    # 添加所有实例为节点
    for instance in instances:
        nodes.add(instance['name'])

    # 处理信号连接，建立图的边
    for net, conns in signals.items():
        drivers = [conn for conn in conns if conn['direction'] == 'output']
        receivers = [conn for conn in conns if conn['direction'] == 'input']

        for driver in drivers:
            source = driver['instance'] if driver['instance'] != 'external' else net
            for receiver in receivers:
                target = receiver['instance']
                graph[source].append(target)

    # 处理孤立的输出信号，连接到OUT节点
    nodes.add("OUT")
    for net in external_ports:
        drivers = [conn for conn in signals.get(net, []) if conn['direction'] == 'output']
        for driver in drivers:
            source = driver['instance'] if driver['instance'] != 'external' else net
            graph[source].append("OUT")
            print(f"Connecting {source} to OUT for external port {net}")

    # 递归检测并移除环路
    while True:
        has_cycle, cycle_path = detect_cycles(graph)
        if not has_cycle:
            break  # 如果没有环路，退出循环

        print("Combinational loop detected! Removing loop edges.")
        print("Cycle path:", " -> ".join(cycle_path))
        # 移除环路中所有节点的输出边
        for node in cycle_path:
            graph[node] = []
        # 合并延时到代表节点
        representative = cycle_path[0]
        combined_delay = sum(node_delay.get(node, 0) for node in cycle_path)
        node_delay[representative] = combined_delay
        for node in cycle_path[1:]:
            node_delay[node] = 0  # 清零其他节点的延时

    return nodes, graph

def topological_sort(nodes, graph):
    """拓扑排序，确保无环图"""
    visited = set()
    stack = []

    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for neighbor in graph[node]:
            dfs(neighbor)
        stack.append(node)

    for node in nodes:
        if node not in visited:
            dfs(node)

    return stack[::-1]

def find_longest_path(nodes, graph, node_delay, end_node="OUT"):
    """找到最长延时路径，延时与节点关联，路径以end_node结尾"""
    topo_order = topological_sort(nodes, graph)
    max_delay = {node: node_delay.get(node, 0) for node in nodes}
    predecessor = {node: None for node in nodes}

    for node in topo_order:
        for neighbor in graph[node]:
            if max_delay[neighbor] < max_delay[node] + node_delay.get(neighbor, 0):
                max_delay[neighbor] = max_delay[node] + node_delay.get(neighbor, 0)
                predecessor[neighbor] = node

    # 确保end_node存在
    if end_node not in max_delay:
        print(f"End node '{end_node}' not found in the graph.")
        return max_delay, []

    longest_path = []
    current = end_node
    while current is not None:
        longest_path.append(current)
        current = predecessor[current]
    return max_delay, longest_path[::-1]

def count_logic_gates(instances):
    """计算网表中使用的基础逻辑门数量"""
    return sum(inst['gate_num'] for inst in instances)

def visualize_graph(nodes, graph, longest_path, external_ports, output_file):
    """可视化网表连接与最长延时路径"""
    dot = Digraph(comment="Netlist Visualization with Longest Delay Path")
    dot.attr(rankdir='LR')

    for node in nodes:
        if node == "OUT":
            shape, color = ('ellipse', 'green')
        elif node in external_ports:
            shape, color = ('ellipse', 'red')
        else:
            shape, color = ('box', 'black')
        dot.node(node, shape=shape, color=color)

    # 创建一个集合用于快速查找路径中的节点对
    path_edges = set()
    for i in range(len(longest_path) - 1):
        path_edges.add((longest_path[i], longest_path[i + 1]))

    for src, neighbors in graph.items():
        for dst in neighbors:
            if (src, dst) in path_edges:
                color = "blue"
                penwidth = '2'
            else:
                color = "black"
                penwidth = '1'
            dot.edge(src, dst, color=color, penwidth=penwidth)

    dot.render(output_file, view=False)

def main(sp_file, device_types_path):
    # 加载设备类型信息
    try:
        with open(device_types_path, "r") as json_file:
            DEVICE_TYPES = json.load(json_file)
    except FileNotFoundError:
        print(f"Device types file not found: {device_types_path}")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return

    # 预处理SPICE网表文件
    preprocessed_netlist = preprocess_sp_file(sp_file)

    # 解析网表
    instances, signals, external_ports = parse_netlist(preprocessed_netlist, DEVICE_TYPES)

    # 创建节点延时映射
    node_delay = {port: 0 for port in external_ports}  # 外部端口的延时为0
    for instance in instances:
        node_delay[instance['name']] = instance['delay']

    # 构建图并处理环路和寄存器输出
    nodes, graph = build_graph(instances, signals, external_ports, node_delay)

    # 统计逻辑门数量
    logic_gate_count = count_logic_gates(instances)

    # 查找最长路径和最大延时，路径以OUT结尾
    max_delay, longest_path = find_longest_path(nodes, graph, node_delay, end_node="OUT")

    if not longest_path:
        print("No valid path found to OUT.")
        return

    # 打印结果
    print(f"\nLongest delay: {max_delay.get('OUT', 0)} ns")
    print("Longest path:", " -> ".join(longest_path))
    print(f"Total logic gates: {logic_gate_count}")

    # 打印延时累计情况沿最长路径
    print("\n延时累计情况沿最长路径:")
    for node in longest_path:
        incremental_delay = node_delay.get(node, 0)
        cumulative_delay = max_delay.get(node, 0)
        print(f"{node}: {cumulative_delay} ns (增加 {incremental_delay} ns)")
    print(f"Total delay: {cumulative_delay}")
    # 可视化
    output = sp_file.split("/")[-1].split(".sp")[0]
    visualize_graph(nodes, graph, longest_path, external_ports, output + '-delay')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process SPICE netlist and device types files.")
    parser.add_argument(
        "--sp_file", 
        required=True, 
        help="Path to the SPICE netlist file (e.g., counter-small-3-no-delete.sp)."
    )
    parser.add_argument(
        "--device_type_file", 
        required=True, 
        help="The corresponding device type JSON file."
    )
    args = parser.parse_args()

    # 调用主函数并传递参数
    main(args.sp_file, args.device_type_file)