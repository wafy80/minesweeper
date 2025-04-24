document.addEventListener('DOMContentLoaded', function() {
    const cells = document.querySelectorAll('.cell');
    const minesRemainingElement = document.getElementById('mines-remaining');
    const timerElement = document.getElementById('timer');
    const leaderboardList = document.getElementById('leaderboard-list');
    let minesRemaining = parseInt(document.getElementById('mines').textContent) || 0;
    let startTime = true;

    function updateMinesRemaining() {
        minesRemainingElement.textContent = `Mines remaining: ${minesRemaining}`;
    }

    function updateTimer() {
        fetch('/time')
            .then(response => response.json())
            .then(data => {
                timerElement.textContent = `Time: ${data.time}`;
            });
    }

    setInterval(updateTimer, 1000);

    cells.forEach(cell => {
        cell.addEventListener('click', function() {
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
                        alert(`You won in ${data.time} seconds!`);
                        updateLeaderboard(data.time);
                    }
                } else {
                    alert('You lost!');
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
                            if (c) {
                                const cell = document.querySelector(`.cell[data-row="${i}"][data-col="${j}"]`);
                                cell.classList.add('flag');
                            } else {
                                const cell = document.querySelector(`.cell[data-row="${i}"][data-col="${j}"]`);
                                cell.classList.remove('flag');
                            }
                        });
                    });
                    minesRemaining = data.minesRemaining;
                    updateMinesRemaining();
                }
            });
        });        

    });

    function updateLeaderboard(time) {
        leaderboardList.innerHTML = '';
        fetch('/')
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const leaderboardItems = doc.querySelectorAll('#leaderboard-list li');
                leaderboardItems.forEach(item => {
                    leaderboardList.appendChild(item.cloneNode(true));
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
        }
    });
}
