import pygame
import random, time, os
import math


pygame.init()
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
running = True
game_active = False
game_choosing = False
game_start = True
pygame.display.set_caption('Word Bomb')
font = pygame.font.SysFont("None",150)
small_font = pygame.font.SysFont("None",70)
lil_font = pygame.font.SysFont("None",50)

heart_surf = pygame.image.load('heart.png').convert_alpha()
heart_surf = pygame.transform.scale(heart_surf,(50,50))
empty_heart_surf = pygame.image.load('empty_heart.png').convert_alpha()
empty_heart_surf = pygame.transform.scale(empty_heart_surf,(50,50))
bomb_surf = pygame.image.load("bomb.png").convert_alpha()
bomb_rect = bomb_surf.get_rect(center = ((screen_width//2)+30,((screen_height//2)-30)))
arrow_surf = pygame.image.load("arrow.png").convert_alpha()
arrow_surf = pygame.transform.rotate(arrow_surf, 90)
arrow_surf = pygame.transform.scale(arrow_surf,(200,420))
player_surf = pygame.image.load("player.png").convert_alpha()
player_surf = pygame.transform.scale(player_surf,(100,100))

player_boxes = [
    {"rect": pygame.Rect(260, 100, 370, 250), "label": "1 Player", "players": 1},
    {"rect": pygame.Rect(650, 100, 370, 250), "label": "2 Players", "players": 2},
    {"rect": pygame.Rect(260, 370, 370, 250), "label": "3 Players", "players": 3},
    {"rect": pygame.Rect(650, 370, 370, 250), "label": "4 Players", "players": 4},
]

def pyprint(text,pos,colour = "white",font = lil_font):
  surf = font.render(text,True,colour)
  rect = surf.get_rect(center = (pos))
  screen.blit(surf,rect)
#        pyprint("You guessed the song!",(200,350),"white",lil_font)

def clear():
  os.system("clear")

def blurSurf(surface, amt):
  """
  Blur the given surface by the given 'amount'.  Only values 1 and greater
  are valid.  Value 1 = shown_letters blur.
  """
  if amt < 1.0:
      raise ValueError("Arg 'amt' must be greater than 1.0, passed in value is %s"%amt)
  scale = 1.0/float(amt)
  surf_size = surface.get_size()
  scale_size = (int(surf_size[0]*scale), int(surf_size[1]*scale))
  surf = pygame.transform.smoothscale(surface, scale_size)
  surf = pygame.transform.smoothscale(surf, surf_size)
  return surf


def draw_player_info_ring(players, center, radius):
    visible_players = [p for p in players if not p.get("ai", False)]  # Exclude AI
    num_players = len(visible_players)
    
    if num_players == 0:  # Just in case
        return
    
    angle_step = 2 * math.pi / num_players  # Angle between each player
    for i, player in enumerate(visible_players):
        angle = -math.pi / 2 + i * angle_step
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)

        pyprint(player["name"], (x, y - 20), "white", small_font)
        max_lives = 2
        heart_spacing = 20
        for j in range(max_lives):
            heart_x = x - (max_lives * heart_spacing // 2) + j * heart_spacing - 10
            heart_y = y + 10
            if j < player["lives"]:
                screen.blit(heart_surf, (heart_x, heart_y))
            else:
                screen.blit(empty_heart_surf, (heart_x, heart_y))

def rotate_arrow(arrow_surface, center, current_angle, target_angle, rotation_speed):
    """
    Smoothly rotate the arrow toward the target angle.
    """
    # Calculate the shortest rotational direction (clockwise or counterclockwise)
    angle_diff = (target_angle - current_angle + 360) % 360
    if angle_diff > 180:
        angle_diff -= 360  # Rotate counterclockwise if shorter

    # Incrementally update the current angle based on rotation speed
    if abs(angle_diff) <= rotation_speed:
        current_angle = target_angle  # Snap to target if close enough
    else:
        current_angle += rotation_speed if angle_diff > 0 else -rotation_speed

    # Draw the rotated arrow
    rotated_arrow = pygame.transform.rotate(arrow_surface, -current_angle)
    rotated_rect = rotated_arrow.get_rect(center=center)
    screen.blit(rotated_arrow, rotated_rect)

    return current_angle  # Return the updated angle



def calculate_angle_to_player(current_player, num_players):
    """Calculate the angle the arrow should point to based on the player's position."""
    angle_step = 360 / num_players  # Angle step in degrees
    return current_player * angle_step

with open("dictionary.txt", "r") as f:
    dictionary = sorted(word.strip().lower() for word in f.readlines())


answered_dictionary = []

def binary_search(words, target):
  low = 0
  high = len(words) - 1

  while low <= high:
      mid = (low + high) // 2
      guess = words[mid]

      if guess == target:
          return mid
      if guess < target:
          low = mid + 1
      else:
          high = mid - 1

  return -1  # Target not found

combinations = [
    "an", "ing", "cr", "er", "br", "th", "ch", "st", "tr", "sh",
    "pl", "fr", "gr", "pr", "bl","ts","unc","fr","ek","pb", "cl", "dr", "fl", "gl", "sp",
    "sl", "sw", "tw", "sk", "sn", "sm", "sc", "wh", "wr", "kn",
    "ed", "ly","tr","aa", "es", "en", "nt", "mp", "di", "nd", "ng", "ld", "lt",
    "pt", "rk", "rt", "rm", "rp", "lk", "ft", "mn", "ph", "gh",
    "ex", "un", "in", "re", "de","mi", "up", "out", "pre", "mis", "sub",
    "bio", "eco", "pro", "tri", "quad", "uni", "bi",
    "cir", "gen", "tan", "cir", "par", "syn", "hyp", "mic", "mac",
    "tox", "neo", "aer", "dem", "met", "cos", "aut", "alt", "sup",
    "max", "min", "opt", "via", "act", "lit", "exp", "dev", "sys", "mod"
]


answer = ""
message = ""
answering = False
lives = 0 
pause = pygame.time.get_ticks()
bomb = False
naming = True
combination_colour = "white"
pulsing_speed = 0.005
bomb_time = pygame.time.get_ticks()
bomb_skip = 0

current_arrow_angle = 0  # Initial arrow angle
rotation_speed = 10  # Adjust rotation speed for smoothness (higher = faster)


ring_radius = 250  # Radius of the circle
ring_center = (screen_width // 2, screen_height // 2)  # Center of the ring


players = [{"name": f"Player {i+1}", "lives": 2, "ai" : False} for i in range(3)]  # 3 players
current_player = 0

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if game_choosing:  # Handle player selection screen
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            print(mouse_pos)
            for box in player_boxes:
                if box["rect"].collidepoint(mouse_pos):
                    # Set up players based on the selection
                    if box["players"] == 1:
                        players = [
                            {"name": "Player 1", "lives": 2, "ai": False},
                            {"name": "AI", "lives": 2, "ai": True}
                        ]
                        single_player = True
                    else:
                        players = [{"name": f"Player {i+1}", "lives": 2} for i in range(box["players"])]           
                        single_player = False
                    game_active = True
                    naming = True  # Start naming round
                    current_player = 0
                    game_choosing = False
                    break
    elif game_start:
      keys = pygame.key.get_pressed()
      if event.type == pygame.MOUSEBUTTONDOWN:
        game_choosing = True
        game_start = False
        game_played = True
    elif game_active:
      if event.type == pygame.MOUSEBUTTONDOWN:

        print(f'Mouse clicked at {pygame.mouse.get_pos()}')
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            pause = pygame.time.get_ticks()
            answering = True
        if event.key == pygame.K_BACKSPACE:
            answer = answer[:-1]
        else:
            answer += event.unicode



  if game_active:
    current_time = pygame.time.get_ticks()
    screen.fill((134, 137, 143))
    if len(players) > 1 and not game_start:
      if bomb:
        message = f"{players[current_player]['name']} ran out of time!"
        players[current_player]["lives"] -= 1
        if players[current_player]["lives"] <= 0:
          score = 0 
          eliminated_player = players.pop(current_player)
          message = f"{eliminated_player['name']} has been eliminated!"
          current_player %= len(players)  # Adjust index
        else:
          current_player = (current_player + 1) % len(players)  # Next player's turn

        answer = ""
        rng = random.randint(0,len(combinations)-1)
        x = combinations[rng]
        bomb = False
      
      
      if players[current_player].get("ai", False):  # AI's turn
            bomb_time = current_time  # Reset bomb timer
            current_player = (current_player + 1) % len(players)  # Skip AI instantly

      if answering and not naming:
        answer = answer.strip().lower()
        
        if x not in answer:
          message = "Letters needed!"
        elif answer in answered_dictionary:
          message = "Word already used!"
        elif binary_search(dictionary, answer) == -1:
          message = "Not in dictionary!"
        else:
          answered_dictionary.append(answer)
          rng = random.randint(0, len(combinations) - 1)
          x = combinations[rng]
          message = ""
          bomb_time = current_time - bomb_skip
          bomb_skip += 100
          current_player = (current_player + 1) % len(players)  # Switch turn
          score += 100
        answer = ""
      elif answering and naming:
        answer = answer.strip()
        players[current_player]["name"] = answer
        current_player += 1
        answer = ""
        if current_player >= len(players) or players[current_player].get("ai",False):
          current_player = 0
          naming = False
      answering = False
      
      if current_time - bomb_time > 10000:
        combination_colour = (250,83,65)
        bomb = True
        bomb_time = current_time - bomb_skip
        bomb_skip = 0 
      elif current_time - bomb_time >= 7000:
        combination_colour = (250, 83, 65)
        pulsing_speed = 0.015
      elif current_time - bomb_time >= 5000:
        combination_colour = (247, 169, 114)
        pulsing_speed = 0.01
      else: 
        combination_colour = "white"
        pulsing_speed = 0.005
        
      #angle_to_player = calculate_angle_to_player(current_player, len(players))
      #rotate_arrow(arrow_surf, ring_center, angle_to_player)
      if not players[current_player].get("ai", False):  # Only rotate if it's not AI
        target_angle = calculate_angle_to_player(current_player, len(players))
        current_arrow_angle = rotate_arrow(arrow_surf, ring_center, current_arrow_angle, target_angle, rotation_speed)


    # Smoothly rotate the arrow toward the target angle
     
      # Bomb pulsing
      scale_factor = 1 + 0.05 * math.sin(current_time * pulsing_speed)  # Oscillate scale between 0.9 and 1.1
      scaled_bomb_surf = pygame.transform.scale(
          bomb_surf, 
          (int(bomb_rect.width * scale_factor), int(bomb_rect.height * scale_factor))
      )
      scaled_bomb_rect = scaled_bomb_surf.get_rect(center=bomb_rect.center)
      screen.blit(scaled_bomb_surf, scaled_bomb_rect)  # Blit scaled bomb
      draw_player_info_ring(players, ring_center, ring_radius)
     
      # Add the blinking cursor
      cursor_visible = (current_time // 500) % 2 == 0  # Toggle every 500 ms
      if cursor_visible:
        cursor_x = screen_width//2 + font.size(answer)[0] // 4 - 5*len(answer)  # Position the cursor after the text
        pygame.draw.line(screen, (0, 0, 0), (cursor_x, screen_height//2+85), (cursor_x, screen_height//2+115), 2)  # Draw cursor as a vertical line

      # Hearts
      """
      for i in range(2):
        heart_x = 450 - (2 * 60 // 2) + i * 60 
        if i < lives:
            screen.blit(heart_surf, (heart_x, 320))  # Full heart
        else:
            screen.blit(empty_heart_surf, (heart_x, 320))  # Empty 
      """
      pyprint(f"{players[current_player]['name']}'s Turn", (screen_width, screen_height-50), "white", lil_font)
    
      # Timer      
      #pyprint(str(10-int((current_time - bomb_time)/1000)),(445,50))
      # Combination
      if not naming:
        pyprint(f"{x.upper()}",(screen_width//2,screen_height//2),combination_colour,small_font)
      
      else:
        bomb_time = current_time
        pyprint(f"NAME",(screen_width//2,screen_height//2),"white",lil_font)
      # Answer
      pyprint(answer,(screen_width//2,screen_height//2+100))
      # Message
      if current_time - pause < 2000:
        pyprint(message,(screen_width//2,screen_height-100))
      if single_player:
        pyprint(str(score),(screen_width//2, screen_height-130),"white",small_font)
    else:
      game_start = True
  if game_choosing:
    screen.fill((134, 137, 143))

    # Draw player selection boxes
    for box in player_boxes:
        pygame.draw.rect(screen, (50, 50, 50), box["rect"])  # Draw box background

        num_players = box["players"]
        box_width, box_height = box["rect"].size
        start_x = box["rect"].x
        start_y = box["rect"].y

        if num_players == 1:  # Single player image centered
            player_x = start_x + (box_width - player_surf.get_width()) // 2
            player_y = start_y + (box_height - player_surf.get_height()) // 2
            screen.blit(player_surf, (player_x, player_y))

        elif num_players == 2:  # Two players side by side
            spacing = 20
            total_width = 2 * player_surf.get_width() + spacing
            player_x = start_x + (box_width - total_width) // 2
            player_y = start_y + (box_height - player_surf.get_height()) // 2
            for i in range(2):
                screen.blit(player_surf, (player_x + i * (player_surf.get_width() + spacing), player_y))

        elif num_players == 3:  # Triangle formation
            top_x = start_x + box_width // 2 - player_surf.get_width() // 2
            top_y = start_y + 10
            bottom_x = start_x + (box_width - (2 * player_surf.get_width() + 20)) // 2
            bottom_y = start_y + box_height - player_surf.get_height() - 30

            # Top player
            screen.blit(player_surf, (top_x, top_y))
            # Bottom two players
            for i in range(2):
                screen.blit(player_surf, (bottom_x + i * (player_surf.get_width() + 20), bottom_y))

        elif num_players == 4:  # Square formation
            spacing = 20
            grid_x = start_x + (box_width - (2 * player_surf.get_width() + spacing)) // 2
            grid_y = start_y + (box_height - (2 * player_surf.get_height() + spacing)) // 2

            # Draw 2x2 grid
            for row in range(2):
                for col in range(2):
                    player_x = grid_x + col * (player_surf.get_width() + spacing)
                    player_y = grid_y + row * (player_surf.get_height() + spacing-10)
                    screen.blit(player_surf, (player_x, player_y))

  elif game_start:
     players = [{"name": f"Player {i+1}", "lives": 2,"ai": False} for i in range(5)]
     question_answered = False
     answering = False
     boom = False
     naming = True
     bomb_skip = 0
     score = 0 
     single_player = False
     answer = ""
     message = ""
     answered_dictionary = []
     bomb_time = pygame.time.get_ticks()
     rng = random.randint(0,len(combinations)-1)
     x = combinations[rng]


     screen.fill((134, 137, 143))
     pyprint("WORD BOMB",(screen_width//2,screen_height//2),"white",font)
     pyprint("Click to start",(screen_width//2,(screen_height//2)+100),"white")

  pygame.display.flip()
  clock.tick(60)

pygame.quit()
