import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

SCRIPT = Path(__file__).with_name("fixturepress.py")
def run(*args, ok=0):
    result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    assert result.returncode == ok, (args, result.stdout, result.stderr)
    return result

def git(*args):
    subprocess.run(["git", *args], check=True)

with tempfile.TemporaryDirectory() as tmp:
    os.chdir(tmp)
    Path("input").write_text('{"keep":1,"parts":[1,2,3]}')
    code="import sys,json; hit='keep' in json.load(open(sys.argv[1])); print('BUG' if hit else 'ok'); sys.exit(int(hit))"
    run("input","-o","out","--",sys.executable,"-c",code,"{}")
    assert json.loads(Path("out").read_text())=={"keep":1}
