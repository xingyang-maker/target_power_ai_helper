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
        "--ai-endpoint", 
        default="", 
        help="QGenie LLM endpoint URL (empty to use default configuration)"
    )
    
    return parser
