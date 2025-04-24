from flask import Flask, render_template, request, jsonify
import random
import time
import json
from datetime import datetime

app = Flask(__name__)

timer_started = False  # Tracks whether the timer has started

# Function to create a minesweeper field
# Generates a grid with the specified number of rows, columns, and mines
def create_field(rows, cols, mines):
    field = [['0' for _ in range(cols)] for _ in range(rows)]
    mine_positions = random.sample(range(rows * cols), mines)
    
    # Place mines in the field
    for pos in mine_positions:
        row = pos // cols
        col = pos % cols
        field[row][col] = 'X'
    
    # Calculate the number of adjacent mines for each cell
    for row in range(rows):
        for col in range(cols):
            if field[row][col] == 'X':
                continue
            count = 0
            for i in range(max(0, row-1), min(rows, row+2)):
                for j in range(max(0, col-1), min(cols, col+2)):
                    if field[i][j] == 'X':
                        count += 1
            field[row][col] = str(count)
    
    return field

# Function to reveal a cell
# Reveals the cell and recursively reveals adjacent cells if the cell is empty ('0')
def reveal_cell(field, row, col, revealed):
    if field[row][col] == 'X':  # If the cell is a mine, return False
        return False
    elif field[row][col] != '0':  # If the cell is not empty, reveal it and return True
        revealed[row][col] = True
        return True
    else:
        revealed[row][col] = True
        # Recursively reveal adjacent cells
        for i in range(max(0, row-1), min(len(field), row+2)):
            for j in range(max(0, col-1), min(len(field[0]), col+2)):
                if not revealed[i][j]:
                    if not reveal_cell(field, i, j, revealed):
                        return False
        return True

# Function to add or remove a flag
# Updates the flag status of a cell and adjusts the remaining mine count
def add_flag(row, col, flags, mines_remaining):
    if flags[row][col]:
        flags[row][col] = False
        mines_remaining += 1
    else:
        flags[row][col] = True
        mines_remaining -= 1
    return mines_remaining

# Function to check if the game is won
# The game is won if all free cells are revealed or all mines are flagged
def is_game_won(field, revealed, flags):
    all_free_cells_revealed = True
    all_mines_flagged = True

    for row in range(len(field)):
        for col in range(len(field[0])):
            # Check if all non-mine cells are revealed
            if field[row][col] != 'X' and not revealed[row][col]:
                all_free_cells_revealed = False
            # Check if all mines are flagged
            if field[row][col] == 'X' and not flags[row][col]:
                all_mines_flagged = False

    return all_free_cells_revealed or all_mines_flagged

# Load leaderboard from a file
# Reads the leaderboard data from 'leaderboard.json'
def load_leaderboard():
    try:
        with open('leaderboard.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save leaderboard to a file
# Writes the leaderboard data to 'leaderboard.json'
def save_leaderboard(leaderboard):
    with open('leaderboard.json', 'w') as file:
        json.dump(leaderboard, file)

@app.route('/')
def index():
    # Initialize the game field and settings
    global field, revealed, flags, start_time, rows, cols, mines, timer_started
    rows = rows if 'rows' in globals() else 8
    cols = cols if 'cols' in globals() else 8
    mines = mines if 'mines' in globals() else 10
    field = create_field(rows, cols, mines)
    revealed = [[False for _ in range(cols)] for _ in range(rows)]
    flags = [[False for _ in range(cols)] for _ in range(rows)]
    start_time = time.time()
    timer_started = False
    leaderboard = load_leaderboard()
    return render_template('index.html', rows=rows, cols=cols, mines=mines, leaderboard=leaderboard)

@app.route('/click', methods=['POST'])
def click():
    global field, revealed, flags, mines, timer_started, start_time
    data = request.get_json()
    row = data['row']
    col = data['col']
    action = data['action']  # 'click' or 'flag'

    if action == 'flag':
        mines = add_flag(row, col, flags, mines)
        if is_game_won(field, revealed, flags):
            end_time = time.time()
            game_time = int(end_time - (start_time if timer_started else end_time))
            leaderboard = load_leaderboard()
            leaderboard.append({
                'time': game_time,
                'date': datetime.now().strftime('%d/%m/%Y'),
                'time_of_day': datetime.now().strftime('%H:%M:%S'),
                'ip': request.remote_addr
            })
            leaderboard.sort(key=lambda x: x['time'])
            leaderboard = leaderboard[:10]
            save_leaderboard(leaderboard)
            return jsonify({'action': 'flag', 'flags': flags, 'minesRemaining': mines, 'won': True, 'time': game_time})
        return jsonify({'action': 'flag', 'flags': flags, 'minesRemaining': mines})

    elif action == 'click':
        if not timer_started:
            start_time = time.time()
            timer_started = True
        success = reveal_cell(field, row, col, revealed)
        if not success:
            return jsonify({'success': False, 'field': field, 'revealed': revealed, 'flags': flags})
        else:
            if is_game_won(field, revealed, flags):
                end_time = time.time()
                game_time = int(end_time - start_time)
                leaderboard = load_leaderboard()
                leaderboard.append({
                    'time': game_time,
                    'date': datetime.now().strftime('%d/%m/%Y'),
                    'time_of_day': datetime.now().strftime('%H:%M:%S'),
                    'ip': request.remote_addr
                })
                leaderboard.sort(key=lambda x: x['time'])
                leaderboard = leaderboard[:10]
                save_leaderboard(leaderboard)
                return jsonify({'success': True, 'field': field, 'revealed': revealed, 'flags': flags, 'won': True, 'time': game_time})
            return jsonify({'success': True, 'field': field, 'revealed': revealed, 'flags': flags})

@app.route('/time', methods=['GET'])
def get_game_time():
    # Get the elapsed game time only if the timer has started
    global start_time, timer_started
    if not timer_started:
        return jsonify({'time': 0})  # Return 0 if the timer hasn't started
    current_time = time.time()
    game_time = int(current_time - start_time)
    return jsonify({'time': game_time})

@app.route('/start_timer', methods=['POST'])
def start_timer():
    # Start the timer when the player clicks "Start" or a cell
    global start_time, timer_started
    if not timer_started:
        start_time = time.time()
        timer_started = True
    return jsonify({'success': True})

@app.route('/settings', methods=['POST'])
def settings():
    # Update game settings (rows, columns, mines)
    global field, revealed, flags, start_time, rows, cols, mines, timer_started
    data = request.get_json()
    rows = data['rows']
    cols = data['cols']
    mines = data['mines']
    field = create_field(rows, cols, mines)
    revealed = [[False for _ in range(cols)] for _ in range(rows)]
    flags = [[False for _ in range(cols)] for _ in range(rows)]
    start_time = time.time()
    timer_started = False
    return jsonify({'success': True, 'rows': rows, 'cols': cols, 'mines': mines})

if __name__ == '__main__':
    app.run(host='0.0.0.0')