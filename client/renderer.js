const {PythonShell} = require('python-shell');
const {ipcRenderer} = require('electron');
const path = require('path');
const {ChromaClient} = require('chromadb');
const {CohereEmbeddingFunction} = require('chromadb');

require('dotenv').config();

const embedder = new CohereEmbeddingFunction(process.env.CO_API_KEY);

// For the Python Scripts (to run and to stop)
const runScriptButton = document.getElementById('runScript');
const stopScriptButton = document.getElementById('stopScript');

// Database output
const outputElement = document.getElementById('output_database');
let pyshell;

// Connects to Docker when loaded
const client = new ChromaClient("http://localhost:8000");

async function addToCollection() {
    outputElement.innerHTML = ""

    const addText = document.getElementById('addToDatabase').value;

    let collection = await client.getOrCreateCollection("testing_db", undefined, embedder)
    // const text_embedding = await embedder.generate(["I love water"])
    // console.log(text_embedding[0])
    const now = new Date();

    let addToTheCollection = await collection.add(
        [now],
        undefined,
        undefined,
        [addText])

    console.log(addToTheCollection)
    outputElement.innerHTML += addToTheCollection + '\n';

}

function record() {
    pyshell = new PythonShell('record.py');
    pyshell.on('message', (message) => {
        console.log(message);
    });
}

async function fetchAll() {
    outputElement.innerHTML = ''

    let collection = await client.getOrCreateCollection("testing_db", undefined, embedder)

    results = await collection.get()
    console.log(results);
    outputElement.innerHTML += results.documents + '\n'
}

async function resetDatabase() {
    outputElement.innerHTML = ''
    results = await client.reset()
    console.log(results);
    outputElement.innerHTML += "Database is reset" + '\n'
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

async function queryCollection(collection) {
    outputElement.innerHTML = ''

    const queryText = document.getElementById('queryText').value;
    if (!queryText) {
        alert('Please enter a query text.');
        return;
    }
    const text_embedding = await embedder.generate([queryText])
    console.log(text_embedding)
    const results = await collection.query(
        [text_embedding[0]],
        1,
        undefined,
        [queryText],
    )

    console.log(results);
    outputElement.innerHTML += results.distances + '\n';
    outputElement.innerHTML += results.documents + '\n';


}

// record();

runScriptButton.addEventListener('click', addToCollection);

// Stop the script when the stop button is clicked
stopScriptButton.addEventListener('click', stopScript);


document.getElementById('queryBtn').addEventListener('click', async () => {
    let collection = await client.getOrCreateCollection("testing_db", undefined, embedder)
    if (collection) {
        await queryCollection(collection);
    }
});

document.getElementById('addDB').addEventListener('click', async () => {
    let collection = await client.getOrCreateCollection("testing_db", undefined, embedder)
    if (collection) {
        await addToCollection();
    }
});

document.getElementById('fetchAll').addEventListener('click', async () => {
    let collection = await client.getOrCreateCollection("testing_db", undefined, embedder)
    if (collection) {
        await fetchAll();
    }
});

document.getElementById('reset').addEventListener('click', async () => {
    let collection = await client.getOrCreateCollection("testing_db", undefined, embedder)
    if (collection) {
        await resetDatabase();
    }
});