let userUuid = null;
let gameUuid = null;
let currentGame = null;
let board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
let login = "";
let password = "";
let refreshTimer = null;
let lastMoveKey = null;

const statusElement = document.getElementById("status");
const boardElement = document.getElementById("board");
const loginInput = document.getElementById("login");
const passwordInput = document.getElementById("password");
const userBadge = document.getElementById("userBadge");
const gameInfoElement = document.getElementById("gameInfo");
const availableGamesElement = document.getElementById("availableGames");
const myGamesElement = document.getElementById("myGames");
const gameUuidInput = document.getElementById("gameUuidInput");

function authHeader() {
    return "Basic " + btoa(`${login}:${password}`);
}

function shortUuid(value) {
    if (!value) {
        return "—";
    }
    if (value === "COMPUTER") {
        return "Компьютер";
    }
    return `${value.slice(0, 8)}…${value.slice(-4)}`;
}

function setStatus(text, type = "normal") {
    statusElement.textContent = text;
    statusElement.classList.remove("good", "error");
    if (type === "good") {
        statusElement.classList.add("good");
    }
    if (type === "error") {
        statusElement.classList.add("error");
    }
}

function saveAuthToStorage() {
    localStorage.setItem("ttt_login", login);
    localStorage.setItem("ttt_password", password);
    localStorage.setItem("ttt_user_uuid", userUuid || "");
}

function loadAuthFromStorage() {
    login = localStorage.getItem("ttt_login") || "";
    password = localStorage.getItem("ttt_password") || "";
    userUuid = localStorage.getItem("ttt_user_uuid") || null;
    loginInput.value = login;
    passwordInput.value = password;
    updateUserBadge();
}

function updateUserBadge() {
    if (!userUuid) {
        userBadge.textContent = "Гость";
        return;
    }
    userBadge.textContent = `${login} · ${shortUuid(userUuid)}`;
}

function getMyMark(game = currentGame) {
    if (!game || !userUuid) {
        return null;
    }
    if (game.players?.X === userUuid) {
        return 1;
    }
    if (game.players?.O === userUuid) {
        return 2;
    }
    return null;
}

function getMarkName(mark) {
    if (mark === 1) {
        return "X";
    }
    if (mark === 2) {
        return "O";
    }
    return "—";
}

function canMove() {
    return Boolean(
        currentGame &&
        userUuid &&
        currentGame.status === "TURN" &&
        currentGame.currentTurnUserUuid === userUuid &&
        getMyMark() !== null
    );
}

function renderBoard() {
    boardElement.innerHTML = "";
    const allowMove = canMove();

    for (let row = 0; row < 3; row++) {
        for (let column = 0; column < 3; column++) {
            const button = document.createElement("button");
            button.className = "cell";

            if (board[row][column] === 1) {
                button.textContent = "X";
                button.classList.add("x");
            } else if (board[row][column] === 2) {
                button.textContent = "O";
                button.classList.add("o");
            }

            if (lastMoveKey === `${row}:${column}`) {
                button.classList.add("last-move");
            }

            button.disabled = !allowMove || board[row][column] !== 0;
            button.addEventListener("click", () => makeMove(row, column));
            boardElement.appendChild(button);
        }
    }
}

function renderGameInfo() {
    if (!currentGame) {
        gameInfoElement.classList.add("hidden");
        gameInfoElement.innerHTML = "";
        return;
    }

    gameInfoElement.classList.remove("hidden");
    gameInfoElement.innerHTML = `
        <div class="info-item">
            <span class="info-label">UUID игры</span>
            <span class="info-value">${currentGame.uuid}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Режим</span>
            <span class="info-value">${currentGame.mode === "USER" ? "2 игрока" : "Компьютер"}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Твой знак</span>
            <span class="info-value">${getMarkName(getMyMark())}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Состояние</span>
            <span class="info-value">${statusToText(currentGame.status)}</span>
        </div>
    `;
}

function statusToText(status) {
    const map = {
        WAITING_PLAYERS: "Ожидание игрока",
        TURN: "Идёт игра",
        DRAW: "Ничья",
        WIN: "Победа",
    };
    return map[status] || status;
}

