# Android Suspend Diagnosis Tool

A command-line tool for diagnosing Android device suspend issues by collecting and analyzing logs.

## Overview

This tool helps diagnose Android suspend-related issues by:

1. **Analyzing existing logs** from a local directory (primary use case)
2. **Collecting fresh logs** from an Android device using ADB (when needed)
3. Detecting suspend failures using a systematic 3-step analysis process
4. Generating comprehensive reports in both Markdown and HTML formats
5. Providing AI-powered analysis and recommendations (optional)

## Features

- **Analyze pre-collected logs**: Point to any directory containing suspend-related log files
- **Collect fresh logs**: Automatically gather logs from connected Android devices via ADB
- **3-step analysis process**: 
  - Step 1: Check suspend statistics (`/d/suspend_stats`)
  - Step 2: Analyze wakelocks (`dumpsys suspend_control_internal`)
  - Step 3: Examine kernel messages (`dmesg`)
- **Multiple output formats**: Generate both Markdown and HTML reports
- **AI-powered insights**: Get detailed analysis and recommendations (requires QGenie)
- **Flexible input**: Works with three essential log files:
  - `dmesg.txt` - Kernel messages
  - `dumpsys_suspend.txt` - Suspend control internal state  
  - `suspend_stats.txt` - Suspend statistics from `/d/suspend_stats`

## 📋 Log Collection Guide

For detailed instructions on how to properly collect the required log files, see: **[LOG_COLLECTION_GUIDE.md](LOG_COLLECTION_GUIDE.md)**

This guide covers:
- Step-by-step log collection procedures
- Required permissions and device setup
- Common issues and troubleshooting
- Log quality verification
- Best practices for different scenarios

### Quick Log Collection

We provide convenient scripts for quick log collection:

**Windows:**
```cmd
scripts\collect_logs.bat
```

**Linux/macOS:**
```bash
./scripts/collect_logs.sh
```

These scripts automatically handle device detection, permission checks, and collect all required log files with quality verification.

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
usage: suspend-diagnosis [-h] [--adb ADB] [--device DEVICE] [--out OUT] 
                         [--case-dir CASE_DIR]

Android Suspend Diagnosis Tool

options:
  -h, --help            show this help message and exit
  --adb ADB             Path to ADB executable (default: 'adb')
  --device DEVICE       Target device serial number (empty for default device)
  --out OUT             Output directory for reports (default: './reports')
  --case-dir CASE_DIR   Path to a directory containing pre-collected log files 
                        (dmesg.txt, dumpsys_suspend.txt, suspend_stats.txt).
                        Files can be partial - the tool will analyze whatever 
                        logs are available and skip missing ones.
```

### Examples

**Collect logs from the default connected device:**
```bash
python bin/suspend_diagnosis
```

**Collect logs from a specific device:**
```bash
python bin/suspend_diagnosis --device DEVICE_SERIAL_NUMBER
```

**Analyze pre-collected logs from a local directory:**
```bash
python bin/suspend_diagnosis --case-dir ./cases/test_case1
```

This is useful when you have already saved logs and want to re-analyze them without 
reconnecting to the device.

**Specify a custom output directory:**
```bash
python bin/suspend_diagnosis --out /path/to/output/directory
```

**Combine options:**
```bash
python bin/suspend_diagnosis --case-dir ./cases/test_case1 --out ./my_reports
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
