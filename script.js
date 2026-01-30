function centerElements() {
    // Centralizar todos os botões
    const buttons = document.querySelectorAll('.stButton, .stFormSubmitButton');
    buttons.forEach(button => {
        if (button.parentElement) {
            button.parentElement.style.display = 'flex';
            button.parentElement.style.justifyContent = 'center';
            button.parentElement.style.alignItems = 'center';
            button.parentElement.style.width = '100%';
        }
    });
    
    // Centralizar botão de download específico
    const downloadButtons = document.querySelectorAll('[data-testid="stDownloadButton"]');
    downloadButtons.forEach(button => {
        button.style.display = 'flex';
        button.style.justifyContent = 'center';
        button.style.alignItems = 'center';
        button.style.width = '100%';
        button.style.margin = '0 auto';
        
        // Garantir que o container interno também esteja centralizado
        const innerDiv = button.querySelector('div');
        if (innerDiv) {
            innerDiv.style.display = 'flex';
            innerDiv.style.justifyContent = 'center';
            innerDiv.style.width = '100%';
        }
    });
    
    // Centralizar colunas
    const columns = document.querySelectorAll('.stColumns > div, [data-testid="column"]');
    columns.forEach(col => {
        col.style.display = 'flex';
        col.style.justifyContent = 'center';
        col.style.alignItems = 'center';
        col.style.flexDirection = 'column';
    });
    
    // Mobile adjustments
    if (window.innerWidth <= 768) {
        const inputs = document.querySelectorAll('.stTextInput');
        inputs.forEach(input => { 
            input.style.margin = '0 auto'; 
            input.style.maxWidth = '100%';
        });
    }
}

// Função para centralizar específicamente os botões de download
function centerDownloadButtons() {
    const downloadContainers = document.querySelectorAll('[data-testid="stDownloadButton"]');
    downloadContainers.forEach(container => {
        // Garantir que o container principal esteja centralizado
        container.style.display = 'flex';
        container.style.justifyContent = 'center';
        container.style.alignItems = 'center';
        container.style.width = '100%';
        container.style.margin = '0 auto';
        
        // Garantir que o botão dentro do container esteja centralizado
        const button = container.querySelector('button');
        if (button) {
            button.style.margin = '0 auto';
            button.style.display = 'block';
        }
        
        // Se estiver dentro de uma coluna, centralizar a coluna também
        let parent = container.parentElement;
        while (parent && !parent.classList.contains('stApp')) {
            if (parent.getAttribute('data-testid') === 'column') {
                parent.style.display = 'flex';
                parent.style.justifyContent = 'center';
                parent.style.alignItems = 'center';
            }
            parent = parent.parentElement;
        }
    });
}

// Função para simular clique no botão "VERIFICAR LINK" ao pressionar Enter na URL
function setupEnterKeyForUrl() {
    const urlInput = document.querySelector('input[placeholder="Cole o link da mídia aqui..."]');
    if (urlInput) {
        urlInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.ctrlKey) {
                e.preventDefault();
                // Encontrar o botão "VERIFICAR LINK" e clicar nele
                const buttons = document.querySelectorAll('.stButton button, .stFormSubmitButton button');
                for (let btn of buttons) {
                    if (btn.textContent.includes('VERIFICAR LINK')) {
                        btn.click();
                        break;
                    }
                }
            }
        });
    }
}

// Função para navegação entre campos do formulário de feedback
function setupFeedbackFormNavigation() {
    // Só aplicar se o formulário de feedback estiver aberto
    const form = document.querySelector('form[aria-label="report_form"]');
    if (!form) return;
    
    // Campo de e-mail - ao pressionar Enter, focar no textarea
    const emailInput = document.querySelector('input[placeholder="Contato..."]');
    if (emailInput) {
        emailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.ctrlKey) {
                e.preventDefault();
                // Focar no textarea de detalhes
                const textarea = document.querySelector('textarea[placeholder="Ex: O vídeo baixou sem áudio..."]');
                if (textarea) {
                    textarea.focus();
                }
            }
        });
    }
    
    // Textarea de detalhes - Ctrl+Enter para enviar
    const textarea = document.querySelector('textarea[placeholder="Ex: O vídeo baixou sem áudio..."]');
    if (textarea) {
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                // Encontrar o botão "Enviar Reporte" e clicar
                const submitButtons = document.querySelectorAll('.stFormSubmitButton button, form button[type="submit"]');
                for (let btn of submitButtons) {
                    if (btn.textContent.includes('Enviar Reporte')) {
                        btn.click();
                        break;
                    }
                }
            }
        });
        
        // Adicionar dica visual sobre Ctrl+Enter
        if (!document.querySelector('.ctrl-enter-hint')) {
            const hint = document.createElement('div');
            hint.className = 'ctrl-enter-hint';
            hint.style.color = 'rgba(255,255,255,0.5)';
            hint.style.fontSize = '12px';
            hint.style.marginTop = '5px';
            hint.style.textAlign = 'center';
            hint.textContent = 'Dica: Pressione Ctrl+Enter para enviar';
            
            const textareaContainer = textarea.closest('.stTextArea');
            if (textareaContainer) {
                textareaContainer.appendChild(hint);
            }
        }
    }
}

// Inicializar todas as funcionalidades
function initializeAll() {
    centerElements();
    centerDownloadButtons();
    setupEnterKeyForUrl();
    setupFeedbackFormNavigation();
}

// Event listeners
window.addEventListener('load', initializeAll);
window.addEventListener('resize', function() {
    centerElements();
    centerDownloadButtons();
});
window.addEventListener('DOMContentLoaded', initializeAll);

// Verificar periodicamente para garantir centralização e funcionalidade
setInterval(initializeAll, 500);

// Observar mudanças no DOM para detectar quando o formulário de feedback é aberto/fechado
const observer = new MutationObserver(function(mutations) {
    setupEnterKeyForUrl();
    setupFeedbackFormNavigation();
});

observer.observe(document.body, { childList: true, subtree: true });