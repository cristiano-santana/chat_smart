const loadingOverlay = document.getElementById('loadingOverlay');
const enviarBtn = document.getElementById('enviarBtn');
const perguntaTextarea = document.getElementById('pergunta');
const downloadContainer = document.getElementById('downloadContainer');
const resultadosDiv = document.getElementById('resultados');
const queryPre = document.getElementById('query');
const feedbackContainer = document.getElementById('feedbackContainer');
const feedbackMessage = document.getElementById('feedbackMessage');

async function enviarPergunta() {
    const pergunta = perguntaTextarea.value;

    if (!pergunta.trim()) {
        queryPre.innerText = "";
        resultadosDiv.innerHTML = '<div class="error">⚠️ Digite uma pergunta antes de enviar!</div>';
        downloadContainer.style.display = "none";
        feedbackContainer.style.display = "none";
        return;
    }

    // Mostrar loading e desabilitar o botão
    loadingOverlay.classList.add('active');
    enviarBtn.disabled = true;
    feedbackContainer.style.display = "none";
    feedbackMessage.innerText = "";

    try {
        const response = await fetch('/pergunta', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ pergunta }),
        });

        const data = await response.json();

        if (data.erro) {
            queryPre.innerText = "";
            resultadosDiv.innerHTML = `<div class="error">⚠️ ${data.erro}</div>`;
            downloadContainer.style.display = "none";
            feedbackContainer.style.display = "none";
        } else {
            queryPre.innerText = data.tabelas.map(t => t.query)
                .join("\n-------------------------------\n");

            let html = "";
            data.tabelas.forEach((item, index) => {
                html += `<h2>Resposta parte ${index + 1}:</h2>`;
                html += item.tabela_html;
                html += "<hr />";
            });

            resultadosDiv.innerHTML = html;
            downloadContainer.style.display = "block";
            feedbackContainer.style.display = "block";
        }
    } catch (error) {
        queryPre.innerText = "";
        resultadosDiv.innerHTML = `<div class="error">⚠️ Erro ao comunicar com o servidor: ${error.message}</div>`;
        downloadContainer.style.display = "none";
        feedbackContainer.style.display = "none";
    } finally {
        // Esconder loading e reabilitar o botão
        loadingOverlay.classList.remove('active');
        enviarBtn.disabled = false;
    }
}

function baixarExcel() {
    const tabelas = resultadosDiv.querySelectorAll("table");

    if (tabelas.length === 0) {
        alert("⚠️ Nenhum resultado para baixar!");
        return;
    }

    const wb = XLSX.utils.book_new();

    tabelas.forEach((tabela, index) => {
        const ws = XLSX.utils.table_to_sheet(tabela);
        XLSX.utils.book_append_sheet(wb, ws, `Resultados ${index + 1}`);
    });

    XLSX.writeFile(wb, "resultado.xlsx");
}

// Permitir enviar a pergunta ao pressionar 'Enter' na textarea
perguntaTextarea.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) { // Shift+Enter para nova linha
        event.preventDefault(); // Evita a nova linha padrão
        enviarBtn.click(); // Simula o clique no botão "Consultar"
    }
});

function enviarFeedback(avaliacao) {
    // Aqui você pode enviar a avaliação para o servidor ou fazer algo com ela
    console.log(`Feedback do usuário: ${avaliacao}`);
    feedbackMessage.innerText = "Obrigado pelo seu feedback!";
    // Desabilitar os botões de feedback após o envio (opcional)
    document.querySelectorAll('.feedback-btn').forEach(btn => btn.disabled = true);
}