// script.js
// Terminal Pyodide - nomes e comentários em pt-br, Tab/ShiftTab, Shift+Backspace apaga linha,
// Enter envia (se bloco completo), Shift+Enter nova linha com indent, histórico, Ctrl+L limpa,
// e dicas iniciais exibidas ao carregar.

document.addEventListener('DOMContentLoaded', () => {
    // elementos DOM
    const areaSaida = document.getElementById('area-saida');
    const entradaComando = document.getElementById('entrada-comando');
    const palavraDigitacao = document.getElementById('palavra-digitacao');

    // ambiente Pyodide
    let ambientePyodide = null;
    let funcaoVerificadorIncompleto = null; // função Python para checar blocos incompletos

    // histórico
    const historicoComandos = [];
    let indiceHistorico = 0;

    // configuração
    const tabString = '    '; // 4 espaços
    const alturaMaximaTextareaPx = Math.floor(window.innerHeight * 0.40); // 40vh aproximado

    // ========== utilitários ==========

    function anexarAoTerminal(texto, tipo = 'info') {
        const p = document.createElement('p');
        switch (tipo) {
            case 'usuario':
                p.innerHTML = `<span class="prompt">></span> ${escapeHtml(texto)}`;
                break;
            case 'python':
                p.style.color = 'var(--result-color)';
                p.textContent = texto.replace(/\n$/, '');
                break;
            case 'resultado':
                p.style.color = 'var(--result-color)';
                p.textContent = texto;
                break;
            case 'erro':
                p.style.color = 'var(--error-color)';
                p.textContent = texto;
                break;
            default:
                p.textContent = texto;
        }
        areaSaida.appendChild(p);
        areaSaida.scrollTop = areaSaida.scrollHeight;
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    function ajustarAlturaTextarea() {
        entradaComando.style.height = 'auto'; // reset
        const alturaConteudo = entradaComando.scrollHeight;
        const alturaAplicada = Math.min(alturaConteudo, alturaMaximaTextareaPx);
        entradaComando.style.height = alturaAplicada + 'px';
        if (alturaConteudo > alturaMaximaTextareaPx) {
            entradaComando.style.overflowY = 'auto';
        } else {
            entradaComando.style.overflowY = 'hidden';
        }
    }

    function calcularIndentAutomatica(textoAteCursor) {
        const linhas = textoAteCursor.split('\n');
        const ultimaLinha = linhas[linhas.length - 1];
        const empacotamento = ultimaLinha.match(/^\s*/);
        let indent = empacotamento ? empacotamento[0] : '';
        if (ultimaLinha.trim().endsWith(':')) indent += tabString;
        return indent;
    }

    // indenta / desindenta seleção (ou insere tab no cursor)
    function ajustarIndentacaoSelecionada(textarea, desempacotamento = false) {
        const inicio = textarea.selectionStart;
        const fim = textarea.selectionEnd;
        const valor = textarea.value;

        if (inicio === fim) {
            if (!desempacotamento) {
                const antes = valor.slice(0, inicio);
                const depois = valor.slice(fim);
                textarea.value = antes + tabString + depois;
                const pos = inicio + tabString.length;
                textarea.setSelectionRange(pos, pos);
            } else {
                const antes = valor.slice(0, inicio);
                const depois = valor.slice(fim);
                if (antes.endsWith(tabString)) {
                    const novoAntes = antes.slice(0, -tabString.length);
                    textarea.value = novoAntes + depois;
                    const pos = inicio - tabString.length;
                    textarea.setSelectionRange(pos, pos);
                } else if (antes.endsWith('\t')) {
                    const novoAntes = antes.slice(0, -1);
                    textarea.value = novoAntes + depois;
                    const pos = inicio - 1;
                    textarea.setSelectionRange(pos, pos);
                }
            }
            ajustarAlturaTextarea();
            return;
        }

        let linhaInicio = valor.lastIndexOf('\n', inicio - 1);
        linhaInicio = linhaInicio === -1 ? 0 : linhaInicio + 1;
        let linhaFim = valor.indexOf('\n', fim);
        linhaFim = linhaFim === -1 ? valor.length : linhaFim;

        const antes = valor.slice(0, linhaInicio);
        const selecao = valor.slice(linhaInicio, linhaFim);
        const depois = valor.slice(linhaFim);

        const linhas = selecao.split('\n');
        let novaSelecao;
        if (!desempacotamento) {
            novaSelecao = linhas.map(l => tabString + l).join('\n');
        } else {
            novaSelecao = linhas.map(l => {
                if (l.startsWith(tabString)) return l.slice(tabString.length);
                if (l.startsWith('\t')) return l.slice(1);
                return l;
            }).join('\n');
        }

        textarea.value = antes + novaSelecao + depois;
        const novoInicio = linhaInicio;
        const novoFim = linhaInicio + novaSelecao.length;
        textarea.setSelectionRange(novoInicio, novoFim);
        ajustarAlturaTextarea();
    }

    // apaga a linha atual (quando Shift+Backspace)
    function apagarLinhaAtual(textarea) {
        const pos = textarea.selectionStart;
        const valor = textarea.value;
        const inicioLinha = valor.lastIndexOf('\n', pos - 1);
        const inicio = inicioLinha === -1 ? 0 : inicioLinha + 1;
        const fimLinhaIndex = valor.indexOf('\n', pos);
        const fim = fimLinhaIndex === -1 ? valor.length : fimLinhaIndex;
        const antes = valor.slice(0, inicio);
        const depois = valor.slice(fim);
        textarea.value = antes + depois;
        const novaPos = inicio;
        textarea.setSelectionRange(novaPos, novaPos);
        ajustarAlturaTextarea();
    }

    // ========== typing header ==========

    const frasesDigitacao = ['Terminal', 'em Python', 'feito', 'para você'];

    async function loopDigitacao(elemento, frases, velocidadeDigitacao = 80, velocidadeApagar = 40, pausaDepoisDigitar = 1200, pausaDepoisApagar = 400) {
        let i = 0;
        elemento.textContent = '';
        while (true) {
            const palavra = frases[i % frases.length];
            for (let j = 1; j <= palavra.length; j++) {
                elemento.textContent = ' ' + palavra.slice(0, j);
                await new Promise(r => setTimeout(r, velocidadeDigitacao));
            }
            await new Promise(r => setTimeout(r, pausaDepoisDigitar));
            for (let j = palavra.length; j >= 0; j--) {
                elemento.textContent = j > 0 ? ' ' + palavra.slice(0, j) : '';
                await new Promise(r => setTimeout(r, velocidadeApagar));
            }
            await new Promise(r => setTimeout(r, pausaDepoisApagar));
            i++;
        }
    }

    loopDigitacao(palavraDigitacao, frasesDigitacao).catch(console.error);

    // ========== integração Pyodide ==========

    // mostra dicas iniciais compactas (uma tela)
    function mostrarDicasIniciais() {
        const dicas = [
            '',
            '💡 Dicas rápidas:',
            '• Enter → executar (se o bloco estiver completo)',
            '• Shift+Enter → nova linha com indent automático',
            '• Tab / Shift+Tab → indentar / desindentar',
            '• Shift+Backspace → apagar linha inteira',
            '• Ctrl+L → limpar terminal',
            '• ↑ / ↓ → histórico de comandos',
            ''
        ];
        // anexa cada linha rapidamente (mantendo espaçamento e emojis)
        dicas.forEach(l => anexarAoTerminal(l));
    }

    async function inicializarAmbiente() {
        try {
            // Mensagem já presente no HTML: "Iniciando sistema..."
            anexarAoTerminal('⏳ Carregando Pyodide (pode levar alguns segundos)...\n\n');

            ambientePyodide = await loadPyodide({
                stdout: (texto) => anexarAoTerminal(texto, 'python'),
                stderr: (texto) => anexarAoTerminal(texto, 'erro')
            });

            // define função Python para detectar blocos incompletos
            await ambientePyodide.runPythonAsync(`
from code import compile_command

def _esta_incompleto(src):
    try:
        return compile_command(src) is None
    except Exception:
        return False
`);

            funcaoVerificadorIncompleto = ambientePyodide.globals.get('_esta_incompleto');

            anexarAoTerminal('✅ Pyodide carregado. Python pronto.\n\n');
            // mostrar dicas compactas logo após carregar
            mostrarDicasIniciais();

            entradaComando.disabled = false;
            entradaComando.placeholder = 'Digite um comando Python e pressione Enter (Shift+Enter -> nova linha)';
            entradaComando.focus();
            ajustarAlturaTextarea();
        } catch (erro) {
            anexarAoTerminal(`Erro crítico ao carregar Pyodide: ${erro}`, 'erro');
            console.error('Erro completo:', erro);
        }
    }

    async function executarBlocoPython(codigo) {
        if (!ambientePyodide) {
            anexarAoTerminal('Ambiente Pyodide ainda não está pronto.', 'erro');
            return;
        }
        try {
            const resultado = await ambientePyodide.runPythonAsync(codigo);
            if (resultado !== undefined && resultado !== null) {
                anexarAoTerminal(String(resultado), 'resultado');
            }
        } catch (erro) {
            anexarAoTerminal(String(erro), 'erro');
        }
    }

    async function verificarSeBlocoEstaIncompleto(codigo) {
        if (!ambientePyodide || !funcaoVerificadorIncompleto) return false;
        try {
            await ambientePyodide.runPythonAsync('_ultimo_incompleto = _esta_incompleto(' + JSON.stringify(codigo) + ')');
            const proxy = ambientePyodide.globals.get('_ultimo_incompleto');
            const ehIncompleto = String(proxy) === 'True';
            return ehIncompleto;
        } catch (e) {
            console.warn('Falha ao verificar incompletude do bloco:', e);
            return false;
        }
    }

    // ========== eventos do textarea ==========

    entradaComando.addEventListener('input', () => ajustarAlturaTextarea());

    entradaComando.addEventListener('keydown', async (evento) => {
        // Ctrl+L -> limpar a tela (sem mensagem de confirmação)
        if (evento.ctrlKey && evento.key.toLowerCase() === 'l') {
            evento.preventDefault();
            areaSaida.innerHTML = '';
            entradaComando.focus();
            return;
        }

        // Tab / Shift+Tab -> indent / unindent
        if (evento.key === 'Tab') {
            evento.preventDefault();
            const desempacotamento = evento.shiftKey === true;
            ajustarIndentacaoSelecionada(entradaComando, desempacotamento);
            return;
        }

        // Shift+Backspace -> apagar linha inteira
        if (evento.key === 'Backspace' && evento.shiftKey) {
            evento.preventDefault();
            apagarLinhaAtual(entradaComando);
            return;
        }

        // histórico (setas)
        if (evento.key === 'ArrowUp' && !evento.shiftKey && !evento.ctrlKey && !evento.altKey) {
            if (historicoComandos.length === 0) return;
            evento.preventDefault();
            if (indiceHistorico > 0) indiceHistorico -= 1;
            entradaComando.value = historicoComandos[indiceHistorico] || '';
            ajustarAlturaTextarea();
            entradaComando.setSelectionRange(entradaComando.value.length, entradaComando.value.length);
            return;
        }
        if (evento.key === 'ArrowDown' && !evento.shiftKey && !evento.ctrlKey && !evento.altKey) {
            if (historicoComandos.length === 0) return;
            evento.preventDefault();
            if (indiceHistorico < historicoComandos.length - 1) {
                indiceHistorico += 1;
                entradaComando.value = historicoComandos[indiceHistorico];
            } else {
                indiceHistorico = historicoComandos.length;
                entradaComando.value = '';
            }
            ajustarAlturaTextarea();
            entradaComando.setSelectionRange(entradaComando.value.length, entradaComando.value.length);
            return;
        }

        // Enter: Shift+Enter => nova linha com indent; Enter => tenta enviar
        if (evento.key === 'Enter') {
            if (evento.shiftKey) {
                evento.preventDefault();
                const inicio = entradaComando.selectionStart;
                const fim = entradaComando.selectionEnd;
                const antes = entradaComando.value.slice(0, inicio);
                const depois = entradaComando.value.slice(fim);
                const indent = calcularIndentAutomatica(antes);
                entradaComando.value = antes + '\n' + indent + depois;
                const novaPos = inicio + 1 + indent.length;
                ajustarAlturaTextarea();
                entradaComando.setSelectionRange(novaPos, novaPos);
                return;
            } else {
                // Enter sem Shift -> enviar se bloco completo
                evento.preventDefault();
                const codigo = entradaComando.value;
                if (!codigo.trim()) return;

                const incompleto = await verificarSeBlocoEstaIncompleto(codigo);
                if (incompleto) {
                    const indent = calcularIndentAutomatica(codigo);
                    entradaComando.value = codigo + '\n' + indent;
                    ajustarAlturaTextarea();
                    entradaComando.focus();
                    entradaComando.setSelectionRange(entradaComando.value.length, entradaComando.value.length);
                    return;
                }

                anexarAoTerminal(codigo, 'usuario');
                if (historicoComandos.length === 0 || historicoComandos[historicoComandos.length - 1] !== codigo) {
                    historicoComandos.push(codigo);
                }
                indiceHistorico = historicoComandos.length;
                await executarBlocoPython(codigo);
                entradaComando.value = '';
                ajustarAlturaTextarea();
                entradaComando.focus();
                return;
            }
        }
    });

    // inicializar Pyodide e interface
    inicializarAmbiente();
});
