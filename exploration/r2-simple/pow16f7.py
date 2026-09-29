import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simple import make
setup, journey, P = make(h="pow", p=16, b=0.8, min_sim=0.7)
