from typing import Any
import pygame, math, numpy

class GUIElement:
  def __init__(self, props = {}, extra_defaults = {}) -> None:
    self.props = props
    self.all_defaults = {
      "x": 0,
      "y": 0,
      "position": "relative",
      "top": None,
      "bottom": None,
      "left": None,
      "right": None,
      "width": 0,
      "height": 0,
      "color": "transparent",
      "border_width": 0,
      "border_radius": 0,
      "border_color": 0,
      "border_top_left_radius": props.get("border_radius", 0),
      "border_top_right_radius": props.get("border_radius", 0),
      "border_bottom_left_radius": props.get("border_radius", 0),
      "border_bottom_right_radius": props.get("border_radius", 0),
      "padding": 0,
      "padding_left": props.get("padding", 0),
      "padding_right": props.get("padding", 0),
      "padding_top": props.get("padding", 0),
      "padding_bottom": props.get("padding", 0),
      "margin": 0,
      "margin_left": props.get("margin", 0),
      "margin_right": props.get("margin", 0),
      "margin_top": props.get("margin", 0),
      "margin_bottom": props.get("margin", 0),
      "content_vertical_align": "center",
      "content_horizontal_align": "center",
      "align_direction": "horizontal"
    }
    
    for key, value in extra_defaults.items():
      self.all_defaults[key] = value
      
    self.props = self.evaluate_props(props)
    self.base_props = self.props.copy()
      
    self.rect = pygame.Rect(self.prop("x"), self.prop("y"), self.prop("width"), self.prop("height"))
    self.pressed_down_callbacks = []
    self.pressed_up_callbacks = []
    self.pressed_callbacks = []
    self.pressed = False
    self.children = []
    self.parent = None
    
  def prop(self, name):
    return self.props[name]
  
  def base_prop(self, name):
    return self.base_props[name]
  
  def set_prop(self, name, value):
    self.props[name] = value
    
  def set_attribute(self, name, value):
    self.__setattr__(name, value)
    
  def set_rect_attribute(self, name, value):
    self.rect.__setattr__(name, value)
    self.snap_children_to_parent()
    
  def add_child(self, child):
    self.children.append(child)
    child.parent = self
  
  def draw(self, screen, gui):
    if (self.prop("color") != "transparent"):
      pygame.draw.rect(screen, self.prop("color"), self.rect, 0, self.prop("border_radius"), self.prop("border_top_left_radius"), self.prop("border_top_right_radius"), self.prop("border_bottom_left_radius"), self.prop("border_bottom_right_radius"))
    if (self.prop("border_color") != "transparent" and self.prop("border_width") != 0):
      pygame.draw.rect(screen, self.prop("border_color"), self.rect, self.prop("border_width"), self.prop("border_radius"), self.prop("border_top_left_radius"), self.prop("border_top_right_radius"), self.prop("border_bottom_left_radius"), self.prop("border_bottom_right_radius"))
    
    self.__play_mouse_events(gui)
    draw_list = self.children.copy()
    
    for item in draw_list:
      item.draw(screen, gui)
      
  def snap_children_to_parent(self):
    # Finding full width and height of children with relative positioning
    children_width = 0
    children_height = 0
    for child in self.children:
      if (child.prop("position") == "absolute"):
        continue
      
      children_width += child.prop("width") + child.prop("margin_left") + child.prop("margin_right")
      children_height += child.prop("height") + child.prop("margin_top") + child.prop("margin_bottom")
    
    # Vars used in aligning
    rect_with_padding = pygame.Rect(self.rect.x + self.prop("padding_left"), self.rect.y + self.prop("padding_top"), self.rect.width - (self.prop("padding_left") + self.prop("padding_right")), self.rect.height - (self.prop("padding_top") + self.prop("padding_bottom")))
    space_sides_x = (rect_with_padding.width - children_width)
    space_sides_y = (rect_with_padding.height - children_height)
    vert_align = self.prop("content_vertical_align")
    horiz_align = self.prop("content_horizontal_align")
    row_width = 0
    col_height = 0
    
    def do_horizontal_align(elem: GUIElement, side_space: tuple, row_width_before, ignore_vert = False):
      horiz_options = {
        "center": ("left", rect_with_padding.left + side_space[0] / 2 + row_width_before + elem.prop("margin_left")),
        "left": ("left", rect_with_padding.left + row_width_before + elem.prop("margin_left")), 
        "right": ("left", rect_with_padding.left + side_space[0] + row_width_before + elem.prop("margin_left"))
      }
      if (horiz_align in horiz_options.keys()):
        option = horiz_options[horiz_align]
        elem.set_rect_attribute(option[0], option[1])
        
      if (ignore_vert):
        return
      
      vert_options = {
        "center": ("centery", rect_with_padding.centery),
        "top": ("top", rect_with_padding.top), 
        "bottom": ("bottom", rect_with_padding.bottom)
      }
      if (vert_align in vert_options.keys()):
        option = vert_options[vert_align]
        elem.set_rect_attribute(option[0], option[1])
        
    def do_vertical_align(elem: GUIElement, side_space: tuple, col_height_before, ignore_horiz = False):
      vert_options = {
        "center": ("top", rect_with_padding.top + side_space[1] / 2 + col_height_before + elem.prop("margin_top")),
        "top": ("top", rect_with_padding.top + col_height_before + elem.prop("margin_top")), 
        "bottom": ("top", rect_with_padding.top + side_space[1] + col_height_before + elem.prop("margin_top"))
      }
      if (vert_align in vert_options.keys()):
        option = vert_options[vert_align]
        elem.set_rect_attribute(option[0], option[1])
        
      if (ignore_horiz):
        return
        
      horiz_options = {
        "center": ("centerx", rect_with_padding.centerx),
        "left": ("left", rect_with_padding.left), 
        "right": ("right", rect_with_padding.right)
      }
      if (horiz_align in horiz_options.keys()):
        option = horiz_options[horiz_align]
        elem.set_rect_attribute(option[0], option[1])
    
    for i, child in enumerate(self.children):
      # For elements with absolute positioning
      has_positioning_prop_v = False
      has_positioning_prop_h = False
      if (child.prop("position") == "absolute"):
        
        if (child.prop("top") != None):
          has_positioning_prop_v = True
          child.rect.top = rect_with_padding.top + child.prop("top")
        elif (child.prop("bottom") != None):
          has_positioning_prop_v = True
          child.rect.bottom = rect_with_padding.bottom - child.prop("bottom")
        
        if (child.prop("left") != None):
          has_positioning_prop_h = True
          child.rect.left = rect_with_padding.left + child.prop("left")
        elif (child.prop("right") != None):
          has_positioning_prop_h = True
          child.rect.right = rect_with_padding.right - child.prop("right")
            
        space_sides_x = (rect_with_padding.width - child.rect.width + child.prop("margin_left") + child.prop("margin_right"))
        space_sides_y = (rect_with_padding.height - child.rect.height + child.prop("margin_top") + child.prop("margin_bottom"))
        if (not has_positioning_prop_h):
          do_horizontal_align(child, (space_sides_x, space_sides_y), 0, True)
        if (not has_positioning_prop_v):
          do_vertical_align(child, (space_sides_x, space_sides_y), 0, True)
        
      if (has_positioning_prop_v or has_positioning_prop_h):
          continue
      
      # For elements with relative positioning
      if (self.prop("align_direction") == "horizontal"):
        do_horizontal_align(child, (space_sides_x, space_sides_y), row_width)
      
      if (self.prop("align_direction") == "vertical"):
        do_vertical_align(child, (space_sides_x, space_sides_y), col_height)
      
      row_width += child.rect.width + child.prop("margin_left") + child.prop("margin_right")
      col_height += child.rect.height + child.prop("margin_top") + child.prop("margin_bottom")
        
  def evaluate_props(self, props):
    props_keys = props.keys()
    final_props = {}
    for key in self.all_defaults.keys():
      default = self.all_defaults[key]
      final_props[key] = props[key] if key in props_keys else default
      
    return final_props

  def is_mouse_over(self):
    mouse = pygame.mouse.get_pos()
    return self.rect.collidepoint(mouse)
  
  def __play_pressed_down_callback(self):
    for callback in self.pressed_down_callbacks:
      callback({"event": "mousedown", "target": self, "position": pygame.mouse.get_pos()})
  def __play_pressed_up_callback(self):
    for callback in self.pressed_up_callbacks:
      callback({"event": "mouseup", "target": self, "position": pygame.mouse.get_pos()})
  def __play_pressed_callback(self):
    for callback in self.pressed_callbacks:
      callback({"event": "mousepressed", "target": self, "position": pygame.mouse.get_pos()})
  def __play_mouse_events(self, gui):
    if (self.is_mouse_over()):
      if (gui.mouse_pressed):
        self.__play_pressed_callback()
        self.pressed = True
      if (gui.mouse_just_pressed):
        self.__play_pressed_down_callback()
    if (gui.mouse_just_released and self.pressed):
      self.__play_pressed_up_callback()
      self.pressed = False
          
  def copy(self):
    copied = GUIElement(self.props)
    copied.rect = self.rect
    copied.pressed_down_callbacks = self.pressed_down_callbacks
    copied.pressed_up_callbacks = self.pressed_up_callbacks
    copied.pressed_callbacks = self.pressed_callbacks
    copied.children = self.children
    copied.parent = self.parent
    return copied
  
