import random, flet
from flet import Page, Container, Row, Column, Text, ElevatedButton, colors, alignment, KeyboardEvent, animation, border_radius, GestureDetector

GRID_SIZE = 4
tile_colors = {
    0: colors.GREY_300,
    2: colors.LIGHT_BLUE_200,
    4: colors.LIGHT_GREEN_300,
    8: colors.ORANGE,
    16: colors.PINK_300,
    32: colors.YELLOW,
    64: colors.RED,
    128: colors.PURPLE,
    256: colors.RED_200,
    512: colors.PINK_200,
    1024: colors.GREEN_200,
}

def initialize_grid():
    return [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

def add_random_tile(grid):
    empty_tiles = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]
    if empty_tiles:
        r, c = random.choice(empty_tiles)
        grid[r][c] = 2 if random.random() < 0.9 else 4

def update_grid_display(grid, controls):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            value = grid[r][c]
            value_str = str(value) if value else ""
            
            # Adjust font size based on the length of the number
            if len(value_str) <= 2:
                font_size = 36
            elif len(value_str) == 3:
                font_size = 28
            else:
                font_size = 24
            
            controls[r].controls[c].content.value = value_str
            controls[r].controls[c].bgcolor = tile_colors[value]
            controls[r].controls[c].content.size = font_size
            controls[r].controls[c].content.color = colors.BLACK if value else colors.WHITE
            controls[r].controls[c].border_radius = border_radius.all(12)
            controls[r].controls[c].update()

def move_left(grid):
    global score
    moved = False
    
    for r in range(GRID_SIZE):
        new_row = [i for i in grid[r] if i != 0]
        
        merged_row = []
        skip = False

        for i in range(len(new_row)):
            if skip:
                skip = False
                continue

            if i + 1 < len(new_row) and new_row[i] == new_row[i + 1]:
                merged_row.append(new_row[i] * 2)
                score += new_row[i] * 2
                skip = True
                moved = True
            else:
                merged_row.append(new_row[i])

        merged_row += [0] * (GRID_SIZE - len(merged_row))

        if grid[r] != merged_row:
            moved = True
            grid[r] = merged_row

    return moved, grid

def move_right(grid):
    grid = [reverse(row) for row in grid]
    moved, grid = move_left(grid)
    grid = [reverse(row) for row in grid]
    return moved, grid

def move_up(grid):
    grid = transpose(grid)
    moved, grid = move_left(grid)
    grid = transpose(grid)
    return moved, grid

def move_down(grid):
    grid = transpose(grid)
    grid = [reverse(row) for row in grid]
    moved, grid = move_left(grid)
    grid = [reverse(row) for row in grid]
    grid = transpose(grid)
    return moved, grid

def reverse(row):
    return row[::-1]

def transpose(grid):
    return [list(row) for row in zip(*grid)]

def check_win_condition(grid):
    for row in grid:
        if 1024 in row:  # Adjusted to 1024 for this game
            return True
    return False

def can_merge(grid):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if c + 1 < GRID_SIZE and grid[r][c] == grid[r][c + 1]:
                return True
            if r + 1 < GRID_SIZE and grid[r][c] == grid[r + 1][c]:
                return True
    return False

def check_loss_condition(grid):
    if any(0 in row for row in grid):
        return False
    if can_merge(grid):
        return False
    return True

def on_key_press(event: KeyboardEvent):
    global score_text, high_score, high_score_text, grid
    key = event.key
    moved = False

    if key == "Arrow Left":
        moved, grid = move_left(grid)
    elif key == "Arrow Right":
        moved, grid = move_right(grid)
    elif key == "Arrow Up":
        moved, grid = move_up(grid)
    elif key == "Arrow Down":
        moved, grid = move_down(grid)

    if moved:
        add_random_tile(grid)
        update_grid_display(grid, controls)
        score_text.value = f"Score: {score}"
        score_text.update()

        if score > high_score:
            high_score = score
            high_score_text.value = f"High Score: {high_score}"
            high_score_text.update()

        if check_win_condition(grid):
            print("Game won!")
        elif check_loss_condition(grid):
            print("Game lost!")

def restart_game(e):
    global grid, score
    grid = initialize_grid()
    score = 0
    add_random_tile(grid)
    add_random_tile(grid)
    update_grid_display(grid, controls)
    score_text.value = f"Score: {score}"
    score_text.update()
    
def on_pan_update(event):
    global score_text, high_score, high_score_text, grid
    moved = False
    direction = ""

    if abs(event.delta_x) > abs(event.delta_y):
        if event.delta_x > 0:
            direction = "Right"
            moved, grid = move_right(grid)
        else:
            direction = "Left"
            moved, grid = move_left(grid)
    else:
        if event.delta_y > 0:
            direction = "Down"
            moved, grid = move_down(grid)
        else:
            direction = "Up"
            moved, grid = move_up(grid)

    print(f"Swipe detected: {direction}")
    if moved:
        add_random_tile(grid)
        update_grid_display(grid, controls)
        score_text.value = f"Score: {score}"
        score_text.update()
        print(f"Score: {score}")

        if score > high_score:
            high_score = score
            high_score_text.value = f"High Score: {high_score}"
            high_score_text.update()

        if check_win_condition(grid):
            print("Game won!")
        elif check_loss_condition(grid):
            print("Game lost!")

def main(page: Page):
    page.title = "2048 GAME"
    page.window_width = 360
    page.window_height = 640
    
    page.window_min_width = 300
    page.window_min_height = 300
    page.window_max_width = 1200
    page.window_max_height = 900

    
    global grid, controls, score, score_text, high_score, high_score_text

    grid = initialize_grid()
    controls = []
    score = 0

    high_score = int(page.client_storage.get("high_score") or "0")

    tile_size = min(page.width, page.height) // (GRID_SIZE + 5)
    font_size = tile_size // 2

    for _ in range(GRID_SIZE):
        row = Row(
            expand=True,
            spacing=10,
            controls=[
                Container(
                    width=tile_size,
                    height=tile_size,
                    bgcolor=colors.GREY_300,
                    content=Text("", color=colors.BLACK, size=font_size),
                    padding=10,
                    animate=animation.Animation(duration=300),
                    border_radius=border_radius.all(12),
                )
                for _ in range(GRID_SIZE)
            ],
        )
        controls.append(row)
    
    # Wrap the entire grid inside a GestureDetector
    grid_with_gestures = GestureDetector(
        content=Column(expand=True, controls=controls, alignment=alignment.center),
        on_pan_update=on_pan_update,
    )

    # Create a container to hold the grid and the gesture detector
    grid_container = Container(
        content=grid_with_gestures,
        expand=True,
        alignment=alignment.center
    )

    # Add the grid container to the page
    page.add(grid_container)

    add_random_tile(grid)
    add_random_tile(grid)
    update_grid_display(grid, controls)

    score_text = Text(f"Score: {score}", size=30, color=colors.YELLOW_100, weight="bold")
    high_score_text = Text(f"High Score: {high_score}", size=30, color=colors.BLUE_300, weight="bold")
    
    restart_button = ElevatedButton(
        text="Restart Game",
        on_click=restart_game,
    )
    
    # Add score display and restart button
    page.add(Column(
        expand=False,
        controls=[
            score_text,
            high_score_text,
            restart_button,
        ],
        alignment=alignment.center,
        spacing=10
    ))
    
    page.on_keyboard_event = on_key_press
    page.update()
    
flet.app(target=main)
