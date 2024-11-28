import pygame
import random, time, os
import math


pygame.init()
screen = pygame.display.set_mode((890,500))
clock = pygame.time.Clock()
running = True
game_active = False

pygame.display.set_caption('Word Bomb')
font = pygame.font.SysFont("None",150)
small_font = pygame.font.SysFont("None",70)
lil_font = pygame.font.SysFont("None",50)

heart_surf = pygame.image.load('heart.png').convert_alpha()
heart_surf = pygame.transform.scale(heart_surf,(50,50))
empty_heart_surf = pygame.image.load('empty_heart.png').convert_alpha()
empty_heart_surf = pygame.transform.scale(empty_heart_surf,(50,50))
bomb_surf = pygame.image.load("bomb.png").convert_alpha()
bomb_rect = bomb_surf.get_rect(center = (475,220))

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
    "pl", "fr", "gr", "pr", "bl", "cl", "dr", "fl", "gl", "sp",
    "sl", "sw", "tw", "sk", "sn", "sm", "sc", "wh", "wr", "kn",
    "ed", "ly", "es", "en", "nt", "mp", "nd", "ng", "ld", "lt",
    "pt", "rk", "rt", "rm", "rp", "lk", "ft", "mn", "ph", "gh",
    "ex", "un", "in", "re", "de", "up", "out", "pre", "mis", "sub",
    "bio", "eco", "geo", "aqua", "psy", "pro", "tri", "quad", "uni", "bi",
    "cir", "gen", "tan", "cir", "par", "syn", "hyp", "mic", "mac",
    "tox", "neo", "aer", "dem", "met", "cos", "geo", "aut", "alt", "sup",
    "max", "min", "opt", "via", "act", "lit", "exp", "dev", "sys", "mod"
]

answer = ""
message = ""
lives = 0 
pause = pygame.time.get_ticks()
bomb = False
combination_colour = "white"
pulsing_speed = 0.005

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if not game_active:
      keys = pygame.key.get_pressed()
      if event.type == pygame.MOUSEBUTTONDOWN:
        game_active = True
        game_start = True
        game_played = True
    else:
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
    if lives > 0:
      if bomb is True:
        message = "You ran out of time!"
        answer = ""
        lives -= 1
        rng = random.randint(0,len(combinations)-1)
        x = combinations[rng]
        bomb = False
      if answering:
        answer = answer.strip().lower()

        if x not in answer:
            message = "You didn't include the letters in your word"
            answer = ""
        elif answer in answered_dictionary:
            message = "You have already used this word"
            answer = ""
        elif binary_search(dictionary, answer) == -1:
            message = "Your word is not in the dictionary!"
            answer = ""
        else:
            rng = random.randint(0, len(combinations) - 1)
            x = combinations[rng]
            bomb_time = current_time
            answered_dictionary.append(answer)
            message = ""
            answer = ""

      answering = False

      answering = False
      if current_time - bomb_time > 10000:
        combination_colour = (250,83,65)
        bomb = True
        bomb_time = current_time
      elif current_time - bomb_time >= 7000:
        combination_colour = (250, 83, 65)
        pulsing_speed = 0.015
      elif current_time - bomb_time >= 5000:
        combination_colour = (247, 169, 114)
        pulsing_speed = 0.01
      else: 
        combination_colour = "white"
        pulsing_speed = 0.005

      # Bomb pulsing
      scale_factor = 1 + 0.05 * math.sin(current_time * pulsing_speed)  # Oscillate scale between 0.9 and 1.1
      scaled_bomb_surf = pygame.transform.scale(
          bomb_surf, 
          (int(bomb_rect.width * scale_factor), int(bomb_rect.height * scale_factor))
      )
      scaled_bomb_rect = scaled_bomb_surf.get_rect(center=bomb_rect.center)
      screen.blit(scaled_bomb_surf, scaled_bomb_rect)  # Blit scaled bomb

      # Add the blinking cursor
      cursor_visible = (current_time // 500) % 2 == 0  # Toggle every 500 ms
      if cursor_visible:
        cursor_x = 445 + font.size(answer)[0] // 4 - 5*len(answer)  # Position the cursor after the text
        pygame.draw.line(screen, (0, 0, 0), (cursor_x, 375), (cursor_x, 405), 2)  # Draw cursor as a vertical line

      # Hearts
      for i in range(2):
        heart_x = 450 - (2 * 60 // 2) + i * 60 
        if i < lives:
            screen.blit(heart_surf, (heart_x, 320))  # Full heart
        else:
            screen.blit(empty_heart_surf, (heart_x, 320))  # Empty heart
      # Timer      
      pyprint(str(10-int((current_time - bomb_time)/1000)),(445,50))
      # Combination
      pyprint(f"{x.upper()}",(445,250),combination_colour,small_font)
      # Answer
      pyprint(answer,(445,390))
      # Message
      if current_time - pause < 2000:
        pyprint(message,(445,450))
    else:
      game_active = False


  else:
     lives = 2
     question_answered = False
     answering = False
     boom = False
     answer = ""
     message = ""
     answered_dictionary = []
     bomb_time = pygame.time.get_ticks()
     rng = random.randint(0,len(combinations)-1)
     x = combinations[rng]


     screen.fill((134, 137, 143))
     pyprint("WORD BOMB",(445,220),"white",font)
     pyprint("Click to start",(445,300),"white")
  pygame.display.flip()
  clock.tick(30)

pygame.quit()