class GUIText(GUIElement):
  
  def __init__(self, props = {}) -> None:
    extra_defaults = {
      "width": props.get("width", props.get("font", pygame.font.SysFont("Arial", 20)).size(props.get("text", ""))[0]),
      "height": props.get("height", props.get("font", pygame.font.SysFont("Arial", 20)).size(props.get("text", ""))[1]),
      "text": "",
      "font": pygame.font.SysFont("Arial", 20),
      "font_color": "black",
    }
    super().__init__(props, extra_defaults)

  def draw(self, screen, gui):
    super().draw(screen, gui)
    
    text = self.prop("font").render(self.prop("text"), True, self.prop("font_color"))
    screen.blit(text, (self.rect.x, self.rect.y))
    
  def copy(self):
    copied = GUIText(self.props)
    copied.rect = self.rect
    copied.pressed_down_callbacks = self.pressed_down_callbacks
    copied.pressed_up_callbacks = self.pressed_up_callbacks
    copied.pressed_callbacks = self.pressed_callbacks
    copied.children = self.children
    copied.parent = self.parent
    return copied

class GUIButton(GUIElement):
  def __init__(self, props = {}, clicked_callbacks = [], mousedown_callbacks = [], pressed_callbacks = []) -> None:
    extra_defaults = {
      "text": "",
      "font": pygame.font.SysFont("Arial", 20),
      "font_color": "black",
    }
    
    super().__init__(props, extra_defaults)
    
    self.pressed_down_callbacks = mousedown_callbacks
    self.pressed_up_callbacks = clicked_callbacks
    self.pressed_callbacks = pressed_callbacks
    
    self.add_child(GUIText({"x": self.prop("x"), "y": self.prop("y"), "text": self.prop("text"), "font_color": self.prop("font_color"), "font": self.prop("font")}))
  
  def draw(self, screen, gui):
    super().draw(screen, gui)
  
  def copy(self):
    copied = GUIButton(self.props, self.pressed_up_callbacks, self.pressed_down_callbacks, self.pressed_callbacks)
    copied.rect = self.rect
    copied.pressed_down_callbacks = self.pressed_down_callbacks
    copied.pressed_up_callbacks = self.pressed_up_callbacks
    copied.pressed_callbacks = self.pressed_callbacks
    copied.children = self.children
    copied.parent = self.parent
    return copied

