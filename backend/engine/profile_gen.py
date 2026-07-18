import random

FIRST_NAMES = ["Jack", "Vincent", "Raymond", "Arthur", "Harvey", "Victor", "Leo", "Julian"]
LAST_NAMES = ["Marlowe", "Cross", "Vance", "Doyle", "Sterling", "Pendleton", "Kerr", "Gaines"]
OCCUPATIONS = ["Private Eye", "Nightclub Owner", "Corporate Security", "Dock Worker", "Journalist", "Safe Cracker"]
DATES_FILED = ["Oct 12, 1995", "Nov 03, 1995", "Jan 24, 1996", "Mar 15, 1996"]
INTERESTS = ["Jazz Music", "Cheap Bourbon", "Cigarettes", "Classic Cars", "Rainy Nights", "High-Stakes Poker"]

def generate_suspect_profile(suspect_id, gender):
    """Generates a unique biographical case file identity."""
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    job = random.choice(OCCUPATIONS)
    date_str = random.choice(DATES_FILED)
    likes_dislikes = random.sample(INTERESTS, 2)
    
    return {
        "id": suspect_id,
        "name": name,
        "gender": gender,
        "date_filed": date_str,
        "occupation": job,
        "likes": likes_dislikes[0],
        "dislikes": likes_dislikes[1],
        "history": "Subject flagged in municipal archives. Records show recurring links to local trade smuggling.",
        "alibi": "Claims to have been reviewing terminal log tracks during the recorded incident window."
    }