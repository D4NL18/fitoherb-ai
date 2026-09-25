import sys
import os

# Garante que a raiz do projeto está no PYTHONPATH em qualquer ambiente (local e CI)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
