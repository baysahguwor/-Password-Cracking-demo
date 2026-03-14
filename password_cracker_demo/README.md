# Password Cracking Visualizer (Cybersecurity Demo)

A desktop cybersecurity education project that simulates how weak passwords can be cracked using common attack strategies.

This application is designed for training, classroom demonstrations, and portfolio use. It visualizes attack attempts, speed, progress, and outcomes in a modern dashboard.

## Important Safety Notice

This tool is for educational simulation only.

- It only runs locally on user-entered passwords.
- It does not attack networks, systems, or real accounts.
- It does not include exploitation, scanning, or unauthorized access features.

## Features

- Password strength analysis
  - Strength categories: Very Weak, Weak, Moderate, Strong, Very Strong
  - Factors: length, uppercase, lowercase, numbers, symbols, common words
  - Estimated crack time display
- Brute force simulation
  - Character-combination guessing (a-z + 0-9)
  - Live attempts, speed, elapsed time, progress
- Dictionary attack simulation
  - Uses a local common-password wordlist
- Hybrid attack simulation
  - Dictionary words with numeric and basic mutation patterns
- Live dashboard visuals
  - Progress bars
  - Attempt/speed counters
  - Cracking timeline chart
  - Terminal-style attack feed
- Attack result summary panel
- SQLite attack logging
  - Stores timestamp, attack type, attempts, time, result, and password length
- Quick demo password buttons
- Security education tips panel

## Tech Stack

- Python 3.10+
- PySide6 (GUI)
- SQLite3 (local logging)
- threading, hashlib, time
- Pure PySide6 chart rendering (no Matplotlib required)

## Project Structure

```text
password_cracker_demo/
├── main.py
├── password_analyzer.py
├── brute_force_engine.py
├── dictionary_attack.py
├── hybrid_attack.py
├── attack_logger.py
├── database.py
├── attack_logs.db
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── dashboard.py
│   └── charts.py
└── wordlists/
    └── common_passwords.txt
```

## Installation

1. Clone or download this project.
2. Open a terminal in the project folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the App

From the project root:

```bash
python main.py
```

The application opens maximized and loads the dashboard UI.

## How to Use

1. Enter a password (or click one of the quick demo passwords).
2. Click Analyze Password to view strength and estimated crack time.
3. Start one of the attacks:
   - Brute Force
   - Dictionary
   - Hybrid
4. Watch live metrics:
   - Attempts
   - Speed (guesses/sec)
   - Elapsed time
   - Progress
   - Timeline chart
5. Review the Attack Result panel and Attack Log table.
6. Use Stop Attack to manually interrupt a running simulation.

## Demo Password Suggestions

- password123
- admin
- Welcome@123
- MyStrongPass!2026

These show clear differences in estimated strength and cracking behavior.

## Database Logging

Attack results are stored in a local SQLite database file:

- Database file: attack_logs.db
- Table: attack_logs
- Columns:
  - id
  - timestamp
  - password_length
  - attack_type
  - attempts
  - time_taken
  - result

## Notes on Simulation Behavior

- Brute force is intentionally bounded for demo usability.
- Long, complex passwords may not be found within simulation limits.
- Not found in simulation should be interpreted as stronger resistance in this demo context.

## Troubleshooting

### App does not start

- Confirm Python version is 3.10 or newer.
- Confirm dependency installed:

```bash
pip install -r requirements.txt
```

### UI feels slow during attack

- Use shorter test passwords for brute force demos.
- Stop the current attack and switch to dictionary/hybrid for faster classroom runs.

### Permission error activating venv on Windows

If script execution is blocked, run PowerShell as user and allow local scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Educational Outcomes

This project demonstrates:

- Why weak passwords are risky
- How common attack approaches work
- Why length and complexity dramatically increase cracking effort
- Why security best practices (MFA, unique passwords, password managers) matter

## Disclaimer

The authors and contributors are not responsible for misuse. Use this software only in legal, authorized, and educational contexts.
