document.addEventListener('DOMContentLoaded', () => {
    const outputArea = document.getElementById('output-area');
    const commandInput = document.getElementById('command-input');

    let pyodide;

    function appendToTerminal(message, type = 'info') {
        const p = document.createElement('p');
        switch (type) {
            case 'user':
                p.innerHTML = `<span class="prompt">></span> ${message}`;
                break;
            
            // ########## ALTERAÇÃO AQUI ##########
            // Agora, a saída do 'print' (tipo 'python') também usa a cor de resultado (branca).
            case 'python':
                p.style.color = 'var(--result-color)'; // <-- LINHA MODIFICADA
                p.textContent = message.replace(/\n$/, '');
                break;
            // #####################################

            case 'result':
                p.style.color = 'var(--result-color)';
                p.textContent = message;
                break;
            case 'error':
                p.style.color = 'var(--error-color)';
                p.textContent = message;
                break;
            default: // info
                p.textContent = message;
        }
        outputArea.appendChild(p);
        outputArea.scrollTop = outputArea.scrollHeight;
    }

    const originalConsoleLog = console.log;
    console.log = (...args) => {
        originalConsoleLog(...args);
        appendToTerminal(args.join(' '), 'info');
    };

    appendToTerminal("Carregando Pyodide (pode levar alguns segundos)...");

    async function main() {
        try {
            pyodide = await loadPyodide({
                stdout: (text) => appendToTerminal(text, 'python'),
                stderr: (text) => appendToTerminal(text, 'error')
            });

            appendToTerminal("Pyodide carregado. Python 3 está pronto.");
            
            commandInput.disabled = false;
            commandInput.placeholder = "Digite um comando Python e pressione Enter";
            commandInput.focus();

        } catch (error) {
            appendToTerminal(`Erro crítico ao carregar Pyodide: ${error}`, 'error');
            console.error("Erro completo:", error);
        }
    }

    async function executePythonCommand(command) {
        if (!pyodide) {
            appendToTerminal("Pyodide ainda não está pronto.", 'error');
            return;
        }
        try {
            let result = await pyodide.runPythonAsync(command);
            if (result !== undefined) {
                appendToTerminal(String(result), 'result');
            }
        } catch (error) {
            appendToTerminal(error, 'error');
        }
    }
    
    commandInput.addEventListener('keydown', async (event) => {
        if (event.key === 'Enter') {
            const command = commandInput.value.trim();
            if (command) {
                appendToTerminal(command, 'user');
                await executePythonCommand(command);
                commandInput.value = '';
            }
        }
    });

    main();
});