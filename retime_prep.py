import re
import os

def extract_path_nodes(report_path: str, top_n: int = 5) -> list:
    """
    只提取 STA 报告中 top N 条路径的、类型为(.names)的节点（去重），
    只保留最前面的部分（如[1327]或new_n_n3976_）

    Args:
        report_path: STA 报告文件路径（如 .rpt 文件）
        top_n: 提取前 N 条路径

    Returns:
        node_names (list): 从所有路径中提取的去重(.names)节点列表，只保留最前面的部分
    """
    with open(report_path, 'r') as f:
        content = f.read()

    path_blocks = re.split(r'(?=^#Path \d+)', content, flags=re.MULTILINE)
    node_names = []
    count = 0

    for block in path_blocks:
        if not block.strip().startswith("#Path"):
            continue
        if count >= top_n:
            break

        # 提取节点表格块
        table_match = re.search(r'Point\s+Incr\s+Path\n[-]+\n(.*?)(?:data arrival time|$)', block, re.DOTALL)
        node_lines = table_match.group(1).strip().split('\n') if table_match else []

        for line in node_lines:
            # 只匹配(.names)节点
            m = re.match(r'([^\s\|]+)\s+.*\(\.names\)', line.strip())
            if m:
                name = m.group(1)
                # 去掉.in[...]或.out[...]等后缀
                base = re.split(r'\.in\[|\.out\[', name)[0]
                if base not in node_names:
                    node_names.append(base)
        count += 1

    return node_names


def write_nodes_to_file(node_names: list, output_file: str):
    """
    将节点名称写入文本文件，每行一个

    Args:
        node_names: 节点列表
        output_file: 文件路径
    """
    with open(output_file, 'w') as f:
        for node in node_names:
            f.write(f"{node}\n")


def extract_first_latch_params(blif_path: str):
    """
    提取 blif 文件中第一条 .latch 行的后三个参数（始终心系）

    Args:
        blif_path: blif 文件路径

    Returns:
        latch_params (tuple): 第一条 .latch 行后三个参数组成的元组，若无则返回 None
    """
    with open(blif_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('.latch'):
                parts = line.split()
                if len(parts) >= 6:
                    # 只提取第一条
                    return tuple(parts[-3:])
    return None


def optimize_latch_lines_inplace(blif_path: str, latch_params: tuple):
    """
    用给定 latch_params 替换 blif 文件中所有 .latch 行的后三个参数，原地覆盖写回

    Args:
        blif_path: 需要修改的 blif 文件路径
        latch_params: 用于替换的后三个参数（如 ('re', 'pclk', '2')）
    """
    with open(blif_path, 'r') as fin:
        lines = fin.readlines()

    new_lines = []
    for line in lines:
        if line.strip().startswith('.latch'):
            parts = line.strip().split()
            if len(parts) >= 3:
                # 保留前两个参数，后三个用 latch_params 替换
                new_line = f".latch\t {parts[1]}\t {parts[2]} \t {' '.join(latch_params)}\n"
                new_lines.append(new_line)
                continue
        new_lines.append(line)

    with open(blif_path, 'w') as fout:
        fout.writelines(new_lines)

def extract_delay_fmax_from_log(log_path):
    """
    从vpr_stdout.log中提取Final critical path delay和Fmax
    """
    pattern = re.compile(r"Final critical path delay \(least slack\): ([\d\.]+) ns, Fmax: ([\d\.]+) MHz")
    with open(log_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                delay = float(match.group(1))
                fmax = float(match.group(2))
                return delay, fmax
    return None, None

def stat_all_iters(bench_dir):
    """
    统计bench_dir下所有iter*目录中的vpr_stdout.log的delay和Fmax
    """
    results = []
    for subdir in sorted(os.listdir(bench_dir)):
        iter_path = os.path.join(bench_dir, subdir)
        if os.path.isdir(iter_path) and subdir.startswith("iter"):
            log_path = os.path.join(iter_path, "vpr_stdout.log")
            if os.path.exists(log_path):
                delay, fmax = extract_delay_fmax_from_log(log_path)
                results.append((subdir, delay, fmax))
            else:
                results.append((subdir, None, None))
    # 打印表格
    print(f"{'迭代轮次':<10} {'Delay(ns)':<12} {'Fmax(MHz)':<12}")
    for subdir, delay, fmax in results:
        delay_str = f"{delay:.5f}" if delay is not None else "N/A"
        fmax_str = f"{fmax:.3f}" if fmax is not None else "N/A"
        print(f"{subdir:<10} {delay_str:<12} {fmax_str:<12}")


if __name__ == "__main__":
    report = '/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/ret/diffeq_test/iter0/report_timing.setup.rpt'
    output = '/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/ret/diffeq/cpdInfo.txt'
    nodes = extract_path_nodes(report, top_n=5)
    write_nodes_to_file(nodes, output)
    print(f"Extracted {len(nodes)} nodes:")
    # print(" -> ".join(nodes))
    # blif_file = '/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/ret/diffeq/diffeq_1.blif'
    # params = extract_first_latch_params(blif_file)
    # blif_out_file = '/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/retdiffeq_retimed.blif'
    # if params:
    #     optimize_latch_lines_inplace(blif_out_file, params)
    #     print(f"已优化并覆盖写回原文件: {blif_out_file}")
    # else:
    #     print("未找到 .latch 行，未做修改。")
    # bench_dir = "/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/ret/diffeq_test"
    # stat_all_iters(bench_dir)