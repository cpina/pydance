# Like DWI and SM files, CRS files are a variant of the MSD format.

# Course loading is structured differently from step file loading. In
# step files, SongItem is instantiated,creates an instance of a
# specific file class, loads it, and pulls the information it needs
# from it. In Courses, CourseFile is just function that returns an
# object of the appropriate type, which inherits from Course.

# I'm not sure which approach is better.

from constants import *

import random
import util
import error
import records
import os

class Course(object):
  def __init__(self, all_songs, recordkeys):
    self.songs = []
    self.name = "A Course"
    self.mixname = " "
    self.all_songs = all_songs
    self.recordkeys = recordkeys

  def setup(self, screen, player_configs, game_config, gametype):
    self.player_configs = player_configs
    self.game_config = game_config
    self.index = 0
    self.gametype = gametype
    self.screen = screen

  def done(self):
    self.screen = self.player_configs = self.game_config = None

  def _find_difficulty(self, song, diff):
    if self.gametype not in song.difficulty: return False
    elif isinstance(diff, str):
      if diff in song.difficulty[self.gametype]: return diff
      else: return False
    elif isinstance(diff, list):
      possible = []
      for name, rating in song.difficulty[self.gametype].items():
        if rating in diff: possible.append(name)
      if len(possible) > 0: return random.choice(possible)
    return False

  def __iter__(self): return self

  def next(self):
    if self.index == len(self.songs): raise StopIteration
    
    name, diff, mods = self.songs[self.index]
    fullname = None

    a, b = 0, 0
    if diff.find("..") != -1: a, b = map(int, diff.split(".."))
    elif len(diff) < 3: a, b = int(diff), int(diff)
    if a or b: diff = range(a, b + 1)

    if name[0] == "BEST":
      s = self.recordkeys.get(records.best(name[1], diff, self.gametype), None)
      if s: fullname = s.filename
    elif name[0] == "WORST":
      s = self.recordkeys.get(records.worst(name[1], diff, self.gametype), None)
      if s: fullname = s.filename
    elif name[-1] == "*": # A random song
      if "/" in name:
        folder, dummy = name.split("/")
        folder = folder.lower()
        if folder in self.all_songs:
          songs = self.all_songs[folder].values()
        else:
          error.ErrorMessage(self.screen, [folder, "was not found."])
          raise StopIteration

      else:
        songs = []
        for v in self.all_songs.values(): songs.extend(v.values())

      songs = [s for s in songs if self._find_difficulty(s, diff)]

      if len(songs) == 0:
        error.ErrorMessage(self.screen, ["No valid songs were found."])
        raise StopIteration
      else:
        song = random.choice(songs)
        diff = self._find_difficulty(song, diff)
        fullname = song.filename
        
    else:
      for path in mainconfig["songdir"].split(os.pathsep):
        fn = os.path.join(path, name)
        fn = os.path.expanduser(fn)
        if os.path.isfile(fn): fullname = fn
        elif os.path.isdir(fn):
          file_list = util.find(fn, ["*.sm", "*.dwi"])
          if len(file_list) != 0: fullname = file_list[0]
        if fullname: break

    if not fullname and len(name[0]) == 1: # Still haven't found it...
      folder, song = name.split("/")
      song = self.all_songs.get(folder.lower(), {}).get(song.lower())
      if song: fullname = song.filename

    if not fullname:
      if len(name[0]) > 1:
        name = "Player's %s #%d" % (name[0].capitalize(), name[1])
      error.ErrorMessage(self.screen, [name, "was not found."])
      raise StopIteration

    self.index += 1

    return (fullname, [diff] * len(self.player_configs))

def CourseFile(*args):
  if args[0].lower().endswith(".crs"): return CRSFile(*args)
  else: raise RuntimeError(filename + " is an unsupported format.")

class CRSFile(Course):
  # Map modifier names to internal pydance names.
  modifier_map = { "0.5x" : ("speed", 0.5),
                   "0.75x" : ("speed", 0.75),
                   "1.5x" : ("speed", 1.5),
                   "2.0x" : ("speed", 2.0),
                   "3.0x" : ("speed", 3.0),
                   "4.0x" : ("speed", 4.0),
                   "5.0x" : ("speed", 5.0),
                   "8.0x" : ("speed", 8.0),
                   "boost": ("accel", 1),
                   "break": ("accel", 2),
                   "sudden": ("fade", 1),
                   "hidden": ("fade", 2),
                   "cycle": ("fade", 4),
                   "stealth": ("fade", 5),
                   "mirror": ("transform", 1),
                   "left": ("transform", 2),
                   "right": ("transform", 3),
                   "shuffle": ("transform", -1),
                   "random": ("transform", -2),
                   "little": ("size", 2),
                   "reverse": ("scrollstyle", 1),
                   "noholds": ("holds", 0),
                   "dark": ("dark", 1),
                   }

  def __init__(self, filename, all_songs, recordkeys):
    Course.__init__(self, all_songs, recordkeys)
    self.filename = filename
    lines = []
    f = open(filename)
    for line in f:
      if line.find("//") != -1: line = line[:line.find("//")]
      line = line.strip()

      if len(line) == 0: continue
      elif line[0] == "#": lines.append(line[1:]) # A new tag
      else: lines[-1] += line

    for i in range(len(lines)):
      line = lines[i]
      while line[-1] == ";": line = line[:-1] # Some lines have two ;s.
      lines[i] = line.split(":")

    if os.path.split(self.filename)[0][-7:] != "courses":
      self.mixname = os.path.split(os.path.split(self.filename)[0])[1]

    for line in lines:
      if line[0] == "COURSE": self.name = ":".join(line[1:])
      elif line[0] == "SONG":
        if len(line) == 3:
          name, diff = line[1:]
          modifiers = []
        elif len(line) == 4:
          name, diff, modifiers = line[1:]
          modifiers = modifiers.split(",")
        else: continue

        if name[0:4] == "BEST": name = ("BEST", int(name[4:]))
        elif name[0:5] == "WORST": name = ("WORST", int(name[5:]))
        else: name = name.replace("\\", "/") # DWI uses Windows-style

        mods = {}
        for mod in modifiers:
          if mod in CRSFile.modifier_map:
            key, value = CRSFile.modifier_map[mod]
            mods[key] = value
        
        self.songs.append((name, diff, mods))