class GUI:
  def __init__(self, screen, props={}) -> None:
    self.all_defaults = {
      "color": "transparent",
      "padding": 0,
      "padding_left": props.get("padding", 0),
      "padding_right": props.get("padding", 0),
      "padding_top": props.get("padding", 0),
      "padding_bottom": props.get("padding", 0),
      "content_vertical_align": "center",
      "content_horizontal_align": "center",
      "align_direction": "horizontal",
    }
    self.props = self.evaluate_props(props)
    self.screen = screen
    self.elements = []
    self.open = True
    self.__pressed = False
    self.mouse_pressed = False
    self.mouse_just_pressed = False
    self.mouse_just_released = False
    self.display = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    self.display.fill((0,0,0,0))
    self.to_alpha = 255
    self.current_alpha = 255
    
  def add_element(self, element: GUIElement):
    self.elements.append(element)
    
    width, height = self.display.get_size()
    x = 0
    y = 0
    
    # Finding full width and height of children with relative positioning
    children_width = 0
    children_height = 0
    for child in self.elements:
      if (child.prop("position") == "absolute"):
        continue
      
      children_width += child.prop("width") + child.prop("margin_left") + child.prop("margin_right")
      children_height += child.prop("height") + child.prop("margin_top") + child.prop("margin_bottom")
    
    # Vars used in aligning
    rect_with_padding = pygame.Rect(x + self.prop("padding_left"), y + self.prop("padding_top"), width - (self.prop("padding_left") + self.prop("padding_right")), height - (self.prop("padding_top") + self.prop("padding_bottom")))
    space_sides_x = (rect_with_padding.width - children_width)
    space_sides_y = (rect_with_padding.height - children_height)
    vert_align = self.prop("content_vertical_align")
    horiz_align = self.prop("content_horizontal_align")
    row_width = 0
    col_height = 0
    
    def do_horizontal_align(elem: GUIElement, side_space: tuple, row_width_before, ignore_vert = False):
      horiz_options = {
        "center": ("left", rect_with_padding.left + side_space[0] / 2 + row_width_before + elem.prop("margin_left")),
        "left": ("left", rect_with_padding.left + row_width_before + elem.prop("margin_left")), 
        "right": ("left", rect_with_padding.left + side_space[0] + row_width_before + elem.prop("margin_left"))
      }
      if (horiz_align in horiz_options.keys()):
        option = horiz_options[horiz_align]
        elem.set_rect_attribute(option[0], option[1])
        
      if (ignore_vert):
        return
      
      vert_options = {
        "center": ("centery", rect_with_padding.centery),
        "top": ("top", rect_with_padding.top), 
        "bottom": ("bottom", rect_with_padding.bottom)
      }
      if (vert_align in vert_options.keys()):
        option = vert_options[vert_align]
        elem.set_rect_attribute(option[0], option[1])
        
    def do_vertical_align(elem: GUIElement, side_space: tuple, col_height_before, ignore_horiz = False):
      vert_options = {
        "center": ("top", rect_with_padding.top + side_space[1] / 2 + col_height_before + elem.prop("margin_top")),
        "top": ("top", rect_with_padding.top + col_height_before + elem.prop("margin_top")), 
        "bottom": ("top", rect_with_padding.top + side_space[1] + col_height_before + elem.prop("margin_top"))
      }
      if (vert_align in vert_options.keys()):
        option = vert_options[vert_align]
        elem.set_rect_attribute(option[0], option[1])
        
      if (ignore_horiz):
        return
        
      horiz_options = {
        "center": ("centerx", rect_with_padding.centerx),
        "left": ("left", rect_with_padding.left), 
        "right": ("right", rect_with_padding.right)
      }
      if (horiz_align in horiz_options.keys()):
        option = horiz_options[horiz_align]
        elem.set_rect_attribute(option[0], option[1])
    
    for i, child in enumerate(self.elements):
      # For elements with absolute positioning
      has_positioning_prop_v = False
      has_positioning_prop_h = False
      if (child.prop("position") == "absolute"):
        
        if (child.prop("top") != None):
          has_positioning_prop_v = True
          child.rect.top = rect_with_padding.top + child.prop("top")
        elif (child.prop("bottom") != None):
          has_positioning_prop_v = True
          child.rect.bottom = rect_with_padding.bottom - child.prop("bottom")
        
        if (child.prop("left") != None):
          has_positioning_prop_h = True
          child.rect.left = rect_with_padding.left + child.prop("left")
        elif (child.prop("right") != None):
          has_positioning_prop_h = True
          child.rect.right = rect_with_padding.right - child.prop("right")
            
        space_sides_x = (rect_with_padding.width - child.rect.width + child.prop("margin_left") + child.prop("margin_right"))
        space_sides_y = (rect_with_padding.height - child.rect.height + child.prop("margin_top") + child.prop("margin_bottom"))
        if (not has_positioning_prop_h):
          do_horizontal_align(child, (space_sides_x, space_sides_y), 0, True)
        if (not has_positioning_prop_v):
          do_vertical_align(child, (space_sides_x, space_sides_y), 0, True)
        
      if (has_positioning_prop_v or has_positioning_prop_h):
          continue
      
      # For elements with relative positioning
      if (self.prop("align_direction") == "horizontal"):
        do_horizontal_align(child, (space_sides_x, space_sides_y), row_width)
      
      if (self.prop("align_direction") == "vertical"):
        do_vertical_align(child, (space_sides_x, space_sides_y), col_height)
      
      row_width += child.rect.width + child.prop("margin_left") + child.prop("margin_right")
      col_height += child.rect.height + child.prop("margin_top") + child.prop("margin_bottom")
        
  def evaluate_props(self, props):
    props_keys = props.keys()
    final_props = {}
    for key in self.all_defaults.keys():
      default = self.all_defaults[key]
      final_props[key] = props[key] if key in props_keys else default
      
    return final_props
  
  def prop(self, name):
    return self.props[name]
  
  def set_prop(self, name, value):
    self.props[name] = value
    
  def set_attribute(self, name, value):
    self.__setattr__(name, value)
    
  def __get_mouse_events(self):
    mouse_pressed = pygame.mouse.get_pressed()[0]
    mouse_just_pressed = False
    mouse_just_released = False
    if (mouse_pressed):
      if (not self.__pressed):
        mouse_just_pressed = True
      self.__pressed = True
    else:
      if (self.__pressed):
        mouse_just_released = True
      self.__pressed = False
    
    self.mouse_pressed = mouse_pressed
    self.mouse_just_pressed = mouse_just_pressed
    self.mouse_just_released = mouse_just_released
 
  def update(self):
    if (self.prop("color") != "transparent"):
      self.screen.fill(self.prop("color"))
      
    if (self.open):
      self.__get_mouse_events()
      
    for element in self.elements:
      element.draw(self.display, self)
        
    # Alpha & transparency stuff
    if (self.current_alpha != self.to_alpha):
      if (abs(self.current_alpha - self.to_alpha) <= 8):
        self.current_alpha = self.to_alpha
      else:
        self.current_alpha += math.copysign(1, self.to_alpha - self.current_alpha) * 8
    new_display = self.display.copy()
    new_display.set_alpha(self.current_alpha)
    
    self.screen.blit(new_display, (0, 0))
    