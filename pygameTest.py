import pygame
from gui import *
pygame.init()

screen = pygame.display.set_mode((800, 600))

def get_desaturated_color(colorValue):
  color = pygame.Color(colorValue)
  new_col = pygame.Color((max(0, color.r - 50), max(0, color.g - 50), max(0, color.b - 50)))
  return new_col

left_amount = 0
def set_left_amount(value):
  global left_amount
  left_amount = value


myGUI = GUI(screen, {
  "content_vertical_align": "center",
  "content_horizontal_align": "left"
})

def closeGUI():
  global myGUI
  myGUI.open = False
  myGUI.to_alpha = 0

def create_page(num):
  def create_sample_button(extra_event = lambda: None):
    return GUIButton(
      {
        "width": 100,
        "height": 100,
        "border_radius": 20,
        "border_width": 5,
        "border_color": (0, 0, 55),
        "margin": 15,
        "color": (0, 0, 155),
        "text": "Click Me! " + str(num),
        "font_color": "white"
      },
      [lambda e: e["target"].set_prop("color", (e["target"].base_props["color"])), lambda e: set_left_amount(left_amount + 800), lambda e: extra_event()],
      [lambda e: e["target"].set_prop("color", get_desaturated_color(e["target"].base_props["color"]))],
    )

  innerElem = GUIElement(
    {
      "width": 600,
      "height": 450,
      "margin_left": 100,
      "margin_right": 100,
      "margin_top": 75,
      "margin_bottom": 75,
      "padding": 0,
      "color": "gray",
      "border_radius": 50,
      "border_width": 10,
      "border_color": "red",
      "content_vertical_align": "center",
      "content_horizontal_align": "center",
      "align_direction": "vertical"
    }
  )

  row1 = GUIElement(
    {
      "width": 600,
      "height": 150,
      "color": (255, 255, 255),
      "content_vertical_align": "center",
      "content_horizontal_align": "center",
      "align_direction": "horizontal"
    }
  )
  for i in range(4):
    row1.add_child(create_sample_button())
  innerElem.add_child(row1)

  row2 = GUIElement(
    {
      "width": 600,
      "height": 150,
      "color": (155, 155, 155),
      "content_vertical_align": "center",
      "content_horizontal_align": "left",
      "align_direction": "horizontal"
    }
  )
  
  row2.add_child(create_sample_button(closeGUI))
  innerElem.add_child(row2)

  row3 = GUIElement(
    {
      "width": 600,
      "height": 150,
      "color": (55, 55, 55),
      "content_vertical_align": "center",
      "content_horizontal_align": "center",
      "align_direction": "horizontal"
    }
  )
  for i in range(4):
    row3.add_child(create_sample_button())
  innerElem.add_child(row3)

  myGUI.add_element(innerElem)
  
create_page(1)
create_page(2)
create_page(3)

while True:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      quit()
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
      myGUI.open = not myGUI.open
      myGUI.to_alpha = 255 if myGUI.open else 0
  
  #print(left_amount)
  myGUI.set_prop("padding_left", left_amount)
      
  screen.fill((125, 125, 125))
  
  myGUI.update()
      
  pygame.display.update()
      
    