const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
    });

    mainWindow.loadFile('index.html');
}
function stopScript() {
    if (pyshell) {
        pyshell.terminate()
    }
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});



app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        // stopScript()
        app.quit();
    }
});

app.on('before-quit', () => {
  const mainWindow = BrowserWindow.getAllWindows()[0];
  if (mainWindow) {
    mainWindow.webContents.send('app-before-quit');
  }
});