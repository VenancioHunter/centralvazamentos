// formatarValor.js

function formatarValor(input) {
    // Remove tudo que não for dígito
    let valor = input.value.replace(/\D/g, '');

    // Limita o valor ao menos a 3 dígitos (2 para decimais)
    valor = valor.padStart(3, "0");

    // Mantém as últimas 2 casas para as decimais
    const parteInteira = valor.slice(0, -2).replace(/^0+(?=\d)/, ""); // Remove zeros extras à esquerda
    const parteDecimal = valor.slice(-2);

    // Formata parte inteira com pontos como separador de milhar
    const parteInteiraFormatada = parteInteira.replace(/\B(?=(\d{3})+(?!\d))/g, ".");

    // Atualiza o valor no campo de entrada
    input.value = `${parteInteiraFormatada},${parteDecimal}`;
}

function configurarFormatacaoValor(inputId) {
    const inputValor = document.getElementById(inputId);

    // Aplica a formatação a cada entrada de valor
    inputValor.addEventListener('input', () => formatarValor(inputValor));

    // Limpa o campo se ele estiver com o valor padrão ao focar
    inputValor.addEventListener('focus', () => {
        if (inputValor.value === "0,00") {
            inputValor.value = "";
        }
    });

    // Restaura "0,00" se estiver vazio ao sair do campo
    inputValor.addEventListener('blur', () => {
        if (inputValor.value === "" || inputValor.value === "0") {
            inputValor.value = "0,00";
        }
    });
}
