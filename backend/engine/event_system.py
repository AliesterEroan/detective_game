import random

EVENTS_POOL = [
    "An anonymous secure line log routes an untraceable tip to your console desk.",
    "A baseline terminal sector crash temporarily restricts network database visibility.",
    "Internal Oversight requests an immediate diagnostic of open case files.",
    "A key witness changes their statement regarding the suspect's description."
]

def process_random_events(game_state):
    """Evaluates turn steps to log random terminal conditions."""
    if random.random() < 0.40:  # 40% probability per action turn
        selected_event = random.choice(EVENTS_POOL)
        game_state["logs"].append(f"[SYS EVENT]: {selected_event}")
        return selected_event
    return None