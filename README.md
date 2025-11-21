# Android Suspend Diagnosis Tool

A command-line tool for diagnosing Android device suspend issues by collecting and analyzing logs.

## Overview

This tool helps diagnose Android suspend-related issues by:

1. Collecting essential logs from an Android device using ADB
2. Analyzing logs to detect suspend failures
3. Generating comprehensive reports in both Markdown and HTML formats
4. Providing AI-powered analysis of the collected logs (optional)

## Features

- Collects three essential evidence files:
  - `dmesg.txt` - Kernel messages
  - `dumpsys_suspend.txt` - Suspend control internal state
  - `suspend_stats.txt` - Suspend statistics from `/d/suspend_stats`
- Detects suspend failures based on known patterns
- Provides AI-powered analysis and recommendations (requires QGenie)
- Outputs both Markdown and HTML reports

## Requirements

- Python 3.9+
- Android Debug Bridge (ADB)
- Connected Android device with USB debugging enabled
- Python packages:
  - matplotlib
  - markdown
  - qgenie (optional, for AI analysis)

## Installation

### Option 1: Install as a Package (Recommended)

1. Clone this repository:
   ```bash
   git clone https://github.com/xingyang-maker/suspend_mvp.git
   cd suspend_mvp
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

3. After installation, you can run the tool from anywhere:
   ```bash
   suspend-diagnosis
   ```

### Option 2: Run Directly from Source

1. Clone this repository:
   ```bash
   git clone https://github.com/xingyang-maker/suspend_mvp.git
   cd suspend_mvp
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the tool using Python:
   ```bash
   python bin/suspend_diagnosis
   ```

## Usage

Basic usage:

```bash
python bin/suspend_diagnosis
```

Or if installed as a package:

```bash
suspend-diagnosis
```

This will collect logs from the default connected device and generate a report in the `./reports` directory.

### Command-line Options

```
usage: suspend-diagnosis [-h] [--adb ADB] [--device DEVICE] [--out OUT] [--ai-endpoint AI_ENDPOINT]

Android Suspend Diagnosis Tool

options:
  -h, --help            show this help message and exit
  --adb ADB             Path to ADB executable (default: 'adb')
  --device DEVICE       Target device serial number (empty for default device)
  --out OUT             Output directory for reports (default: './reports')
  --ai-endpoint AI_ENDPOINT
                        QGenie LLM endpoint URL (empty to use default configuration)
```

### Examples

Collect logs from a specific device:
```bash
python bin/suspend_diagnosis --device DEVICE_SERIAL_NUMBER
```

Or if installed as a package:
```bash
suspend-diagnosis --device DEVICE_SERIAL_NUMBER
```

Specify a custom output directory:
```bash
suspend-diagnosis --out /path/to/output/directory
```

## Report Structure

The generated reports include:

1. **Conclusion** - Whether a suspend failure was detected
2. **Rule-based Criteria** - Specific reasons for the failure determination
3. **Evidence Files** - List of collected log files (dmesg.txt, dumpsys_suspend.txt, suspend_stats.txt)
4. **AI Analysis** (if available) - AI-powered analysis and recommendations
5. **Verification Checklist** - Steps to verify that the issue has been resolved

## Project Structure

```
.
├── src/                    # Source code directory
│   └── suspend_diagnosis/  # Main package
│       ├── __init__.py     # Package initialization
│       ├── main.py         # Main functionality
│       ├── cli.py          # Command-line interface definition
│       ├── core/           # Core functionality
│       │   ├── __init__.py
│       │   ├── collector.py # Log collection from Android devices
│       │   ├── analyzer.py # Log analysis and suspend failure detection
│       │   ├── ai.py       # AI-powered analysis using QGenie
│       │   ├── utils.py    # Utility functions
│       │   └── report/     # Report generation
│       │       ├── __init__.py
│       │       ├── markdown_builder.py # Markdown report generation
│       │       └── html_renderer.py    # HTML report generation with charts
│       └── models/         # Data models
│           ├── __init__.py
│           └── types.py    # Type definitions
├── bin/                    # Executable scripts
│   └── suspend_diagnosis   # Main entry point script
├── reports/                # Generated reports (default location)
├── README.md               # Documentation
├── requirements.txt        # Dependencies
├── setup.py                # Package installation script
├── LICENSE                 # License file
└── .gitignore              # Git ignore file
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
