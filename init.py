import os


os.chdir(os.path.abspath(os.path.dirname(__file__)))


os.makedirs('build/compiled_scripts', exist_ok=True)
os.makedirs('patches', exist_ok=True)
