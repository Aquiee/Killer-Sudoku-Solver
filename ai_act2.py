# Mark Toni Ramsol Tagalogon

import pygame
import sys
import random
import numpy as np
import time

# Define constants
GRID_SIZE = 4
CELL_SIZE = 100
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE
WHITE = (255, 255, 255, 0) 
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Annealing config
a_temperature = 1.5
a_cooling_rate = 0.95
a_iterations = 100

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Killer Sudoku Maker")

# Backend
def generate_board():
    # Generates a random initial board for the Sudoku puzzle.
    board = [[0 for _ in range(4)] for _ in range(4)]
    quadrant_values = [random.sample(range(1, 5), 4) for _ in range(4)]
    quadrants = [(0, 0), (0, 1), (1, 0), (1, 1)]
    random.shuffle(quadrants)
    
    for idx, (qi, qj) in enumerate(quadrants):
        values = quadrant_values[idx]
        for i in range(2):
            for j in range(2):
                board[qi * 2 + i][qj * 2 + j] = values[i * 2 + j]
    
    return board


def is_valid(board, row, col, num, constraints):
    # Checks if placing 'num' at (row, col) violates Sudoku and Killer Sudoku rules.

    for c in range(4):
        if board[row][c] == num and c != col:
            return False
    for r in range(4):
        if board[r][col] == num and r != row:
            return False
        
    start_row = (row // 2) * 2
    start_col = (col // 2) * 2
    for i in range(start_row, start_row + 2):
        for j in range(start_col, start_col + 2):
            if board[i][j] == num and (i, j) != (row, col):
                return False
            
    region_sum = 0
    for cells, target_sum in constraints:
        if (row, col) in cells:
            for r, c in cells:
                if board[r][c] == num:
                    return False  
                region_sum += board[r][c]
            if region_sum + num > target_sum:
                return False 
            break  
    return True

def fitness(board, constraints):
    # Calculates the fitness score of the current board.
    score = 0
    for i in range(4):
        row_values = set()
        col_values = set()
        for j in range(4):
            row_value = board[i][j]
            col_value = board[j][i]
            if row_value not in range(1, 5) or col_value not in range(1, 5):
                score += 1  
            if row_value in row_values or col_value in col_values:
                score += 1  
            row_values.add(row_value)
            col_values.add(col_value)
    for cells, target_sum in constraints:
        cell_sum = sum(board[row][col] for row, col in cells)
        if cell_sum != target_sum:
            score += 1  
    return score


import random

def select_neighbor(board):
    # Selects a neighboring solution by swapping two random cells in the same quadrant.
    quadrant_i, quadrant_j = random.randint(0, 1), random.randint(0, 1)
    
    i1, j1 = random.randint(0, 1), random.randint(0, 1)
    i2, j2 = random.randint(0, 1), random.randint(0, 1)
    
    i1 += quadrant_i * 2
    j1 += quadrant_j * 2
    i2 += quadrant_i * 2
    j2 += quadrant_j * 2
    
    board[i1][j1], board[i2][j2] = board[i2][j2], board[i1][j1]
    
    return board, (i1, j1), (i2, j2)


def simulated_annealing(board, constraints, all_selected_groups, temperature, cooling_rate, iterations):
    # Solves the Sudoku puzzle using simulated annealing.
    if fitness(board, constraints) == 0:
        print("Initial board is already a correct solution. No iterations needed.")
        return board , True

    best_board = board.copy()
    best_score = fitness(board, constraints)
    while temperature > 0.0 and iterations > 0:
        for _ in range(iterations):
            new_board, (i1, j1), (i2, j2) = select_neighbor(board)
            
            new_score = fitness(new_board, constraints)
            delta_e = new_score - best_score

            if delta_e < 0 or random.random() < np.exp(-delta_e / temperature):
                best_score = new_score
                best_board = new_board.copy()
            else:
                best_board[i1][j1], best_board[i2][j2] = best_board[i2][j2], best_board[i1][j1]

            if fitness(best_board, constraints) == 0:
                print("Correct solution found. Stopping iterations.")
                return best_board , True

        # Print the board after each iteration
        print("Current board:")
        for row in best_board:
            print([max(1, min(4, num)) for num in row])  
        
        draw_grid(all_selected_groups,best_board)

        pygame.display.flip()
        
        time.sleep(0.1)
        temperature *= cooling_rate
        
        iterations -= 1  
        
        if temperature <= 0.0:
            break
                
    return best_board , False

# Frontend
def draw_grid(selected_group, solution=None, draw=True):
    window.fill(WHITE) 
    font = pygame.font.Font(None, 36)  

    if draw:
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(window, BLACK, rect, 1)

    if selected_group:
        for group in selected_group:
            for i, j in group[:-1]:  
                if i < GRID_SIZE - 1 and (i + 1, j) in group:
                    pygame.draw.line(window, WHITE, (j * CELL_SIZE+1, (i + 1) * CELL_SIZE),
                                     ((j + 1) * CELL_SIZE-2, (i + 1) * CELL_SIZE), 3) 
                if j < GRID_SIZE - 1 and (i, j + 1) in group:
                    pygame.draw.line(window, WHITE, ((j + 1) * CELL_SIZE, i * CELL_SIZE +1),
                                     ((j + 1) * CELL_SIZE, (i + 1) * CELL_SIZE - 2), 3)  

            first_cell = group[0]
            if not isinstance(group[-1], tuple):
                sum_value = group[-1]
                if sum_value != 0:  
                    sum_text = str(sum_value)
                    font = pygame.font.Font(None, 36)
                    text_surface = font.render(sum_text, True, BLACK)

                    text_rect = text_surface.get_rect(
                        topleft=(first_cell[1] * CELL_SIZE + 2, first_cell[0] * CELL_SIZE + 2)
                    )

                    window.blit(text_surface, text_rect)

                    line_length = 3  
                    pygame.draw.line(window, BLACK, (text_rect.right + 3, text_rect.top -1), (text_rect.right + 3, text_rect.bottom + line_length), 3)
                    pygame.draw.line(window, BLACK, (text_rect.left - 1, text_rect.bottom + 2), (text_rect.right + line_length, text_rect.bottom + 2), 3)

    if solution:
        for i in range(len(solution)):
            for j in range(len(solution[i])):
                cell_value = solution[i][j]
                if isinstance(cell_value, int):
                    cell_value = str(cell_value)
                    text_surface = font.render(cell_value, True, BLACK)
                    text_rect = text_surface.get_rect(
                        center=(j * CELL_SIZE + CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2)
                    )
                    window.blit(text_surface, text_rect)

    all_cells = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)]
    cells_in_groups = [cell for group in selected_group for cell in group[:-1]]
    
    all_cells_included = set(all_cells) == set(cells_in_groups)
    all_groups_have_int = all(isinstance(group[-1], int) for group in selected_group if group)  
    
    return all_cells_included, all_groups_have_int

