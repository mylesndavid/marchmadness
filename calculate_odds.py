import random
import pandas as pd

winrate_df = pd.read_csv("winrates.csv")

# winrate_dict = {
#     1: 0.797213622,
#     2: 0.706225681,
#     3: 0.653758542,
#     4: 0.61209068,
#     5: 0.535714286,
#     6: 0.512578616,
#     7: 0.472789116,
#     8: 0.417293233,
#     9: 0.380952381,
#     10: 0.37751004,
#     11: 0.4,
#     12: 0.336170213,
#     13: 0.2,
#     14: 0.138121547,
#     15: 0.093023256,
#     16: 0.012658228
# }

def get_winrate(seed, round):
    try:
        winrate = winrate_df[(winrate_df['seed'] == seed) & (winrate_df['round'] == round)].iloc[0]['winrate']
        return winrate
    except:
        return None

def get_odds(seed1, seed2, round):
    winrate1 = get_winrate(seed1, round)
    winrate2 = get_winrate(seed2, round)
    
    if winrate1 is None or winrate2 is None:
        raise ValueError("Invalid seed value")
    
    odds = winrate1 / (winrate1 + winrate2)
    return odds

def get_win(seed1, seed2, round):
    odds = get_odds(seed1, seed2, round)
    return seed1 if random.random() < odds else seed2
