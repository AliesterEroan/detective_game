import os
import random
from psd_tools import PSDImage

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Auto-detect root path where the PSDs live
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.exists(os.path.join(os.path.dirname(SCRIPT_DIR), "Male.psd")) else SCRIPT_DIR
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clear_visibility(container):
    """Recursively hides all layers and groups inside the PSD document context."""
    for layer in container:
        layer.visible = False
        if layer.is_group():
            clear_visibility(layer)

def generate_perfect_character(psd_filename):
    psd_path = os.path.join(ROOT_DIR, psd_filename)
    if not os.path.exists(psd_path):
        print(f"Skipping: {psd_filename} not found at {psd_path}")
        return

    print(f"\n=== GENERATING COMPOSITE FOR: {psd_filename.upper()} ===")
    psd = PSDImage.open(psd_path)

    # 1. Reset document canvas visibility state completely
    clear_visibility(psd)

    # 2. Iterate through natural bottom-to-top Photoshop layers sequence
    for element in psd:
        # Handle un-grouped structural layer rows (like standalone backgrounds)
        if not element.is_group():
            if element.name.lower().strip() in ["paper", "background"]:
                # Keep hidden to ensure crisp alpha-channel transparency maps
                element.visible = False 
            else:
                element.visible = True
            continue

        # Process main trait folders (Hair, Clothes, Features, etc.)
        if element.is_group() and "layer_set" not in element.name.lower():
            element.visible = True # Keep the container group folder active
            
            # Select individual components or variation sets inside this tray
            choices = [l for l in element if l.name.strip() != "" and "layer_set" not in l.name.lower()]
            
            if choices:
                chosen_variation = random.choice(choices)
                chosen_variation.visible = True
                
                # If the chosen asset is a nested folder itself, turn all its interior layers on
                if chosen_variation.is_group():
                    for deep_layer in chosen_variation:
                        deep_layer.visible = True
                        
                print(f"  [+] Layer Group '{element.name}' -> Loaded Option: '{chosen_variation.name}'")

    print("Rendering native PSD document structure...")
    final_img = psd.composite()

    # Save to corresponding gender output name
    gender = psd_filename.split('.')[0].lower()
    save_path = os.path.join(OUTPUT_DIR, f"final_perfect_{gender}.png")
    final_img.save(save_path, "PNG")
    print(f"Success! Perfect {gender} portrait saved to:\n -> {save_path}")

if __name__ == "__main__":
    # Process both character configurations in sequence
    generate_perfect_character("Male.psd")
    generate_perfect_character("Female.psd")
    print("\n All character engine generation sweeps completed successfully!")