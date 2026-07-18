import os
import logging
from psd_tools import PSDImage

# Setup log tracing
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Check if PSDs are in parent folder or current folder
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.exists(os.path.join(os.path.dirname(SCRIPT_DIR), "Male.psd")) else SCRIPT_DIR
SRC_DIR = os.path.join(ROOT_DIR, 'src')

def sanitize_folder_name(name):
    """Cleans layer group names to standard system folders."""
    return name.lower().strip().replace(" ", "_").replace("/", "_").replace("<", "").replace(">", "")

def perfect_extract(psd_filename):
    psd_path = os.path.join(ROOT_DIR, psd_filename)
    if not os.path.exists(psd_path):
        logging.error(f"Could not locate target PSD at: {psd_path}")
        return

    logging.info(f"Opening stable layout context for: {psd_filename}")
    psd = PSDImage.open(psd_path)
    prefix = psd_filename.split('.')[0].lower()

    # Recursive function to disable everything completely
    def hide_everything(container):
        for layer in container:
            layer.visible = False
            if layer.is_group():
                hide_everything(layer)

    # Core extraction loop tracking exact group structures
    for group in psd:
        if group.is_group() and "layer_set" not in group.name.lower():
            group_folder = sanitize_folder_name(group.name)
            output_path = os.path.join(SRC_DIR, prefix, group_folder)
            os.makedirs(output_path, exist_ok=True)
            
            logging.info(f"Processing category folder: [{group.name.upper()}] -> Exporting items...")

            for layer in group:
                if "layer_set" in layer.name.lower() or layer.name.strip() == "":
                    continue

                # 1. Reset document visibility back to a clean hidden state
                hide_everything(psd)
                
                # 2. Force ONLY the parent group folder and this single asset layer to be active
                group.visible = True
                layer.visible = True
                
                if layer.is_group():
                    for sub_layer in layer:
                        sub_layer.visible = True

                # 3. Explicitly hide the canvas background layer if detected to keep things transparent
                for root_layer in psd:
                    if not root_layer.is_group() and root_layer.name.lower().strip() in ["paper", "background"]:
                        root_layer.visible = False

                # 4. Composite full canvas cleanly using accurate positioning bounds
                full_canvas_frame = psd.composite()
                
                item_filename = sanitize_folder_name(layer.name) + ".png"
                save_destination = os.path.join(output_path, item_filename)
                
                # Save out the beautifully isolated transparent canvas frame
                full_canvas_frame.save(save_destination, "PNG")
                logging.info(f"  [✓] Saved clean layer asset: {prefix}/{group_folder}/{item_filename}")

    logging.info(f"--- Finished perfect asset extraction for {psd_filename}! ---\n")

if __name__ == "__main__":
    print(f"Project Directory detected: {ROOT_DIR}")
    perfect_extract("Male.psd")
    perfect_extract("Female.psd")