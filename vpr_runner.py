import subprocess
import os

def run_vpr(blif_file: str, arch_file: str, extra_args: list = None) -> int:
    """
    Runs VPR with the specified BLIF file and architecture XML.

    Parameters:
        blif_file (str): Path to the .blif netlist file.
        arch_file (str): Path to the VPR architecture .xml file.
        extra_args (list): Additional command-line arguments for VPR (e.g., ["--route", "--analysis"])

    Returns:
        int: VPR process return code. 0 means success.
    """

    if not os.path.exists(blif_file):
        raise FileNotFoundError(f"BLIF file not found: {blif_file}")
    if not os.path.exists(arch_file):
        raise FileNotFoundError(f"Architecture XML file not found: {arch_file}")

    vpr_path = "/home/wllpro/llwang07/kxzhu/vtr-verilog-to-routing-master/vpr/vpr"
    vpr_cmd = [vpr_path, arch_file, blif_file] + (extra_args if extra_args else [])

    # 拼成字符串，嵌入到 bsub 中
    vpr_cmd_str = " ".join(vpr_cmd)
    bsub_cmd_str = f'bsub -q normal -o /dev/null -e /dev/null "{vpr_cmd_str}"'

    print(f"[VPR-BSUB] Submitting: {bsub_cmd_str}")

    try:
        subprocess.run(bsub_cmd_str, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"[VPR-BSUB] Submission failed with code {e.returncode}")
        return e.returncode
