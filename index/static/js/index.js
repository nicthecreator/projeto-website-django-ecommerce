let quantidadeNoCarrinho = 0;

function adicionarAoCarrinho() {
    quantidadeNoCarrinho++;
    
    const contadorElemento = document.getElementById('cart-count');
    const iconeCarrinho = document.getElementById('cart-btn');
    
    // Feedback visual rápido
    iconeCarrinho.style.color = '#e63946';
    contadorElemento.style.fontWeight = 'bold';
    contadorElemento.style.transform = 'scale(1.2)';
    contadorElemento.style.display = 'inline-block';
    
    // Atualiza o valor na interface
    setTimeout(() => {
        contadorElemento.innerText = quantidadeNoCarrinho;
        
        // Retorna ao estilo original
        setTimeout(() => {
            iconeCarrinho.style.color = 'white';
            contadorElemento.style.transform = 'scale(1)';
        }, 300);
    }, 150);
}

