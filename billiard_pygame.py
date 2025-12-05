import pygame
import sys
import json

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 25  # 25x25 grid
CELL_SIZE = 35
LABEL_MARGIN = 30  # Space for labels
TITLE_MARGIN = 40  # Space for title at top
MENU_WIDTH = 200
GRID_WIDTH = GRID_SIZE * CELL_SIZE + LABEL_MARGIN 
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE + MENU_WIDTH
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + LABEL_MARGIN + TITLE_MARGIN

# Color options
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 150, 255)
GREEN = (100, 255, 150)
RED = (255, 100, 100)
YELLOW = (255, 255, 100)
ORANGE = (255, 165, 100)
PURPLE = (200, 100, 255)
CYAN = (100, 255, 255)
PINK = (255, 150, 200)

# create display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Billiard Ball Simulator")

# Grid data
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# data structures for balls, mirrors, and outputs
balls = []
mirrors = []
outputs = []

# Mirror properties
class Mirror:
    def __init__(self,grid_row, grid_col, orientation ='/'):
        self.grid_row = grid_row
        self.grid_col = grid_col
        self.orientation = orientation 
    def draw(self,surface):
        x = self.grid_col * CELL_SIZE + LABEL_MARGIN
        y = self.grid_row * CELL_SIZE + LABEL_MARGIN + TITLE_MARGIN
        
        if self.orientation == '/':
            start = (x, y + CELL_SIZE)
            end = (x + CELL_SIZE, y)
        else:
            start = (x,y)
            end = (x + CELL_SIZE, y + CELL_SIZE)
            
        pygame.draw.line(surface, BLACK, start, end, 4)
    def reflect(self, dx, dy):
        if self.orientation == '/':
            return -dy, -dx
        else:
            return dy, dx
    
    def to_dict(self):
        return {
            'row': self.grid_row,
            'col': self.grid_col,
            'orientation': self.orientation
        }
            
# Output Block properties

class Output:
    def __init__(self, grid_row, grid_col):
        self.grid_row = grid_row
        self.grid_col = grid_col
        
    def draw(self,surface):
        x = self.grid_col * CELL_SIZE + LABEL_MARGIN
        y = self.grid_row * CELL_SIZE + LABEL_MARGIN + TITLE_MARGIN
        pygame.draw.rect(surface,CYAN,(x,y,CELL_SIZE,CELL_SIZE))
        
    def to_dict(self):
        return {
            'row' : self.grid_row,
            'col' : self.grid_col
        }
        
