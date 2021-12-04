from pathlib import Path
from zephyrus_sc2_parser import parse_replay, parser


data = parse_replay("replay.SC2Replay", local=True)
winner = data[0][data[4]["winner"]]
buildOrder = winner.objects
timeline = data[1]
for dataPoint in timeline:
    print(dataPoint[1]["gameloop"])
#replays = Path('../replays')

#def recurse(dir_path):
 #   """
  #  Recursively searches directories to parse replay files
   # """
#    for obj_path in dir_path.iterdir():
 #       if obj_path.is_file():
  #          replay = parse_replay(obj_path)
            # do stuff with the data
   #     elif obj_path.is_dir():
    #        recurse(obj_path)


#recurse(replays)