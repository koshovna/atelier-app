const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let loginWindow;
let mainWindow;

function createLoginWindow() {
    loginWindow = new BrowserWindow({
        width: 570,
        height: 620,
        icon: path.join(__dirname, 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        resizable: false,
        center: true
    });

    loginWindow.loadFile('login.html');
    loginWindow.setMenuBarVisibility(false);

    loginWindow.on('closed', () => {
        loginWindow = null;
    });
}

function createMainWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        icon: path.join(__dirname, 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        show: false
    });

    mainWindow.loadFile('index.html');
    mainWindow.setMenuBarVisibility(false);

    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        if (loginWindow) {
            loginWindow.close();
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
        createLoginWindow();
    });
}

// Обработчик для открытия главного окна
ipcMain.on('open-main-window', () => {
    createMainWindow();
});

// Обработчик для закрытия окна
ipcMain.on('close-window', () => {
    if (mainWindow) {
        mainWindow.close();
    }
});

app.on('ready', createLoginWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (loginWindow === null) {
        createLoginWindow();
    }
});