# Ball properties
class Ball:
    def __init__(self, grid_row, grid_col, dx,dy, color):
        self.grid_row = grid_row
        self.grid_col = grid_col
        self.initial_row = grid_row
        self.initial_col = grid_col
        self.color = color
        # Actual pixel position (centered in cell)
        self.x = (grid_col * CELL_SIZE + CELL_SIZE // 2) + LABEL_MARGIN
        self.y = (grid_row * CELL_SIZE + CELL_SIZE // 2) + LABEL_MARGIN + TITLE_MARGIN
        self.initial_dx = dx
        self.intial_dy = dy
        self.dx = dx
        self.dy = dy
        self.radius = CELL_SIZE // 3
        self.speed = 3  # pixels per frame
        self.stop_tick = 0
        self.reached_output = False
        self.leave_output = False
        self.output = None
        self.left_input = False
        self.leave_input = False
        self.moving = False
        
    def to_dict(self):
        return {
            'row'  : self.initial_row,
            'col'  : self.initial_col,
            'dx'   : self.initial_dx,
            'dy'   : self.intial_dy,
            'color': self.color
        }
        
    # update the ball position
    def update(self):
        if self.moving:
            
            target_col = self.grid_col + self.dx
            target_row = self.grid_row + self.dy
           
            # Calculate target pixel position (center of target cell)
            target_x = target_col * CELL_SIZE + CELL_SIZE // 2 + LABEL_MARGIN
            target_y = target_row * CELL_SIZE + CELL_SIZE // 2 + LABEL_MARGIN + TITLE_MARGIN
            
            # Calculate direction
            dx = target_x - self.x
            dy = target_y - self.y
            distance = (dx**2 + dy**2)**0.5
            
            # If close enough, snap to target
            if distance < self.speed:
                self.x = target_x
                self.y = target_y
                self.grid_row = target_row
                self.grid_col = target_col
                
                # check if there is a mirror in this space and reflect
                hit_mirror = None
                for mirror in mirrors:
                    if mirror.grid_col == self.grid_col and mirror.grid_row == self.grid_row:
                        hit_mirror = mirror
                        break
                if hit_mirror:
                    self.dx, self.dy = hit_mirror.reflect(self.dx, self.dy)
                    return
                    
                # handle ball collision on corners as well
                for ball in balls:
                    col_diff = ball.grid_col - self.grid_col
                    row_diff = ball.grid_row - self.grid_row
                    
                    # check if they are diagonally adjacent to each other
                    if abs(col_diff) == 1 and abs(row_diff) == 1:
                        
                        # check if they will collide in the same place to make sure a collision is necessary
                        self_next_col = self.grid_col + self.dx
                        self_next_row = self.grid_row + self.dy
                        ball_next_col = ball.grid_col + ball.dx
                        ball_next_row = ball.grid_row + ball.dy
                        
                        
                        if self_next_col == ball_next_col and self_next_row == ball_next_row:
                            
                            # set mirror type depending on collision
                            
                            # reflection for upper right and lower left
                            if col_diff == row_diff:
                                mirror_type = '/'
                                
                            # reflection for lower right and upper left
                            else:
                                mirror_type = '\\'
                                
                            # set new speeds after collision                         
                            ball.dx, ball.dy = ball_collision(mirror_type,ball.dx,ball.dy)
                            self.dx, self.dy = ball_collision(mirror_type,self.dx,self.dy)                               
            else:
                # Move towards target
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                
    def reset(self):
        self.x = (self.grid_col * CELL_SIZE + CELL_SIZE // 2) + LABEL_MARGIN
        self.y = (self.grid_row * CELL_SIZE + CELL_SIZE // 2) + LABEL_MARGIN + TITLE_MARGIN
        self.grid_row = self.initial_row
        self.grid_col = self.initial_col
        self.dx = self.initial_dx
        self.dy = self.intial_dy
        self.moving = False
        self.reached_output = False
        self.leave_output = False
        self.left_input = False
        self.leave_input = False
        self.stop_tick = 0
        
    
    # draw the art for the balls and a box around their original position to keep track of the input square
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw a white highlight
        pygame.draw.circle(surface, WHITE, 
                         (int(self.x - self.radius//3), int(self.y - self.radius//3)), 
                         self.radius//4)
        
        x = self.initial_col * CELL_SIZE + LABEL_MARGIN
        y = self.initial_row * CELL_SIZE + LABEL_MARGIN + TITLE_MARGIN
        pygame.draw.rect(surface,self.color,(x,y,CELL_SIZE,CELL_SIZE),3)
        

class MenuButton:
    def __init__(self,x,y,width,height,label,type,data=None):
        self.rect = pygame.Rect(x,y,width,height)
        self.label = label
        self.type = type
        self.selected = False
        self.data = data
    def draw(self, surface):
        color = BLUE
        if self.selected:
            color = WHITE
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect,2)
        
        font = pygame.font.Font(None,20)
        label = font.render(self.label,True,BLACK)
        label_pos = label.get_rect(center=self.rect.center)
        surface.blit(label, label_pos)
    
    def on_click(self,pos):
        return self.rect.collidepoint(pos)
        

# function for ball collsion
def ball_collision(orientation,dx,dy):
    if orientation == '/':
        return -dy, -dx
    else:
        return dy, dx
  
# function to reverse the direction of the ball  
def ball_reverse(dx,dy):
    return -dx, -dy

# function to draw grid
def draw_grid():
    for x in range(0, GRID_SIZE + 1):
        x_pos = x * CELL_SIZE + LABEL_MARGIN
        pygame.draw.line(screen, GRAY, (x_pos, LABEL_MARGIN + TITLE_MARGIN), (x_pos, WINDOW_HEIGHT))
    for y in range(0, GRID_SIZE + 1):
        y_pos = y * CELL_SIZE + LABEL_MARGIN + TITLE_MARGIN
        pygame.draw.line(screen, GRAY, (LABEL_MARGIN, y_pos), (GRID_WIDTH, y_pos))

# function to draw grid labels
def draw_labels():
    font = pygame.font.Font(None, 20)
    
    # Draw column labels (top)
    for col in range(GRID_SIZE):
        label = font.render(str(col), True, BLACK)
        x = col * CELL_SIZE + CELL_SIZE // 2 + LABEL_MARGIN
        y = LABEL_MARGIN // 2 + TITLE_MARGIN
        text_rect = label.get_rect(center=(x, y))
        screen.blit(label, text_rect)
    
    # Draw row labels (left)
    for row in range(GRID_SIZE):
        label = font.render(str(row), True, BLACK)
        x = LABEL_MARGIN // 2
        y = row * CELL_SIZE + CELL_SIZE // 2 + LABEL_MARGIN + TITLE_MARGIN
        text_rect = label.get_rect(center=(x, y))
        screen.blit(label, text_rect)
        
def save_model(mirrors, balls, outputs,filename="model.json"):

    configuration_dict = {
        'mirrors' : [m.to_dict() for m in mirrors],
        'balls' : [b.to_dict() for b in balls],
        'outputs' : [o.to_dict() for o in outputs]
    }
    
    with open(filename, 'w') as fd:
        json.dump(configuration_dict,fd,indent=2)
        
    print(f'Saved model to {filename}')

def load_model(filename):
    try:
        with open(filename, 'r') as fd:
            configuration = json.load(fd)
        mirrors = [Mirror(m['row'], m['col'], m['orientation']) for m in configuration['mirrors']] 
        balls = [Ball(b['row'], b['col'], b['dx'], b['dy'], b['color']) for b in configuration['balls']] 
        outputs = [Output(o['row'],o['col']) for o in configuration['outputs']] 
        
        return mirrors, balls, outputs
    except FileNotFoundError:
        print(f'{filename} not found')
        return [],[],[]
    
def main():
   
    global balls, mirrors, outputs
    edit_mode = True
    selected_tool = None
    
    
    button_y = TITLE_MARGIN + 10
    button_spacing = 50
    menuButtons = [
        MenuButton(GRID_WIDTH + 10, button_y, 180, 50, "Mirror /", "mirror", "/"),
        MenuButton(GRID_WIDTH + 10, button_y + (button_spacing), 180, 50, "Mirror \\", "mirror", "\\"),
        MenuButton(GRID_WIDTH + 10, button_y + (button_spacing * 2), 180, 50, "Ball Up","ball", (0,-1,RED)),
        MenuButton(GRID_WIDTH + 10, button_y + (button_spacing * 3), 180, 50, "Ball Down", "ball", (0,1,BLUE)),
        MenuButton(GRID_WIDTH + 10, button_y + (button_spacing * 4), 180, 50, "Ball Left", "ball", (-1,0,GREEN)),
        MenuButton(GRID_WIDTH + 10, button_y + (button_spacing * 5), 180, 50, "Ball Right", "ball",(1,0,ORANGE)),
        MenuButton(GRID_WIDTH + 10, button_y + (button_spacing * 6), 180, 50, "Output", "output",None),
        MenuButton(GRID_WIDTH + 10, button_y + (button_spacing * 7), 180, 50, "Erase", "erase",None),
        MenuButton(GRID_WIDTH + 10, button_y + (button_spacing * 8), 180, 50, "Simulate", "mode",None),
        MenuButton(GRID_WIDTH + 10, button_y + (button_spacing * 9), 180, 50, "Save", "save",None),
        MenuButton(GRID_WIDTH + 10, button_y + (button_spacing * 10), 180, 50, "Load", "load",None)
        
    ]
    
    # clock and othDer setup
    clock = pygame.time.Clock()
    running = True
    tick_count = 0
    tick_pause = True
    balls_in_input = True
    reverse = False
    
    while running:
        print(tick_count)
        print(balls_in_input)
        # increment or decrement tick count to track balls for reversing but not during edit mode
        if not tick_pause:
            if not edit_mode and not reverse:
                tick_count += 1
            elif not edit_mode and reverse:
                tick_count -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
        
                for button in menuButtons:
                    if button.on_click(mouse_pos):
                        print("mode button")
                        if button.type == "mode":
                            edit_mode = not edit_mode
                            print("edit mode:")
                            print(edit_mode)
                            if not edit_mode:
                                button.label = "Simulate"
                                for ball in balls:
                                    ball.reset()
                                tick_count = 0
                            else:
                                button.label = "Edit"
                        elif button.type == "save":
                            save_model(mirrors, balls, outputs)
                        elif button.type == "load":
                            mirrors, balls, outputs = load_model("model.json")
                        else:
                            print("tool button")
                            for b in menuButtons:
                                b.selected = False
                            button.selected = True
                            selected_tool = button
                            print(selected_tool.type)

                            
                # get grid coordinates to know what cell to place element in
                if edit_mode and mouse_pos[0] < GRID_WIDTH and selected_tool:
                    grid_col = (mouse_pos[0] - LABEL_MARGIN) // CELL_SIZE
                    grid_row = (mouse_pos[1] - LABEL_MARGIN - TITLE_MARGIN) // CELL_SIZE
                    
                    # check that it is within grid bounds
                    if 0 <= grid_col < GRID_SIZE and 0 <= grid_row < GRID_SIZE:
                        if event.button == 1:
                            print("trying to add something")
                            # place type
                            if selected_tool.type == "mirror":
                                print("mirror")
                                mirrors = [m for m in mirrors if not (m.grid_col == grid_col and m.grid_row == grid_row)]
                                mirrors.append(Mirror(grid_row, grid_col, selected_tool.data))
                            elif selected_tool.type == "ball":
                                print("ball")
                                dx, dy, color = selected_tool.data
                                balls = [b for b in balls if not (b.initial_col == grid_col and b.initial_row == grid_row)]
                                balls.append(Ball(grid_row, grid_col, dx, dy, color))
                            elif selected_tool.type == "output":
                                print("output")
                                outputs = [o for o in outputs if not (o.grid_row == grid_row and o.grid_col == grid_col)]
                                outputs.append(Output(grid_row,grid_col))
                                
                            elif selected_tool.type == "erase":
                                mirrors = [m for m in mirrors if not (m.grid_col == grid_col and m.grid_row == grid_row)]
                                balls = [b for b in balls if not (b.initial_col == grid_col and b.initial_row == grid_row)]
                                outputs = [o for o in outputs if not (o.grid_row == grid_row and o.grid_col == grid_col)]
                        print(balls)
                        print(mirrors)
                                
            # setting up keyboard inputs
            if event.type == pygame.KEYDOWN:
                
                if not edit_mode:
                    if event.key == pygame.K_SPACE:
                        print("space_pressed")
                        print("balls:")
                        print(balls)
                        tick_pause = False
                        if balls_in_input:
                            balls_in_input = False
                            reverse = False
                        for ball in balls:
                            ball.moving = True
                    elif event.key == pygame.K_r:
                        if tick_pause:
                            tick_pause = False
                        if reverse:
                            reverse = False
                        else:
                            reverse = True
                        for ball in balls:
                            if not ball.left_input:
                                reverse = False
                            else:
                                ball.dx, ball.dy = ball_reverse(ball.dx,ball.dy)
                

        # Update ball positions and check if they have hit an output while in simulation mode
        if not edit_mode:
            for ball in balls:
                # track ball leaving input
                if ball.moving and not ball.left_input:
                    if not (ball.grid_col == ball.initial_col and ball.grid_row == ball.initial_row):
                        ball.left_input = True
                        
                # stop ball in input if it reverses back into it or output if it reaches it
                if ball.left_input:
                    if (ball.grid_col == ball.initial_col and ball.grid_row == ball.initial_row):
                        ball.moving = False
                        ball.left_input = False
                        ball.dx, ball.dy = ball_reverse(ball.dx,ball.dy)
                       # reverse_change = True
                
                if not ball.reached_output:
                    for output in outputs:
                        if (ball.grid_col == output.grid_col and ball.grid_row == output.grid_row):
                            ball.output = output
                            ball.reached_output = True
                            ball.moving = False
                            ball.stop_tick = tick_count
                        
                if ball.reached_output and not ball.leave_output:
                    if reverse and tick_count <= ball.stop_tick:
                        ball.moving = True
                        ball.leave_output = True
                        
                if ball.leave_output:
                    
                    if (ball.grid_col != ball.output.grid_col or ball.grid_row != ball.output.grid_row):
                        ball.reached_output = False
                        ball.leave_output = False
                        ball.output = None
                        ball.stop_tick = -1
                        
                # update ball position
                ball.update()
            
            if not tick_pause:
                balls_moving = any(ball.moving for ball in balls)
                balls_in_input = not any(ball.left_input for ball in balls)
                if not balls_moving:
                    tick_pause = True
                    
        
        # Draw everything
        screen.fill(WHITE)
        
        # Draw title with configuration
        title_font = pygame.font.Font(None, 32)
        mode_text = "Editor" if edit_mode else "Simulation"
        title = title_font.render(mode_text, True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 15))
        screen.blit(title, title_rect)
        
        # draw ui
        draw_labels()
        draw_grid()
        
        # draw balls and mirrors from data structures
        for output in outputs:
            output.draw(screen)
        for ball in balls:
            ball.draw(screen)
        for mirror in mirrors:
            mirror.draw(screen)
        for b in menuButtons:
            b.draw(screen)
        
        pygame.display.flip()
        
        # run at 45 fps
        clock.tick(45)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()