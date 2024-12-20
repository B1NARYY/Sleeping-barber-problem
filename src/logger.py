import logging
import os
from datetime import datetime

"""
Logger setup for the Barber Simulation:
- Creates a structured directory for log files.
- Initializes a logger for logging messages during the simulation.
"""

# Define the root directory for logs
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
logs_dir = os.path.join(project_root, 'logs')

# Ensure the logs directory exists
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Create a unique directory for each run
run_dir_name = datetime.now().strftime("run_%Y%m%d_%H%M%S")
run_dir_path = os.path.join(logs_dir, run_dir_name)

# Check if the directory exists to prevent errors
if not os.path.exists(run_dir_path):
    os.makedirs(run_dir_path)

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define the log format
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Path to the current run's log directory
RUN_DIR_PATH = run_dir_path
