import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from myth_fact_quiz import main as quiz_main
quiz_main()
