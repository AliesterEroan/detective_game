import os
import subprocess
import sys

def run_generator_minigame():
    """Executes your working character generator script as an in-game desktop utility."""
    print("\n[Executing Terminal App]: C:\\APPS\\ANIME_GEN.EXE...")
    
    # Dynamically maps directly to your test_character_generator.py script position
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generator_script = os.path.join(base_path, "test_character_generator.py")
    
    if os.path.exists(generator_script):
        # Boots it up using your active Python environment environment cleanly
        subprocess.run([sys.executable, generator_script])
        print("[App Return]: Context closed. Output saved inside output/ folder.")
    else:
        print(f"[File Error]: ANIME_GEN.EXE not found at {generator_script}")