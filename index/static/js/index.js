document.addEventListener('DOMContentLoaded', () => {
    atualizarContadorCarrinho();
    
    // Lógica do Menu Hambúrguer (Mobile)
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navActions = document.getElementById('navActions');
    
    if (mobileMenuBtn && navActions) {
        mobileMenuBtn.addEventListener('click', () => {
            navActions.classList.toggle('active');
        });
    }

    // Lógica da barra lateral do carrinho
    const cartBtn = document.getElementById('cart-btn');
    const closeCartBtn = document.getElementById('close-cart-btn');
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartOverlay = document.getElementById('cart-overlay');
    
    if (cartBtn && cartSidebar && cartOverlay && closeCartBtn) {
        cartBtn.addEventListener('click', (e) => {
            e.preventDefault();
            abrirCarrinho();
        });
        
        closeCartBtn.addEventListener('click', fecharCarrinho);
        cartOverlay.addEventListener('click', fecharCarrinho);
    }
});

function abrirCarrinho() {
    document.getElementById('cart-sidebar').classList.add('open');
    document.getElementById('cart-overlay').classList.add('open');
    renderizarItensCarrinho();
}

function fecharCarrinho() {
    document.getElementById('cart-sidebar').classList.remove('open');
    document.getElementById('cart-overlay').classList.remove('open');
}

function renderizarItensCarrinho() {
    const container = document.getElementById('cart-items-container');
    const totalElement = document.getElementById('cart-total-price');
    if (!container || !totalElement) return;
    
    let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    container.innerHTML = '';
    
    if (carrinho.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:#999; margin-top: 2rem;">Seu carrinho está vazio.</p>';
        totalElement.innerText = 'R$ 0,00';
        return;
    }
    
    let total = 0;
    
    carrinho.forEach((item, index) => {
        total += item.preco * item.quantidade;
        
        const itemHtml = `
            <div class="cart-item">
                <img src="${item.imagem}" alt="${item.nome}">
                <div class="cart-item-details">
                    <h4>${item.nome}</h4>
                    <div class="cart-item-price">R$ ${item.preco.toFixed(2).replace('.', ',')}</div>
                    <div class="cart-item-actions">
                        <button onclick="alterarQuantidade(${index}, -1)">-</button>
                        <span>${item.quantidade}</span>
                        <button onclick="alterarQuantidade(${index}, 1)">+</button>
                    </div>
                </div>
                <button class="btn-remover" onclick="removerDoCarrinho(${index})"><i class="fa-solid fa-trash"></i></button>
            </div>
        `;
        container.innerHTML += itemHtml;
    });
    
    totalElement.innerText = `R$ ${total.toFixed(2).replace('.', ',')}`;
}

async function alterarQuantidade(index, mudanca) {
    let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    if (carrinho[index]) {
        let qtdFutura = carrinho[index].quantidade + mudanca;
        
        if (mudanca > 0) {
            try {
                const csrfToken = getCookie('csrftoken');
                const response = await fetch('/verificar-limite/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        produto_id: carrinho[index].id,
                        quantidade: qtdFutura
                    })
                });
                
                const data = await response.json();
                
                if (!data.success) {
                    if (typeof showErrorModal === 'function') {
                        showErrorModal(data.message);
                    } else {
                        alert(data.message);
                    }
                    return; // aborta o incremento
                }
            } catch (e) {
                console.error('Erro na verificação de limite:', e);
                return;
            }
        }

        carrinho[index].quantidade = qtdFutura;
        if (carrinho[index].quantidade <= 0) {
            carrinho.splice(index, 1);
        }
        localStorage.setItem('carrinho', JSON.stringify(carrinho));
        renderizarItensCarrinho();
        atualizarContadorCarrinho();
    }
}

function removerDoCarrinho(index) {
    let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    carrinho.splice(index, 1);
    localStorage.setItem('carrinho', JSON.stringify(carrinho));
    renderizarItensCarrinho();
    atualizarContadorCarrinho();
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function adicionarAoCarrinho(id, nome, precoFormatado, imagem) {
    let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    let itemExistente = carrinho.find(item => item.id === id || item.nome === nome);
    let qtdFutura = itemExistente ? itemExistente.quantidade + 1 : 1;

    try {
        const csrfToken = getCookie('csrftoken');
        const response = await fetch('/verificar-limite/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                produto_id: id,
                quantidade: qtdFutura
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            if (typeof showErrorModal === 'function') {
                showErrorModal(data.message);
            } else {
                alert(data.message);
            }
            return;
        }
    } catch (e) {
        console.error('Erro na verificação de limite:', e);
        return;
    }

    if (itemExistente) {
        itemExistente.quantidade++;
    } else {
        // Converte o formato do Django "99,90" para "99.90" em JavaScript
        let precoFloat = parseFloat(precoFormatado.replace(',', '.'));
        carrinho.push({ id: id, nome: nome, preco: precoFloat, imagem: imagem, quantidade: 1 });
    }

    localStorage.setItem('carrinho', JSON.stringify(carrinho));
    atualizarContadorCarrinho();

    // Mantém a sua animação visual no ícone do carrinho
    const contadorElemento = document.getElementById('cart-count');
    const iconeCarrinho = document.getElementById('cart-btn');

    if (iconeCarrinho && contadorElemento) {
        iconeCarrinho.style.color = '#e63946';
        contadorElemento.style.fontWeight = 'bold';
        contadorElemento.style.transform = 'scale(1.2)';

        setTimeout(() => {
            iconeCarrinho.style.color = 'white';
            contadorElemento.style.transform = 'scale(1)';
        }, 300);
    }
}

function atualizarContadorCarrinho() {
    let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    let totalItens = carrinho.reduce((total, item) => total + item.quantidade, 0);
    const contadorElemento = document.getElementById('cart-count');
    if (contadorElemento) {
        contadorElemento.innerText = totalItens;
    }
    
    // Atualiza também os botões flutuantes (se existirem)
    document.querySelectorAll('.floating-count').forEach(el => {
        el.innerText = totalItens;
    });
}