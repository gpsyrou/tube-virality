import os
import json
import unittest
from pathlib import Path

# config file exists two directories above
PROJECT_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
CONFIGS_PATH = os.path.join(PROJECT_PATH, 'config')
PROJECT_CONFIG_PATH = os.path.join(CONFIGS_PATH, 'project_config.json')

with open(PROJECT_CONFIG_PATH) as project_config_json:
    project_config = json.load(project_config_json)
    project_config_json.close()

loader = unittest.TestLoader()
start_path = project_config['dir'].get('tests')
suite = loader.discover(start_path)

runner = unittest.TextTestRunner()
runner.run(suite)
