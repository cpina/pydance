# ceci n'est pas une \'{e}cran d'option

import copy
from constants import *
import pygame
import colors

class OptionScreen:

  menu = [
    ("Speed", "speed", [(0.25, ".25x"), (0.5, ".5x"), (1, "1x"), (2, "2x"),
                        (3, "3x"), (4, "4x"), (8, "8x")]),
    ("Sudden", "sudden", [(0, "Off"), (1, "Hide 1"), (2, "Hide 2"),
                          (3, "Hide 3")]),
    ("Hidden", "hidden", [(0, "Off"), (1, "Hide 1"), (2, "Hide 2"),
                          (3, "Hide 3")]),
    ("Size", "scale", [(1, "Normal"), (0, "Shrink"), (2, "Grow")]),
    ("Little", "little", [(0, "Off"), (1, "No 16ths"), (3, "No 16ths/8ths")]),
    ("Scroll", "scrollstyle", [(0, "Normal"), (1, "Reverse"), (2, "Center")]),
    ("Spin", "spin", [(0, "Off"), (1, "On")]),
    ("Flat", "colortype", [(4, "Off"), (1, "On")]),
    ("Dark", "toparrows", [(1, "Off"), (0, "On")]),
    ("Jumps", "jumps", [(1, "On"), (0, "Off")]),
    ]

  player_colors = [colors.color["cyan"], colors.color["yellow"]]

  bg = pygame.image.load(os.path.join(pyddr_path, "images", "option-bg.png"))
  bg.set_colorkey(bg.get_at((0, 0)))
  bg.set_alpha(200)

  # Players is a list of hashes, not Player objects; it should have all
  # config information set to some value already (player_config in constants)
  def __init__(self, players, title = "Players"):
    self.players = players
    self.current = [0] * len(players)
    self.title = title + ": Options"

  def display(self, screen):
    baseimage = pygame.transform.scale(screen, (640,480))

    # Animate the menu opening
    if mainconfig['gratuitous']:
      t = pygame.time.get_ticks()
      eyecandyimage = pygame.surface.Surface((640, 480))
      while pygame.time.get_ticks() - t < 300:
        p = float(pygame.time.get_ticks() - t) / 300
        eyecandyimage.blit(baseimage, (0,0))
        scaledbg = pygame.transform.scale(OptionScreen.bg,(int(580 * p), 480))
        scaledbg.set_alpha(200)
        r = scaledbg.get_rect()
        r.center = (320, 240)
        up = eyecandyimage.blit(scaledbg, r)
        screen.blit(eyecandyimage, (0, 0))
        pygame.display.update(up)
    
    baseimage.blit(OptionScreen.bg, (30, 0))

    self.baseimage = baseimage
    
    screen.blit(baseimage, (0, 0))
    pygame.display.update()
    
    ev = E_PASS
    
    while not (ev == E_START or ev == E_QUIT):
      self.render(screen)
      
      pid, ev = event.wait()
      if pid >= len(self.players): pass
      
      elif ev == E_DOWN:
        self.current[pid] = (self.current[pid] + 1) % len(OptionScreen.menu)
        
      elif ev == E_UP:
        self.current[pid] = (self.current[pid] - 1) % len(OptionScreen.menu)
        
      elif ev == E_LEFT:
        optname = OptionScreen.menu[self.current[pid]][1]
        cur_val = self.players[pid][optname]
        values = copy.copy(OptionScreen.menu[self.current[pid]][2])
        values.reverse()
        
        next = False
        for val in values:
          if next:
            self.players[pid][optname] = val[0]
            break
          elif self.players[pid][optname] == val[0]: next = True

      elif ev == E_RIGHT:
        optname = OptionScreen.menu[self.current[pid]][1]
        cur_val = self.players[pid][optname]
        values = OptionScreen.menu[self.current[pid]][2]
      
        next = False
        for val in values:
          if next:
            self.players[pid][optname] = val[0]
            break
          elif self.players[pid][optname] == val[0]: next = True

    return (ev == E_START)

  def render(self, screen):
    rect = ((45, 5), (570, 470))
    blankimage = pygame.surface.Surface(rect[1])
    blankimage.set_colorkey(blankimage.get_at((0,0)))

    for i in range(len(OptionScreen.menu)):
      color = None
      for j in range(len(self.current)):
        if i == self.current[j]:
          if not color: color = OptionScreen.player_colors[j]
          else: color = colors.average(color, OptionScreen.player_colors[j])
      if not color: color = colors.WHITE

      item = OptionScreen.menu[i]
      name, opt, values = item
      text = FONTS[32].render(name, 1, color)
      blankimage.blit(text, (10, 70 + 35 * i))
      width = 480 / (len(values) + 1)
      for k in range(len(values)):
        color = None
        for plr in range(len(self.players)):
          if values[k][0] == self.players[plr][opt]:
            newcolor = OptionScreen.player_colors[plr]
            if not color: color = newcolor
            else: color = colors.average(color, newcolor)
        if not color: color = colors.WHITE

        text = FONTS[32].render(values[k][1], 1, color)
        blankimage.blit(text, (100 + width * k, 70 + 35 * i))

    faketext = " / ".join([str(i+1) for i in range(len(self.current))])
    faketext = "Players: " + faketext
    textimage = pygame.surface.Surface(FONTS[16].size(faketext))
    textimage.set_colorkey(textimage.get_at((0, 0)))
    text = FONTS[16].render("Players: ", 1, colors.WHITE)
    textimage.blit(text, (0, 0))
    xpos = text.get_width()
    for i in range(len(self.current)):
      text = FONTS[16].render(str(i+1), 1, OptionScreen.player_colors[i])
      textimage.blit(text, (xpos, 0))
      xpos += text.get_width()
      if i != len(self.current) - 1:
        text = FONTS[16].render(" / ", 1, colors.WHITE)
        textimage.blit(text, (xpos, 0))
        xpos += text.get_width()

    r = textimage.get_rect()
    r.center = (blankimage.get_rect().centerx, 450)
    blankimage.blit(textimage, r)

    screen.blit(self.baseimage, (0, 0))
    screen.blit(blankimage, rect)
    pygame.display.update()
