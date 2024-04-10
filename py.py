import pygame
from gui import *
pygame.init()

screen = pygame.display.set_mode((800, 600))

button_props = {
  "border_radius": 10
}

myGUI = GUI(screen)


myGUI.add_element(GUIButton(
  {
    "width": 100, 
    "height": 100, 
    "color": "red", 
    "text": "Click Me!", 
    "border_radius": 10, 
    "border_width": 500, 
    "border_color": "black", 
    "font_color": "black", 
    "font": "Arial", 
    "content-horizontal-align": "center", 
    "content-vertical-align": "center"
  },
  lambda e: e["target"].set_prop("color", "red"),
  lambda e: e["target"].set_prop("color", "green"),
  lambda e: pygame.draw.circle(screen, "black", e["position"], 5)
))
myGUI.add_element(GUIButton(
  {
    "width": 100, 
    "height": 100, 
    "color": "red", 
    "text": "Click Me!", 
    "border_radius": 10, 
    "border_width": 500, 
    "border_color": "black", 
    "font_color": "black", 
    "font": "Arial", 
    "content-horizontal-align": "center", 
    "content-vertical-align": "center"
  },
  lambda e: e["target"].set_prop("color", "red"),
  lambda e: e["target"].set_prop("color", "green"),
  lambda e: pygame.draw.circle(screen, "black", e["position"], 5)
))