import sys
import os

# Add the parent directory to sys.path so tests can find 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
