from flask import Flask, render_template, request, jsonify
import random
import time
import json

app = Flask(__name__)

# Function to create a minesweeper field
def create_field(rows, cols, mines):
    field = [['0' for _ in range(cols)] for _ in range(rows)]
    mine_positions = random.sample(range(rows * cols), mines)
    
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
def reveal_cell(field, row, col, revealed):
    if field[row][col] == 'X':
        return False
    elif field[row][col] != '0':
        revealed[row][col] = True
        return True
    else:
        revealed[row][col] = True
        for i in range(max(0, row-1), min(len(field), row+2)):
            for j in range(max(0, col-1), min(len(field[0]), col+2)):
                if not revealed[i][j]:
                    if not reveal_cell(field, i, j, revealed):
                        return False
        return True

# Function to add/remove a flag
def add_flag(row, col, flags, mines_remaining):
    if flags[row][col]:
        flags[row][col] = False
        mines_remaining += 1
    else:
        flags[row][col] = True
        mines_remaining -= 1
    return mines_remaining

# Function to check if the game is won
def is_game_won(field, revealed, flags):
    for row in range(len(field)):
        for col in range(len(field[0])):
            if field[row][col] == 'X' and not flags[row][col]:
                return False
            if field[row][col] != 'X' and not revealed[row][col]:
                return False
    return True

# Load leaderboard from a file
def load_leaderboard():
    try:
        with open('leaderboard.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save leaderboard to a file
def save_leaderboard(leaderboard):
    with open('leaderboard.json', 'w') as file:
        json.dump(leaderboard, file)

@app.route('/')
def index():
    global field, revealed, flags, start_time, rows, cols, mines
    rows = rows if 'rows' in globals() else 10
    cols = cols if 'cols' in globals() else 10
    mines = mines if 'mines' in globals() else 10
    field = create_field(rows, cols, mines)
    revealed = [[False for _ in range(cols)] for _ in range(rows)]
    flags = [[False for _ in range(cols)] for _ in range(rows)]
    start_time = time.time()
    leaderboard = load_leaderboard()
    return render_template('index.html', rows=rows, cols=cols, mines=mines, leaderboard=leaderboard)

@app.route('/click', methods=['POST'])
def click():
    global field, revealed, flags, mines
    data = request.get_json()
    row = data['row']
    col = data['col']
    action = data['action']  # 'click' or 'flag'
    
    if action == 'flag':
        mines = add_flag(row, col, flags, mines)
        return jsonify({'action': 'flag', 'flags': flags, 'minesRemaining': mines})
    elif action == 'click':
        success = reveal_cell(field, row, col, revealed)
        if not success:
            return jsonify({'success': False, 'field': field, 'revealed': revealed, 'flags': flags})
        else:
            if is_game_won(field, revealed, flags):
                end_time = time.time()
                game_time = int(end_time - start_time)
                leaderboard = load_leaderboard()
                leaderboard.append({'time': game_time})
                leaderboard.sort(key=lambda x: x['time'])
                leaderboard = leaderboard[:10]  # Keep only top 10 scores
                save_leaderboard(leaderboard)
                return jsonify({'success': True, 'field': field, 'revealed': revealed, 'flags': flags, 'won': True, 'time': game_time})
            return jsonify({'success': True, 'field': field, 'revealed': revealed, 'flags': flags})
        
@app.route('/time', methods=['GET'])
def get_game_time():
    global start_time
    current_time = time.time()
    game_time = int(current_time - start_time)
    return jsonify({'time': game_time})

@app.route('/settings', methods=['POST'])
def settings():
    global field, revealed, flags, start_time, rows, cols, mines
    data = request.get_json()
    rows = data['rows']
    cols = data['cols']
    mines = data['mines']
    field = create_field(rows, cols, mines)
    revealed = [[False for _ in range(cols)] for _ in range(rows)]
    flags = [[False for _ in range(cols)] for _ in range(rows)]
    start_time = time.time()
    return jsonify({'success': True, 'rows': rows, 'cols': cols, 'mines': mines})

if __name__ == '__main__':
    app.run(debug=True)