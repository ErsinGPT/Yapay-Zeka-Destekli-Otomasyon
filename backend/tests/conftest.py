"""
Test configuration - minimal
Each test module handles its own database setup
"""
import pytest
import os

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