function setGameStatusText(game) {
    const myMark = getMyMark(game);

    if (game.status === "WIN") {
        if (game.winnerUserUuid === userUuid) {
            setStatus("Игра завершена. Ты победил.", "good");
        } else if (game.winnerUserUuid === "COMPUTER") {
            setStatus("Игра завершена. Победил компьютер.");
        } else {
            setStatus(`Игра завершена. Победитель: ${shortUuid(game.winnerUserUuid)}.`);
        }
        return;
    }

    if (game.status === "DRAW") {
        setStatus("Игра завершена. Ничья.", "good");
        return;
    }

    if (game.status === "WAITING_PLAYERS") {
        setStatus(`Игра создана. Ждём второго игрока. UUID: ${game.uuid}`);
        return;
    }

    if (game.currentTurnUserUuid === userUuid) {
        setStatus(`Твой ход. Ты играешь за ${getMarkName(myMark)}.`, "good");
    } else {
        setStatus(`Сейчас ход другого игрока: ${shortUuid(game.currentTurnUserUuid)}.`);
    }
}

async function requestJson(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.error || "Ошибка запроса");
    }
    return data;
}

async function signup() {
    login = loginInput.value.trim();
    password = passwordInput.value;

    if (!login || !password) {
        setStatus("Введи логин и пароль.", "error");
        return;
    }

    const data = await requestJson("/auth/signup", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({login, password}),
    });

    setStatus(data.success ? "Пользователь зарегистрирован. Теперь нажми Войти." : "Не удалось зарегистрироваться", "good");
}

async function signin() {
    login = loginInput.value.trim();
    password = passwordInput.value;

    if (!login || !password) {
        setStatus("Введи логин и пароль.", "error");
        return;
    }

    const data = await requestJson("/auth/login", {
        method: "POST",
        headers: {"Authorization": authHeader()},
    });

    userUuid = data.uuid;
    saveAuthToStorage();
    updateUserBadge();
    setStatus(`Вход выполнен. UUID пользователя: ${userUuid}`, "good");
    await refreshLists();
    startAutoRefresh();
}

async function createGame(mode) {
    if (!userUuid) {
        setStatus("Сначала войди.", "error");
        return;
    }

    const data = await requestJson("/games", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Authorization": authHeader()},
        body: JSON.stringify({mode}),
    });

    applyGame(data);
    await refreshLists();
}

async function joinGame(joinGameUuid) {
    if (!userUuid) {
        setStatus("Сначала войди.", "error");
        return;
    }

    const data = await requestJson(`/games/${joinGameUuid}/join`, {
        method: "POST",
        headers: {"Authorization": authHeader()},
    });

    applyGame(data);
    await refreshLists();
}

async function openGame(openGameUuid) {
    const id = (openGameUuid || gameUuidInput.value || "").trim();
    if (!id) {
        setStatus("Введи UUID игры.", "error");
        return;
    }

    const data = await requestJson(`/games/${id}`, {
        method: "GET",
        headers: {"Authorization": authHeader()},
    });

    applyGame(data);
}

async function makeMove(row, column) {
    if (!gameUuid || !currentGame) {
        setStatus("Сначала создай или открой игру.", "error");
        return;
    }

    const myMark = getMyMark();
    if (myMark === null) {
        setStatus("Ты не участник этой игры.", "error");
        return;
    }

    if (!canMove()) {
        setStatus("Сейчас не твой ход.", "error");
        return;
    }

    if (board[row][column] !== 0) {
        return;
    }

    const nextBoard = board.map(line => line.slice());
    nextBoard[row][column] = myMark;
    lastMoveKey = `${row}:${column}`;

    try {
        const data = await requestJson(`/games/${gameUuid}`, {
            method: "POST",
            headers: {"Content-Type": "application/json", "Authorization": authHeader()},
            body: JSON.stringify({board: nextBoard}),
        });
        applyGame(data);
        await refreshLists();
    } catch (error) {
        setStatus(error.message, "error");
    }
}

function applyGame(game) {
    currentGame = game;
    gameUuid = game.uuid;
    board = game.board;
    gameUuidInput.value = game.uuid;
    renderGameInfo();
    renderBoard();
    setGameStatusText(game);
    startAutoRefresh();
}

