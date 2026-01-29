from pathlib import Path
import sys

# Ensure project root is on sys.path when running as a script
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
	sys.path.insert(0, str(project_root))
