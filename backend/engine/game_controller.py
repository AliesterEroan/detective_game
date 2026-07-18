import os
import random
import sys
import subprocess
from .profile_gen import generate_suspect_profile
from .inventory_gen import generate_character_inventory
from .event_system import process_random_events

class DetectiveGameController:
    def __init__(self):
        self.state = {
            "case_active": False,
            "current_turn": 0,
            "suspects": [],
            "logs": ["Terminal System initialized securely."],
            "guilty_index": None
        }

    def start_new_case(self):
        self.state["case_active"] = True
        self.state["current_turn"] = 1
        self.state["suspects"] = []
        self.state["logs"].append("New Case File Opened: Murder at the Terminal Room.")
        
        genders = ["male", "female", "male"]
        self.state["guilty_index"] = random.randint(0, len(genders) - 1)
        
        for idx, gender in enumerate(genders):
            is_guilty = (idx == self.state["guilty_index"])
            profile = generate_suspect_profile(idx, gender)
            profile["inventory"] = generate_character_inventory(is_guilty=is_guilty)
            self.state["suspects"].append(profile)

    def advance_turn(self):
        if not self.state["case_active"]:
            return None
        self.state["current_turn"] += 1
        event = process_random_events(self.state)
        return event

    def trigger_portrait_minigame(self):
        """Invokes the external test_character_generator script safely."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        generator_script = os.path.join(base_dir, "test_character_generator.py")
        
        if os.path.exists(generator_script):
            # Executes the script in the current active python environment
            subprocess.run([sys.executable, generator_script])
            return True
        return False