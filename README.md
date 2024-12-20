# Sleeping Barber Problem

## Project Description

This project implements the classic "Sleeping Barber Problem" using multithreaded programming in Python. The program simulates customers (URLs) arriving at a barbershop (barber), where they are processed sequentially. It includes a queue system for customers, logic for adding and processing new customers, and duplicate checking.

## Features

1. **Configuration via config.json**:
   - Input parameters are defined in the `config.json` file.
   - Settings include the maximum number of customers, maximum queue size, and operational intervals.

2. **Customer Processing**:
   - The barber processes customers from the queue.
   - Logic for the barber sleeping when the queue is empty is implemented.

3. **Customer Producer**:
   - Generates new customers and adds them to the queue.
   - Ensures no duplicate customers are processed.

4. **Logging**:
   - Logs are stored in the `logs` directory.
   - Includes logs for customer processing and overall application execution.

5. **Exception Handling**:
   - Handles duplicate inputs and queue overflow.
   - Responds to errors in page downloading or invalid inputs.

6. **Design Patterns Used**:
   - **Singleton**: For managing configuration (`Config` class).
   - **Producer-Consumer**: For synchronizing customer production (URLProducer) and processing (Crawler).
   - **Observer**: For reacting to application state changes, such as stopping processes.

## File Structure

```
ZETA/
├── logs/                   # Log files
├── src/                    # Source code
│   ├── main.py             # Main entry point
│   ├── app_controller.py   # Application controller
│   ├── barber.py           # Barber and Customer classes
│   ├── utils.py            # Utility functions (logging, data processing)
│   └── config.json         # Configuration file
├── requirements.txt        # Python library requirements
└── README.md               # Project documentation
```

## Installation and Running Instructions

### Prerequisites
- Python 3.9 or higher
- PIP (Python Package Installer)
- Windows (CMD or PowerShell) other platforms (Linux, MacOS) are also supported, but without specific instructions for installation and running.

### Steps to Install and Run

#### Windows CMD

1. **Download the project**:
   - Clone or download the project repository to your computer.
   - You have to be in the project directory, where the `requirements.txt` file is located.

2. **Create a virtual environment**:
   ```cmd
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

5. **Set PYTHONPATH**:
   ```cmd
   set PYTHONPATH=%CD%
   ```

6. **Run the program**:
   ```cmd
   python src/main.py
   ```

#### Windows PowerShell

1. **Download the project**:
   - Clone or download the project repository to your computer.
   - You have to be in the project directory, where the `requirements.txt` file is located.

2. **Create a virtual environment**:
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - If execution policies are restricted:
     ```powershell
     Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
     
     And answer 'Y' or 'A' to the prompt.
     ```
   - Activate the environment:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

4. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

5. **Set PYTHONPATH**:
   ```powershell
   $env:PYTHONPATH = $PWD
   ```

6. **Run the program**:
   ```powershell
   python src/main.py
   ```

### Example Usage

After running the program, the console will display an interface for commands:
- `help` - Displays the help menu.
- `start` - Starts the simulation.
- `stop` - Stops the simulation.
- `status` - Displays the current application status.
- `edit` - Allows editing the configuration.
- `exit` - Exits the program.
- `explain` - Explains the structure of the configuration file.

## Test Report

### Test Results

1. **Functionality Tests**:
   - Simulation works correctly with various configurations.
   - Duplicate URLs are not processed.
   - Logs are saved properly.

2. **Error Handling Tests**:
   - Invalid URLs are ignored.
   - Queue overflow is correctly handled and logged.

3. **Performance Tests**:
   - Successfully processed up to 100 customers with maximum queue size.
   - Tested on Windows and Linux platforms.



## Sources Used

1. [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
2. [Python OS Module Documentation](https://docs.python.org/3/library/os.html)
3. [Python Datetime Documentation](https://docs.python.org/3/library/datetime.html)
4. [Python Queue Documentation](https://docs.python.org/3/library/queue.html)
5. [Requests Library Documentation](https://docs.python-requests.org/en/latest/)
6. [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
7. [Python Official Documentation](https://docs.python.org/3/)
8. [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)
9. [PowerShell Execution Policies Documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies)

