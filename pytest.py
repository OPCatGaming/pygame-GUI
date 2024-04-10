import pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))

lvl = pygame.Surface((800, 600))
lvl.fill("green")
lvl_pos = [0,0]
plr = pygame.Rect(300, 0, 50, 50)
plr_pos = [300,0]


while True:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      quit()
      
  keys = pygame.key.get_pressed()
  
  if (keys[pygame.K_a]):
    if plr.left > 100:
      plr.x -= 1
    else:
      lvl_pos[0] += 1
    plr_pos[0] -= 1
  if (keys[pygame.K_d]):
    if plr.right < 700:
      plr.x += 1
    else:
      lvl_pos[0] -= 1
    plr_pos[0] += 1
  if (keys[pygame.K_w]):
    if plr.top > 100:
      plr.y -= 1
    else:
      lvl_pos[1] += 1
    plr_pos[1] -= 1
  if (keys[pygame.K_s]):
    if plr.bottom < 700:
      plr.y += 1
    else:
      lvl_pos[1] -= 1
    plr_pos[1] += 1
    
    
  screen.fill("black")
  screen.blit(lvl, lvl_pos)
  pygame.draw.rect(screen, "red", plr)
    
  pygame.display.update()