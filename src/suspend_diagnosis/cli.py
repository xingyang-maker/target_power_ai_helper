#!/usr/bin/env python3
"""
Command Line Interface for Android Suspend Diagnosis Tool

This module defines the command-line arguments for the tool.
"""
import argparse


def build_parser() -> argparse.ArgumentParser:
    """
    Build and configure the command-line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(description="Android Suspend Diagnosis Tool")
    
    parser.add_argument(
        "--adb", 
        default="adb",
        help="Path to ADB executable (default: 'adb')"
    )
    
    parser.add_argument(
        "--device", 
        default="",
        help="Target device serial number (empty for default device)"
    )
    
    parser.add_argument(
        "--out", 
        default="./reports",
        help="Output directory for reports (default: './reports')"
    )
    
    parser.add_argument(
        "--case-dir",
        default="",
        help="Path to a directory containing pre-collected log files (dmesg.txt, dumpsys_suspend.txt, suspend_stats.txt). Files can be partial - the tool will analyze whatever logs are available and skip missing ones."
    )
    
    return parser
