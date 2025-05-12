import os
from vpr_runner import run_vpr
from staInfo import extract_path_nodes, write_nodes_to_file
import shutil

# 顶层工作目录
work_dir = "/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/ret/"
# benchmark 名称
benchmark = "diffeq_test"
# 子目录路径
bench_dir = os.path.join(work_dir, benchmark)

# 如果子目录不存在则创建
os.makedirs(bench_dir, exist_ok=True)

# 可选：将 blif 文件复制到子目录（如果还没复制）
blif_src = "/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/vtr_flow/benchmarks/blif/diffeq.blif"
blif_dst = os.path.join(bench_dir, f"{benchmark}.blif")
if not os.path.exists(blif_dst):
    shutil.copy(blif_src, blif_dst)

# 保存当前目录
orig_dir = os.getcwd()

try:
    # 进入 benchmark 子目录
    os.chdir(bench_dir)

    # 路径用当前目录下的相对路径
    blif_path = blif_src
    arch_path = "/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/vtr_flow/arch/timing/k6_frac_N10_frac_chain_mem32K_40nm.xml"

    status = run_vpr(blif_path, arch_path)
    if status == 0:
        print("✔️ VPR ran successfully")
        # 等待生成report_timing.setup.rpt文件
        setup_rpt = "report_timing.setup.rpt"
        max_wait = 600  # 最大等待600秒
        wait_time = 0
        while not os.path.exists(setup_rpt) and wait_time < max_wait:
            import time
            time.sleep(1)
            wait_time += 1
            
        if os.path.exists(setup_rpt):
            print("✔️ Timing report generated")
        else:
            print("❌ Timing report not generated after waiting")
    else:
        print("❌ VPR encountered an error")

    # 提取当前目录下的 report_timing.hold.rpt
    nodes = extract_path_nodes("report_timing.setup.rpt", top_n=10)
    write_nodes_to_file(nodes, "cpdInfo.txt")

finally:
    # 切回原目录
    os.chdir(orig_dir)
