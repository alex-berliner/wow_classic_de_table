import subprocess
def docmd(cmd):
    return subprocess.check_output(cmd.split(" ")).decode("utf-8")