def show_button():
    button_width = 100
    button_height = 50
    button_rect = pygame.Rect((WINDOW_WIDTH - button_width) // 2, WINDOW_HEIGHT - 70, button_width, button_height)
    pygame.draw.rect(window, (0, 255, 0), button_rect)

    font = pygame.font.Font(None, 36)
    text_surface = font.render("Solve", True, BLACK)
    text_rect = text_surface.get_rect(center=button_rect.center)
    window.blit(text_surface, text_rect)
    return button_rect

def show_sum(sum_value, group):
    window.fill(GREEN, (group[0][1] * CELL_SIZE, group[0][0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    first_cell = group[0]

    if sum_value != 0:  
        sum_text = str(sum_value)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(sum_text, True, BLACK)
        text_rect = text_surface.get_rect(
            topleft=(first_cell[1] * CELL_SIZE + 2, first_cell[0] * CELL_SIZE + 2)
        )
        window.blit(text_surface, text_rect)

def draw_pause_screen():
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(128)  
    overlay.fill(WHITE)
    window.blit(overlay, (0, 0))


    def draw_instructions():
        title_font = pygame.font.SysFont("comic sans ms", 20) 
        title_text = "KILLER SUDOKU MAKER/SOLVER 4X4"
        title_surface = title_font.render(title_text, True, BLACK)
        title_rect = title_surface.get_rect(midtop=(WINDOW_WIDTH // 2, 30))
        window.blit(title_surface, title_rect)

        # Draw instructions text
        font = pygame.font.SysFont("comic sans ms", 15) 
        instructions_text = [
            "Instructions:",
            '"Right mouse click" to GROUP cells',
            '"Left mouse click" to highlight GROUPED cells',
            '"Input" sum on highlighted group',
            '"Enter" to save GROUP / SUM',
            '"R" to RESET',
            '"P" to pause / show instructions again'
        ]
        y_offset = title_rect.bottom + 40  
        for line in instructions_text:
            text = font.render(line, True, BLACK)
            text_rect = text.get_rect(midleft=(50, y_offset))
            window.blit(text, text_rect)
            y_offset += 25 


    draw_instructions()

    play_button = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 100, 100, 50)
    pygame.draw.rect(window, GREEN, play_button)
    font = pygame.font.SysFont(None, 30)
    play_text = font.render("Play", True, BLACK)
    text_rect = play_text.get_rect(center=play_button.center)
    window.blit(play_text, text_rect)

def draw_result(is_correct):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)  
    overlay.set_alpha(128)  
    overlay.fill(WHITE)
    window.blit(overlay, (0, 0))
    font = pygame.font.SysFont("comic sans ms", 25)

    if is_correct:
        text1 = font.render("Found a solution", True, BLACK)
        text2 = font.render("Click anywhere to Show solution", True, BLACK)
        rect_color = GREEN  
    else:
        text1 = font.render("Did not find a solution", True, BLACK)  # Corrected typo
        text2 = font.render("Click anywhere to solve again", True, BLACK)
        rect_color = RED  

    text1_rect = text1.get_rect()
    text2_rect = text2.get_rect()

    text1_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    text2_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + text1_rect.height + 55)

    pygame.draw.rect(window, GRAY, text1_rect)
    pygame.draw.rect(window, GRAY, text2_rect)
    pygame.draw.rect(window, rect_color, text1_rect.inflate(10, 10)) 
    pygame.draw.rect(window, rect_color, text2_rect.inflate(10, 10))

    window.blit(text1, text1_rect)
    window.blit(text2, text2_rect)
    
def main():
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    all_selected_groups = []  
    selected_group = []
    highlighted_green = []
    draw_grid(selected_group)
    current_sum = 0
    button_displayed = False 
    running = True
    solve_finished = False
    paused = True 
    result = False
    result_pause = False
    solution_local = []

    while running:
        if not paused and not result:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not button_displayed:  
                        if event.button == 1: # Left click
                            x, y = pygame.mouse.get_pos()
                            row, column = y // CELL_SIZE, x // CELL_SIZE  
                            for group in all_selected_groups:
                                draw_grid(all_selected_groups)
                                if (row, column) in group:
                                    highlighted_green = []
                                    current_sum = 0
                                    for cell in group:
                                        if isinstance(cell, tuple):  
                                            pygame.draw.rect(window, GREEN,
                                                            (cell[1] * CELL_SIZE, cell[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                                            highlighted_green.append((cell[0], cell[1]))

                                    pygame.display.flip()  
                                    break  
                        elif event.button == 3:  # Right click
                            highlighted_green = []
                            current_sum = []
                            x, y = pygame.mouse.get_pos()
                            row, column = y // CELL_SIZE, x // CELL_SIZE  
                            if (row, column) not in [cell for group in all_selected_groups for cell in group]:  # Check if cell is not part of any group
                                if (row, column) in selected_group:
                                    selected_group.remove((row, column)) 
                                    draw_grid(all_selected_groups)
                                else:
                                    selected_group.append((row, column))  
                    elif button_displayed and event.button == 1: 
                        x, y = pygame.mouse.get_pos()
                        if button_rect.collidepoint(x, y):  
                            # Convert to new format
                            new_constraints = []
                            for group  in all_selected_groups:
                                coordinates = group [:-1]  
                                value = group [-1]  
                                new_constraints.append((coordinates, value))
                            board = generate_board()
                            solution , is_correct = simulated_annealing(board, new_constraints, all_selected_groups, a_temperature, a_cooling_rate, a_iterations )
                            print("Final solution:")
                            solution_local = [sublist[:] for sublist in solution]
                            for row in solution:
                                print(row)
                            solve_finished = True
                            result = True
                            result_pause = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if selected_group:
                            sorted_groups = sorted(selected_group)
                            all_selected_groups.append(sorted_groups[:])  
                            selected_group = []
                            draw_grid(all_selected_groups)

                        if highlighted_green:
                            group_found = False

                            if highlighted_green in all_selected_groups and current_sum != 0:
                                for group in all_selected_groups:
                                    if highlighted_green == group:

                                        group.append(current_sum)
                                        group_found = True
                                        current_sum = 0
                                        highlighted_green = []
                                        draw_grid(all_selected_groups)
                                        break

                            if not group_found:
                                current_sum = 0
                                draw_grid(all_selected_groups)


                    elif event.key == pygame.K_BACKSPACE:
                        if highlighted_green:
                            current_sum = current_sum // 10
                            show_sum(current_sum,highlighted_green)
                    elif event.key == pygame.K_r:
                        all_selected_groups.clear()
                        current_sum = 0
                        button_displayed = False
                        selected_group = []
                        solution_local.clear()
                        result_pause = False
                        print("Reseted")

                        draw_grid(all_selected_groups)

                    elif pygame.K_0 <= event.key <= pygame.K_9:
                        if highlighted_green:
                            num_pressed = event.key - pygame.K_0
                            current_sum = current_sum * 10 + num_pressed
                            show_sum(current_sum, highlighted_green)  
                    elif event.key == pygame.K_p:  
                        paused = not paused  

            for cell in selected_group:
                pygame.draw.rect(window, RED, (cell[1] * CELL_SIZE, cell[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            
            all_cells = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)]
            cells_in_groups = [cell for group in all_selected_groups for cell in group[:-1]]
            
            all_cells_included = set(all_cells) == set(cells_in_groups)
            all_groups_have_int = all(isinstance(group[-1], int) for group in all_selected_groups if group)  # Only check non-empty groups
            
            if all_cells_included and all_groups_have_int and not button_displayed and not solve_finished:
                button_rect = show_button()
                button_displayed = True  
                pygame.display.flip()
            else:
                pygame.display.flip()

            pass
        elif paused:
            draw_pause_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    play_button = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 100, 100, 50)
                    if play_button.collidepoint(x, y):
                        paused = False
                        if result_pause:
                            draw_grid(all_selected_groups,solution_local)
                        if not result_pause:
                            draw_grid(all_selected_groups)
                            print("play")


        elif result:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    button_result = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
                    if button_result.collidepoint(x, y):
                        if not is_correct:
                            board = generate_board()
                            solution, is_correct = simulated_annealing(board, new_constraints, all_selected_groups, a_temperature, a_cooling_rate, a_iterations)
                        else:
                            draw_grid(all_selected_groups, solution)
                            result = False
                            solve_finished = False

                        break
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    all_selected_groups.clear()
                    current_sum = 0
                    button_displayed = False
                    selected_group = []
                    result = False
                    solve_finished = False
                    solution_local.clear()
                    result_pause = False
                    print("Reseted")
                    print(solution_local)
                    draw_grid(all_selected_groups)
                    pygame.display.flip()

            if result:
                draw_result(is_correct)  
            

                    
        
        pygame.display.flip()


    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
