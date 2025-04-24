document.addEventListener('DOMContentLoaded', function() {
    const cells = document.querySelectorAll('.cell');
    const minesRemainingElement = document.getElementById('mines-remaining');
    const timerElement = document.getElementById('timer');
    const leaderboardList = document.getElementById('leaderboard-list');
    const messageElement = document.getElementById('message'); 
    let minesRemaining = parseInt(document.getElementById('mines').textContent) || 0;
    let startTime = true;

    function updateMinesRemaining() {
        minesRemainingElement.textContent = `${minesRemaining}`;
    }

    function updateTimer() {
        fetch('/time')
            .then(response => response.json())
            .then(data => {
                timerElement.textContent = `${data.time}`;
            });
    }

    function showMessage(message, type) {
        messageElement.textContent = message;
        messageElement.className = type;
    }

    function highlightMines(field) {
        // Highlight all cells that contain mines
        field.forEach((row, i) => {
            row.forEach((cell, j) => {
                if (cell === 'X') { // 'X' represents a mine
                    const mineCell = document.querySelector(`.cell[data-row="${i}"][data-col="${j}"]`);
                    mineCell.classList.add('mine'); // Add the 'mine' class
                }
            });
        });
    }

    setInterval(updateTimer, 1000);

    cells.forEach(cell => {
        cell.addEventListener('click', function() {
            if (startTime) {
                startTime = false;
                startTimer(); // Start the timer on the first click
            }
            const row = cell.getAttribute('data-row');
            const col = cell.getAttribute('data-col');
            fetch('/click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({row: parseInt(row), col: parseInt(col), action: 'click'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    data.revealed.forEach((r, i) => {
                        r.forEach((c, j) => {
                            if (c) {
                                const cell = document.querySelector(`.cell[data-row="${i}"][data-col="${j}"]`);
                                cell.classList.add('revealed');
                                if (data.field[i][j] !== '0') {
                                    cell.textContent = data.field[i][j];
                                }
                            }
                        });
                    });
                    if (data.won) {
                        showMessage(`You won in ${data.time} seconds!`, 'success');
                        highlightMines(data.field); // Highlight mines on victory
                        updateLeaderboard(data.time);
                    }
                } else {
                    showMessage('You lost!', 'error');
                    highlightMines(data.field); // Highlight mines on defeat
                    data.revealed.forEach((r, i) => {
                        r.forEach((c, j) => {
                            if (c) {
                                const cell = document.querySelector(`.cell[data-row="${i}"][data-col="${j}"]`);
                                cell.classList.add('revealed');
                                if (data.field[i][j] === 'X') {
                                    cell.classList.add('mine');
                                } else {
                                    cell.textContent = data.field[i][j];
                                }
                            }
                        });
                    });
                }
            });
        });

        cell.addEventListener('contextmenu', function(event) {
            event.preventDefault();
            if (startTime) {
                startTime = false;
            }
            const row = cell.getAttribute('data-row');
            const col = cell.getAttribute('data-col');
            fetch('/click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({row: parseInt(row), col: parseInt(col), action: 'flag'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.action === 'flag') {
                    data.flags.forEach((r, i) => {
                        r.forEach((c, j) => {
                            const cell = document.querySelector(`.cell[data-row="${i}"][data-col="${j}"]`);
                            if (c) {
                                cell.classList.add('flag');
                            } else {
                                cell.classList.remove('flag');
                            }
                        });
                    });
                    minesRemaining = data.minesRemaining;
                    updateMinesRemaining();

                    if (data.won) {
                        showMessage(`You won in ${data.time} seconds!`, 'success');
                        highlightMines(data.field); // Highlight mines on victory
                        updateLeaderboard(data.time);
                    }
                }
            });
        });
    });

    function updateLeaderboard() {
        const leaderboardTableBody = document.querySelector('#leaderboard-table tbody');
        leaderboardTableBody.innerHTML = ''; // Clear the existing table
        fetch('/')
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const leaderboardRows = doc.querySelectorAll('#leaderboard-table tbody tr');
                leaderboardRows.forEach(row => {
                    leaderboardTableBody.appendChild(row.cloneNode(true));
                });
            });
    }
});

function applySettings() {
    const rows = document.getElementById('rows').value;
    const cols = document.getElementById('cols').value;
    const mines = document.getElementById('mines').value;
    fetch('/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({rows: parseInt(rows), cols: parseInt(cols), mines: parseInt(mines)})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
            startTimer(); // Start the timer when the game is reset
        }
    });
}

function startTimer() {
    fetch('/start_timer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
}
