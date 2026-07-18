import random

GENERIC_ITEMS = [
    {"name": "Silver Zippo", "is_clue": True, "desc": "Engraved with initials. Smells heavily of fluid."},
    {"name": "Stained Notepad", "is_clue": True, "desc": "Indentation reveals an archived room entry: 304."},
    {"name": "Brass Key", "is_clue": False, "desc": "A common un-marked master tumbler key."},
    {"name": "Pocket Watch", "is_clue": True, "desc": "Glass shattered. Hands are frozen precisely at 11:42 PM."},
    {"name": "Matchbook", "is_clue": False, "desc": "Sourced from the diner down the street block."}
]

def generate_character_inventory(is_guilty=False):
    """Assembles item inventories, guaranteeing incriminating evidence for the true culprit."""
    inventory = random.sample(GENERIC_ITEMS, random.randint(2, 3))
    inventory = [item.copy() for item in inventory]  # Avoid reference sharing issues
    
    if is_guilty:
        inventory.append({
            "name": "Modified Lockpick Set",
            "is_clue": True,
            "desc": "Scratched from intensive recent use on physical terminal access panels."
        })
    return inventory