const { PythonShell } = require('python-shell');
const { ipcRenderer } = require('electron');
const path = require('path');

const runScriptButton = document.getElementById('runScript');
const stopScriptButton = document.getElementById('stopScript'); // Add this line
const outputElement = document.getElementById('output');

let pyshell;

function getScriptPath(scriptName) {
    return path.join(__dirname, scriptName);
}

function record() {
    pyshell = new PythonShell('record.py');
    pyshell.on('message', (message) => {
        console.log(message);
    });
}

ipcRenderer.on('app-before-quit', () => {
    console.log(pyshell)
  if (pyshell) {
    pyshell.terminate();
  }
});

// Function to run the print_numbers.py script

function runPrintNumbers() {
    outputElement.innerHTML = ''; // Clear the output element
    pyshell = new PythonShell('count.py');
    console.log(pyshell)
    pyshell.on('message', (message) => {
        outputElement.innerHTML += message + '\n';
    });
}

// Function to stop the running PythonShell
function stopScript() {
    if (pyshell) {
        pyshell.terminate()
    }
}

// Run the print_hello.py script when the app starts
record();

// Run the print_numbers.py script when the button is clicked
runScriptButton.addEventListener('click', runPrintNumbers);

// Stop the script when the stop button is clicked
stopScriptButton.addEventListener('click', stopScript); // Add this line
