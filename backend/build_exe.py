import PyInstaller.__main__
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, "game.py")
src_origin = os.path.join(os.path.dirname(current_dir), "src")

PyInstaller.__main__.run([
    script_path,
    "--onefile",
    "--noconsole",
    f"--add-data={src_origin}{os.path.pathsep}src",
])