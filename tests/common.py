import subprocess
from subprocess import PIPE, STDOUT
import sys
import yaml
import os
from typing import List, Tuple
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from securenv.cli import SecureEnvApp

dir_path = os.path.dirname(os.path.realpath(__file__))

'''
Common utility functions used through out
the test suite.
'''


def call_securenv(*args) -> Tuple[int, bytes]:
    cmd = ["securenv", *args]
    result = subprocess.run(cmd, stdout=PIPE, stderr=STDOUT)
    return result.returncode, result.stdout


def verify_env_file(env_file: str, variables: List[str]) -> bool:
    found_all_vars = True
    try:
        with open(env_file, "r") as f:
            data = f.read()
            for var in variables:
                if var not in data:
                    found_all_vars = False
    except FileNotFoundError:
        print(f"Error: Unable to find file: {env_file}")
        found_all_vars = False
    return found_all_vars


def create_test_app(env_file: str) -> Tuple[SecureEnvApp, dict]:
    variable_groups = None
    metadata_file = f"{dir_path}/data/test_valid_metadata.yaml"
    try:
        with open(metadata_file, "r") as f:
            variable_groups = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Unable to find file: {metadata_file}")
        exit(1)
    return (SecureEnvApp(
        variable_groups=variable_groups,
        env_file=f"{dir_path}/../{env_file}"
    ), variable_groups)
