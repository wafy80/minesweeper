# Minesweeper

A web-based implementation of the classic Minesweeper game built using Python (Flask) for the backend and HTML, CSS, and JavaScript for the frontend.

## Features

- **Customizable Game Settings**: Adjust the number of rows, columns, and mines.
- **Leaderboard**: Tracks the top 10 fastest times.
- **Dynamic Timer**: Displays the elapsed time during gameplay.
- **Flagging System**: Right-click to flag suspected mines.
- **Responsive Design**: Works on various screen sizes.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/wafy80/minesweeper.git
   cd minesweeper
   ```

2. Install dependencies:
   ```bash
   pip install flask
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## File Structure

```
minesweeper/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
├── templates/
│   └── index.html
├── app.py
├── leaderboard.json
└── README.md
```

## How to Play

1. Click on a cell to reveal it.
2. Right-click on a cell to flag it as a mine.
3. Clear all non-mine cells to win the game.
4. If you click on a mine, you lose.

## Customization

You can adjust the default game settings (rows, columns, and mines) by modifying the `index()` function in `app.py`.

## Leaderboard

The leaderboard is stored in `leaderboard.json`. It keeps track of the top 10 fastest times.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.