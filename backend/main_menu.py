import sys
import os

# Append paths cleanly so modules can reference each other perfectly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game_controller import NarrativeGameController
from engine.anime_minigame import run_generator_minigame

def boot_system_console():
    controller = NarrativeGameController()
    
    while True:
        print("\n==================================================")
        print("         DETECTIVE OS MAIN HUB (TERMINAL v1.95)   ")
        print("==================================================")
        print(" [1] [Case Manager] Open Fresh Incident File")
        print(" [2] [Database]     View Cross-Exam Suspect Profiles")
        print(" [3] [Clock]        Advance System Operations Turn")
        print(" [4] [Mini-Game]    Launch Local Utility: ANIME_GEN.EXE")
        print(" [5] [System]       Power Down Terminal")
        print("==================================================")
        
        selection = input("Select operation routing (1-5): ").strip()
        
        if selection == "1":
            controller.initialize_new_case()
            print("\n[✓] Fresh instance logged. Suspect indices filled with inventories.")
        elif selection == "2":
            if not controller.state["suspects"]:
                print("\n[!] Access Denied: Initialize case file protocols first.")
                continue
            for s in controller.state["suspects"]:
                print(f"\n=================== SUSPECT PROFILE ===================")
                print(f" Name: {s['name']} | Logged: {s['date_filed']}")
                print(f" Occupation: {s['occupation']} | Portrait Key: {s['portrait']}")
                print(f" Preference: Likes {s['likes']} / Dislikes {s['dislikes']}")
                print(f" Alibi Log: {s['alibi']}")
                print(f" Evidence Carried: {[i['name'] for i in s['inventory']]}")
        elif selection == "3":
            if not controller.state["case_active"]:
                print("\n[!] Operational Warning: No target cases running to increment.")
                continue
            event = controller.trigger_turn_advance()
            print(f"\n[✓] Operational turn shifted to increment: {controller.state['current_turn']}")
            if event:
                print(f" ALERT: {event}")
        elif selection == "4":
            run_generator_minigame()
        elif selection == "5":
            print("\nFlushing memory allocation tracks. Terminal shut down down clean.")
            break
        else:
            print("\nInvalid operation entry string.")

if __name__ == "__main__":
    boot_system_console()