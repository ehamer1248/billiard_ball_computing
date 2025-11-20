import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 25  # 25x25 grid
CELL_SIZE = 35
LABEL_MARGIN = 30  # Space for labels
TITLE_MARGIN = 40  # Space for title at top
A_COL = 0
A_ROW = 4
B_COL = 3
B_ROW = 1
CIN_COL = 8
CIN_ROW = 20
SUM_COL = 14
SUM_ROW = 1
COUT_COL = 20
COUT_ROW = 9
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE + LABEL_MARGIN
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

# Create the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Billiard Ball Full Adder")

# Grid data
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

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
            

            
# Ball properties
class Ball:
    def __init__(self, grid_row, grid_col, dx, dy, color):
        self.grid_row = grid_row
        self.grid_col = grid_col
        self.initial_row = grid_row
        self.initial_col = grid_col
        self.color = color
        # Actual pixel position (centered in cell)
        self.x = (grid_col * CELL_SIZE + CELL_SIZE // 2) + LABEL_MARGIN
        self.y = (grid_row * CELL_SIZE + CELL_SIZE // 2) + LABEL_MARGIN + TITLE_MARGIN
        self.dx = dx
        self.dy = dy
        self.radius = CELL_SIZE // 3
        self.speed = 3  # pixels per frame
        self.stop_tick = 0
        self.reached_output = False
        self.leave_output = False
        self.left_input = False
        self.leave_input = False
        self.moving = False
        
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
                    if (ball.grid_col == self.grid_col - 1 and ball.grid_row == self.grid_row - 1 ) or (ball.grid_col == self.grid_col + 1 and ball.grid_row == self.grid_row + 1 ):
                        # act as a "/" mirror for both balls involved in the collision
                        ball.dx, ball.dy = ball_collision('/',ball.dx,ball.dy)
                        self.dx, self.dy = ball_collision('/',self.dx,self.dy)
                    elif (ball.grid_col == self.grid_col + 1 and ball.grid_row == self.grid_row - 1 ) or (ball.grid_col == self.grid_col - 1 and ball.grid_row == self.grid_row + 1 ):
                        ball.dx, ball.dy = ball_collision('\\',ball.dx,ball.dy)
                        self.dx, self.dy = ball_collision('\\',self.dx,self.dy)
                                       
            else:
                # Move towards target
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
    
    # draw the art for the balls
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw a white highlight
        pygame.draw.circle(surface, WHITE, 
                         (int(self.x - self.radius//3), int(self.y - self.radius//3)), 
                         self.radius//4)

# create mirror configuration
m_and1 = Mirror(6,2,'\\')
# m_and2 = Mirror(5,4,'/')
m_xorA = Mirror(4,7,"\\")
m_xorB = Mirror(8,3,"\\")
m_sumA1 = Mirror(10,7,'\\')
m_sumA2 = Mirror(10,14,'/')
m_sumCin = Mirror(1,8,'/')
m_sumB1 = Mirror(8,15,'/')
m_sumB2 = Mirror(1,15,'\\')
m_coutAandB = Mirror(6,20,'\\')
mirrors = [m_and1,m_xorA,m_xorB,m_sumA1,m_sumA2,m_sumCin,m_sumB1,m_sumB2,m_coutAandB]

# default configuration A=1, B=1, C=1
A = Ball(4, 0, 1, 0, RED)
B = Ball(1, 3, 0, 1, GREEN)
Cin = Ball(20,8,0,-1,BLACK)
and1 = Ball(13, 5, 0, -1, BLUE)
balls = [A,B,Cin]


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
        pygame.draw.line(screen, GRAY, (LABEL_MARGIN, y_pos), (WINDOW_WIDTH, y_pos))

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
   
# function draw outputs and input squares             
def draw_io():
    sum_x =  SUM_COL * CELL_SIZE + LABEL_MARGIN
    sum_y =  SUM_ROW * CELL_SIZE + LABEL_MARGIN + TITLE_MARGIN
    cout_x =  COUT_COL * CELL_SIZE + LABEL_MARGIN
    cout_y =  COUT_ROW * CELL_SIZE + LABEL_MARGIN + TITLE_MARGIN
    cin_x =  CIN_COL * CELL_SIZE + LABEL_MARGIN
    cin_y =  CIN_ROW * CELL_SIZE + LABEL_MARGIN + TITLE_MARGIN
    a_x =  A_COL * CELL_SIZE + LABEL_MARGIN
    a_y =  A_ROW * CELL_SIZE + LABEL_MARGIN + TITLE_MARGIN
    b_x =  B_COL * CELL_SIZE + LABEL_MARGIN
    b_y =  B_ROW * CELL_SIZE + LABEL_MARGIN + TITLE_MARGIN
    
    pygame.draw.rect(screen, PURPLE, (sum_x, sum_y, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, CYAN, (cout_x, cout_y, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, (255, 180, 180), (a_x, a_y, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, (150, 210, 175), (b_x, b_y, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, GRAY, (cin_x, cin_y, CELL_SIZE, CELL_SIZE))

def main():
    global balls
    clock = pygame.time.Clock()
    running = True
    tick_count = 0
    reverse = False
    reverse_change = False
    first_space = True
   
    config_text = "A=1, B=1, Cin=1"  # Default configuration
 
    font = pygame.font.Font(None, 24)
    
    while running:
        # increment or decrement tick count to track balls for reversing
        if not reverse:
            tick_count += 1
        else:
            tick_count -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            
            # setting up keyboard inputs
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not first_space:
                        first_space = True
                        space_tick = tick_count
                    for ball in balls:
                        ball.moving = True
                elif event.key == pygame.K_r:
                    if reverse:
                        reverse = False
                    else:
                        reverse = True
                    for ball in balls:
                        ball.dx, ball.dy = ball_reverse(ball.dx,ball.dy)
                elif event.key == pygame.K_1:
                    # case for A=0, B=0, Cin=0
                    balls = []
                    config_text = "A=0, B=0, Cin=0"
                    reverse = False
                elif event.key == pygame.K_2:
                    # case for A=0, B=0, Cin=1
                    Cin = Ball(20,8,0,-1,BLACK)
                    balls = [Cin]
                    config_text = "A=0, B=0, Cin=1"
                    reverse = False
                elif event.key == pygame.K_3:
                    # case for A=0, B=1, Cin=0
                    B = Ball(1, 3, 0, 1, GREEN)
                    balls = [B]
                    config_text = "A=0, B=1, Cin=0"
                    reverse = False
                elif event.key == pygame.K_4:
                    # case for A=0, B=1, Cin=1
                    B = Ball(1, 3, 0, 1, GREEN)
                    Cin = Ball(20,8,0,-1,BLACK)
                    balls = [B,Cin]
                    config_text = "A=0, B=1, Cin=1"
                    reverse = False
                elif event.key == pygame.K_5:
                    # case for A=1, B=0, Cin=0
                    A = Ball(4, 0, 1, 0, RED)
                    balls = [A]
                    config_text = "A=1, B=0, Cin=0"
                    reverse = False
                elif event.key == pygame.K_6:
                    # case for A=1, B=0, Cin=1
                    A = Ball(4, 0, 1, 0, RED)
                    Cin = Ball(20,8,0,-1,BLACK)
                    balls = [A,Cin]
                    config_text = "A=1, B=0, Cin=1"
                    reverse = False
                elif event.key == pygame.K_7:
                    # case for A=1, B=1, Cin=0
                    A = Ball(4, 0, 1, 0, RED)
                    B = Ball(1, 3, 0, 1, GREEN)
                    balls = [A,B]
                    config_text = "A=1, B=1, Cin=0"
                    reverse = False
                elif event.key == pygame.K_8:
                    # case for A=1, B=1, Cin=1
                    A = Ball(4, 0, 1, 0, RED)
                    B = Ball(1, 3, 0, 1, GREEN)
                    Cin = Ball(20,8,0,-1,BLACK)
                    balls = [A,B,Cin]
                    config_text = "A=1, B=1, Cin=1"
                    reverse = False
                

        # Update ball positions and check if they have hit an output 
        for ball in balls:
            
            # track ball leaving input
            if ball.moving and not ball.left_input:
                if not (ball.grid_col == ball.initial_col and ball.grid_row == ball.initial_row):
                    ball.left_input = True
                    
            # stop ball in input if it reverses back into it
            if ball.left_input:
                if (ball.grid_col == ball.initial_col and ball.grid_row == ball.initial_row):
                    ball.moving = False
                    ball.left_input = False
                    ball.dx, ball.dy = ball_reverse(ball.dx,ball.dy)
                    reverse_change = True

            # check if ball has reached output to stop it there
            if not ball.reached_output:
                if ((ball.grid_col == SUM_COL and ball.grid_row == SUM_ROW) or (ball.grid_col == COUT_COL and ball.grid_row == COUT_ROW)):
                    ball.moving = False
                    ball.reached_output = True
                    ball.stop_tick = tick_count
                  
            # check if ball should leave input on reverse by syncing with ball.stop_tick with every other ball  
            if ball.reached_output and not ball.leave_output:
                if reverse and  tick_count <= ball.stop_tick:
                    ball.moving = True
                    ball.leave_output = True
            
            #  check if ball is done leaving output
            if ball.leave_output:
                if (ball.grid_col != SUM_COL and ball.grid_row != SUM_ROW) and (ball.grid_col != COUT_COL and ball.grid_row != COUT_ROW):
                    ball.leave_output = False
                    ball.reached_output = False
                    
                
            # update ball position
            ball.update()
            
        # handle reverse changes
        if reverse_change:
            reverse = not reverse
            reverse_change = False
        
        # Draw everything
        screen.fill(WHITE)
        
        # Draw title with configuration
        title_font = pygame.font.Font(None, 32)
        title = title_font.render(config_text, True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 15))
        screen.blit(title, title_rect)
        
        # draw ui
        draw_labels()
        draw_io()
        draw_grid()
        
        # draw balls and mirrors from data structures
        for ball in balls:
            ball.draw(screen)
        for mirror in mirrors:
            mirror.draw(screen)
        
        pygame.display.flip()
        
        # run at 45 fps
        clock.tick(45)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()