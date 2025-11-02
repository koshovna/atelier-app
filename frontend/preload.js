const { contextBridge, ipcRenderer } = require('electron');

// Безопасно передаем API в рендер-процесс
contextBridge.exposeInMainWorld('electronAPI', {
    openMainWindow: () => ipcRenderer.send('open-main-window'),
    closeWindow: () => ipcRenderer.send('close-window')
});
