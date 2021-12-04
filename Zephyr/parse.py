import pathlib
import warnings

import tqdm.auto as tqdm
import zephyrus_sc2_parser

REPLAY_DIRECTORY = "C:/Uni/s2protocol-master/replay"
PLAYER_NAME = "Pexo"
OUTPUT_CSV = "replay.csv"

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    replays = list(pathlib.Path(REPLAY_DIRECTORY).glob("*.SC2Replay"))
    parsed_replays = {}
    for replay_file in tqdm.tqdm(replays):
        try:
            replay = zephyrus_sc2_parser.parse_replay(replay_file, local=True)
        except Exception as e:
            print(f"Failed for {replay_file}: {e}")
            continue
        parsed_replays[replay_file] = replay
        
# utility function to get our own player ID
def grab_player_id(players, name = PLAYER_NAME):
    for key, player in players.items():
        if player.name == name:
            break        
    else:
        key = None
    return key


results = []
for replay_file, replay in parsed_replays.items():
    players, timeline, engagements, summary, meta = replay
    if all(item is None for item in replay):
        print(f"Failed to parse for {replay_file}")
        continue
    my_id = grab_player_id(players, PLAYER_NAME)
    enemy_id = 1 if (my_id == 2) else 2
    
    mmr = summary['mmr'][my_id]

    enemy_mmr = summary['mmr'][enemy_id]
    results.append(
        dict(
            replay_file = replay_file,
            time_played_at = meta['time_played_at'],
            win = meta["winner"] == my_id,
            mmr=mmr,
            enemy_mmr=enemy_mmr,
            mmr_diff = mmr - enemy_mmr,
            race = players[my_id].race,
            enemy_race = players[enemy_id].race,
            enemy_nickame = players[enemy_id].name,
            map_name = meta["map"],
            duration = meta['game_length'],
        )
    )

print(f"We successfully pulled data out of {len(results)} replays, which is {len(results)/len(replays):.2%} of the total!")

import pandas as pd
df = pd.DataFrame(results)
#df['mmr_diff'] = df.mmr - df.enemy_mmr
df.to_csv(OUTPUT_CSV)