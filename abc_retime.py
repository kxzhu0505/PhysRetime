import subprocess
import os

def abc_retime(blif_path: str, cpd_path: str, output_blif: str, retime_mode: int, abc_bin: str ) -> int:
    """
    执行 ABC retime 操作，使用 read_cpd 提供的关键路径节点。

    Args:
        blif_path (str): 输入 .blif 文件路径
        cpd_path (str): 关键路径节点列表文件（由 read_cpd 读取）
        output_blif (str): 输出 .blif 文件路径
        retime_mode (int): retime 模式，默认 -M 7（forward + backward + min-delay）
        abc_bin (str): abc 可执行文件路径（默认在 PATH 中）/home/wllpro/llwang07/kxzhu/abc-master/abc

    Returns:
        int: 返回码，0 表示成功，否则表示失败
    """
    if not os.path.exists(blif_path):
        raise FileNotFoundError(f"BLIF file not found: {blif_path}")
    if not os.path.exists(cpd_path):
        raise FileNotFoundError(f"CPD info file not found: {cpd_path}")

    cmd_str = f'read {blif_path}; read_cpd {cpd_path}; retime -M {retime_mode}; write_blif {output_blif}'
    print(f"[ABC] Running: {cmd_str}")

    try:
        result = subprocess.run([abc_bin, "-c", cmd_str], check=True, capture_output=True, text=True)
        print(result.stdout)
        return 0
    except subprocess.CalledProcessError as e:
        print("[ABC] Error executing command:")
        print(e.stderr)
        return e.returncode

if __name__ == "__main__":
    abc_status = abc_retime(
    blif_path="/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/vtr_flow/benchmarks/blif/diffeq.blif",
    cpd_path="/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/ret/diffeq/cpdInfo.txt",
    output_blif="/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/retdiffeq_retimed.blif",
    retime_mode=7,
    abc_bin="/home/wllpro/llwang07/kxzhu/abc-master/abc"
    )

    if abc_status == 0:
        print("✔️ ABC retime completed successfully.")
    else:
        print("❌ ABC retime failed.")