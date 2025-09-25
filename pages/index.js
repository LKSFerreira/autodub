// /pages/index.js
// Renderiza o conteúdo de ./pyodide/index.html (com style/script inlines) dentro de um iframe
// sem mover arquivos. Leitura dos arquivos é feita no servidor (getServerSideProps).

import fs from 'fs';
import path from 'path';
import { SpeedInsights } from "@vercel/speed-insights/next";
import { Analytics } from "@vercel/analytics/next"

export async function getServerSideProps() {
  const pastaPyodide = path.join(process.cwd(), 'pyodide');

  try {
    // lê os arquivos do disco (rodando no servidor)
    const arquivoHtml = fs.readFileSync(path.join(pastaPyodide, 'index.html'), 'utf8');
    const arquivoCss = fs.readFileSync(path.join(pastaPyodide, 'style.css'), 'utf8');
    const arquivoJs = fs.readFileSync(path.join(pastaPyodide, 'script.js'), 'utf8');

    // substitui a referência ao CSS por um <style> inline
    // (procura por href="style.css" ou href='style.css' para maior robustez)
    let htmlComInlines = arquivoHtml.replace(
      /<link[^>]*href=(["'])style\.css\1[^>]*>/i,
      `<style>\n${arquivoCss}\n</style>`
    );

    // substitui a referência ao script local por um script inline
    // (procura por <script src="script.js"></script>)
    htmlComInlines = htmlComInlines.replace(
      /<script[^>]*src=(["'])script\.js\1[^>]*>\s*<\/script>/i,
      `<script>\n${arquivoJs}\n</script>`
    );

    // OBS: se o index.html já carrega pyodide via CDN (<script src="https://...pyodide.js">),
    // o replace acima não toca nessa tag — ela continuará presente no documento e será carregada
    // normalmente dentro do iframe.

    return {
      props: {
        srcDoc: htmlComInlines
      }
    };
  } catch (erro) {
    // retorna erro para debug na página
    return {
      props: {
        erro: String(erro)
      }
    };
  }
}

export default function Home({ srcDoc, erro }) {
  // Se houve erro ao ler os arquivos, mostra a mensagem
  if (erro) {
    return (
      <>
        <main style={{ padding: 20, fontFamily: 'ui-monospace, SFMono-Regular, monospace' }}>
          <h2>Erro ao carregar os arquivos do diretório <code>pyodide</code></h2>
          <pre style={{ whiteSpace: 'pre-wrap', color: 'crimson' }}>{erro}</pre>
          <p>Verifique se a pasta <code>./pyodide</code> existe e contém index.html, style.css e script.js.</p>
        </main>
        <footer>
          <SpeedInsights />
          <Analytics />
        </footer>
      </>
    );
  }

  // Renderiza um iframe que carrega o HTML gerado (srcDoc)
  // configuramos sandbox para permitir scripts e mesmo-origem (necessário para Pyodide CDN executar)
  // ajuste estilos conforme necessário
  return (
    <div style={{ width: '100%', height: '100vh', margin: 0, padding: 0 }}>
      <iframe
        title="Pyodide Terminal"
        srcDoc={srcDoc}
        style={{ width: '100%', height: '100%', border: '0' }}
        sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
      />
    </div>
  );
}
