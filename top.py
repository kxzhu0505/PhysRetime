import os
import shutil
import time
from abc_retime import abc_retime
from vpr_runner import run_vpr
import retime_prep as retime

# 配置
work_dir = "/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/ret/"
benchmark = "diffeq_test"
bench_dir = os.path.join(work_dir, benchmark)
arch_path = "/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/vtr_flow/arch/timing/k6_frac_N10_frac_chain_mem32K_40nm.xml"
blif_src = "/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/vtr_flow/benchmarks/blif/diffeq.blif"
max_iter = 5  # 最大迭代次数
top_n = 10    # 提取前N条路径

os.makedirs(bench_dir, exist_ok=True)
orig_dir = os.getcwd()

timing_info = retime.extract_first_latch_params(blif_src)

try:
    for i in range(max_iter):
        print(f"\n=== 第{i}轮 ===")
        iter_dir = os.path.join(bench_dir, f"iter{i}")
        os.makedirs(iter_dir, exist_ok=True)
        os.chdir(iter_dir)

        # 1. 拷贝输入blif到本轮目录
        if i == 0:
            # 第一轮用初始blif
            blif_file = os.path.join(iter_dir, f"{benchmark}_iter0.blif")
            if not os.path.exists(blif_file):
                shutil.copy(blif_src, blif_file)
        else:
            # 之后每轮用上一轮输出
            prev_iter_dir = os.path.join(bench_dir, f"iter{i-1}")
            prev_blif = os.path.join(prev_iter_dir, f"{benchmark}_iter{i}.blif")
            blif_file = os.path.join(iter_dir, f"{benchmark}_iter{i}.blif")
            shutil.copy(prev_blif, blif_file)

        # 2. 跑VPR
        rpt_file = f"report_timing.setup.iter{i}.rpt"
        cpd_file = f"cpdInfo.iter{i}.txt"
        status = run_vpr(blif_file, arch_path)
        if status != 0:
            print("❌ VPR运行失败，终止迭代")
            break

        # 3. 等待报告生成
        wait_time = 0
        while not os.path.exists("report_timing.setup.rpt") and wait_time < 600:
            time.sleep(1)
            wait_time += 1
        if not os.path.exists("report_timing.setup.rpt"):
            print("❌ 未生成report_timing.setup.rpt，终止迭代")
            break
        shutil.copy("report_timing.setup.rpt", rpt_file)

        # 4. 提取路径信息
        nodes = retime.extract_path_nodes("report_timing.setup.rpt", top_n=top_n)
        retime.write_nodes_to_file(nodes, cpd_file)

        # 5. 终止条件（可选）

        # 6. 调用abc做retiming，生成新blif
        if i < max_iter - 1:
            new_blif = os.path.join(iter_dir, f"{benchmark}_iter{i+1}.blif")
            retime_status = abc_retime(blif_file, cpd_file, new_blif, 7, "/home/wllpro/llwang07/kxzhu/abc-master/abc")
            if retime_status != 0:
                print("❌ ABC优化失败，终止迭代")
                break
            retime.optimize_latch_lines_inplace(new_blif, timing_info)
        # 下一轮会自动用新目录和新blif

        os.chdir(bench_dir)  # 回到主目录，准备下一轮

    # 统计所有轮次的delay和Fmax
    retime.stat_all_iters(bench_dir)
finally:
    os.chdir(orig_dir)