async function refreshCurrentGame() {
    if (!gameUuid || !userUuid) {
        return;
    }

    try {
        const data = await requestJson(`/games/${gameUuid}`, {
            method: "GET",
            headers: {"Authorization": authHeader()},
        });
        currentGame = data;
        board = data.board;
        renderGameInfo();
        renderBoard();
        setGameStatusText(data);
    } catch (error) {
        // Не спамим ошибками при автообновлении, но если игра открыта — покажем одну понятную ошибку.
        setStatus(error.message, "error");
    }
}

async function refreshLists() {
    if (!userUuid) {
        availableGamesElement.textContent = "Войди, чтобы увидеть список.";
        myGamesElement.textContent = "Войди, чтобы увидеть список.";
        availableGamesElement.classList.add("empty-list");
        myGamesElement.classList.add("empty-list");
        return;
    }

    try {
        const [availableData, myData] = await Promise.all([
            requestJson("/games/available", {
                method: "GET",
                headers: {"Authorization": authHeader()},
            }),
            requestJson("/games/my", {
                method: "GET",
                headers: {"Authorization": authHeader()},
            }),
        ]);

        renderGameList(availableGamesElement, availableData.games || [], "available");
        renderGameList(myGamesElement, myData.games || [], "my");
    } catch (error) {
        setStatus(error.message, "error");
    }
}

function renderGameList(container, games, type) {
    container.innerHTML = "";

    if (!games.length) {
        container.classList.add("empty-list");
        container.textContent = type === "available" ? "Нет доступных игр." : "У тебя пока нет игр.";
        return;
    }

    container.classList.remove("empty-list");

    games.forEach(game => {
        const item = document.createElement("div");
        item.className = "game-list-item";

        const title = document.createElement("div");
        title.className = "game-list-title";
        title.textContent = game.uuid;

        const meta = document.createElement("div");
        meta.className = "game-list-meta";
        meta.innerHTML = `
            Режим: ${game.mode === "USER" ? "2 игрока" : "Компьютер"}<br>
            Статус: ${statusToText(game.status)}<br>
            X: ${shortUuid(game.players?.X)}<br>
            O: ${shortUuid(game.players?.O)}<br>
            Ход: ${shortUuid(game.currentTurnUserUuid)}
        `;

        const actions = document.createElement("div");
        actions.className = "game-list-actions";

        const openButton = document.createElement("button");
        openButton.className = "secondary small";
        openButton.textContent = "Открыть";
        openButton.addEventListener("click", () => openGame(game.uuid).catch(error => setStatus(error.message, "error")));
        actions.appendChild(openButton);

        if (type === "available") {
            const joinButton = document.createElement("button");
            joinButton.className = "small";
            joinButton.textContent = "Присоединиться";
            joinButton.addEventListener("click", () => joinGame(game.uuid).catch(error => setStatus(error.message, "error")));
            actions.appendChild(joinButton);
        }

        item.append(title, meta, actions);
        container.appendChild(item);
    });
}

function startAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }

    refreshTimer = setInterval(async () => {
        if (!userUuid) {
            return;
        }
        await refreshLists();
        await refreshCurrentGame();
    }, 2000);
}

document.getElementById("signupButton").addEventListener("click", () => signup().catch(error => setStatus(error.message, "error")));
document.getElementById("loginButton").addEventListener("click", () => signin().catch(error => setStatus(error.message, "error")));
document.getElementById("newComputerGameButton").addEventListener("click", () => createGame("COMPUTER").catch(error => setStatus(error.message, "error")));
document.getElementById("newUserGameButton").addEventListener("click", () => createGame("USER").catch(error => setStatus(error.message, "error")));
document.getElementById("refreshButton").addEventListener("click", () => refreshLists().catch(error => setStatus(error.message, "error")));
document.getElementById("openGameButton").addEventListener("click", () => openGame().catch(error => setStatus(error.message, "error")));

loadAuthFromStorage();
renderBoard();
renderGameInfo();

if (userUuid && login && password) {
    setStatus("Данные входа восстановлены из браузера. Можно играть.", "good");
    refreshLists().catch(error => setStatus(error.message, "error"));
    startAutoRefresh();
}
