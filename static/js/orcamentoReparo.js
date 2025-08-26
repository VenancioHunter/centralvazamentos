function validarCamposObrigatorios() {
    // IDs dos campos obrigatórios
    const camposObrigatorios = [
        "nome",
        "cpf",
        "endereco",
        "bairro", 
        "cidade",
        "estado",
        "tecnico",
        "data"
    ];

    // Lista de mensagens de erro para campos vazios
    const mensagensErro = [];

    // Verifica cada campo
    camposObrigatorios.forEach(id => {
        const campo = document.getElementById(id);
        if (!campo.value.trim()) {
            mensagensErro.push(`O campo "${campo.previousElementSibling.textContent}" está vazio.`);
        }
    });

    // Exibe mensagens de erro, se houver
    if (mensagensErro.length > 0) {
        alert(mensagensErro.join("\n")); // Exibe os erros em um único alerta
        return false; // Interrompe o processo
    }

    return true; // Todos os campos estão preenchidos
}


async function gerarPDF() {

     // Primeiro, valida os campos obrigatórios
    if (!validarCamposObrigatorios()) {
        return; // Interrompe a geração do PDF se houver campos vazios
    }
    

    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF();
    let nome;

     // SHAPE SUPERIOR
     try {
        const shapeTop = new Image();
        shapeTop.src = "../static/img/shape_superior.png"; // Caminho do seu shape superior

        await new Promise((resolve, reject) => {
            shapeTop.onload = resolve;
            shapeTop.onerror = reject;
        });

        // Adiciona o shape no topo (ajuste X, Y, largura e altura conforme necessário)
        pdf.addImage(shapeTop, "PNG", 0, 0, 210, 55); // 210 = largura A4, 30 = altura do shape
    } catch (e) {
        console.warn("Shape superior não carregado:", e);
        }
    try {
        // Definir logo
        const logoURL = "../static/img/logowhite.png";
        let imgLogo = new Image();
        imgLogo.src = logoURL;

        // Esperar o carregamento da logo
        await new Promise((resolve, reject) => {
            imgLogo.onload = resolve;
            imgLogo.onerror = reject;
        });

        // Adicionar logo no PDF
        pdf.addImage(imgLogo, "PNG", 1, 1, 45, 45);
    } catch (error) {
        console.warn("Logo não carregada. Continuando sem logo.");
    }
  // Função para carregar imagens selecionadas no input e retornar um array de DataURLs
    const carregarImagensDoInput = async (inputId) => {
        const input = document.getElementById(inputId);
        const files = input.files;
        const dataUrls = [];

        for (const file of files) {
            const dataUrl = await new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = (event) => resolve(event.target.result);
                reader.onerror = reject;
                reader.readAsDataURL(file);
            });
            dataUrls.push(dataUrl);
        }
        return dataUrls;
    };

   
    

    try {

        // Primeira página: conteúdo textual do relatório
        //pdf.setFontSize(16);
        //pdf.text("CLIENTE", 90, 45);

        // Exemplo de conteúdo da primeira página
        nome = document.getElementById("nome").value;
        const cpf = document.getElementById("cpf").value;
        const endereco = document.getElementById("endereco").value;
        const bairro = document.getElementById("bairro").value;
        const cidade = document.getElementById("cidade").value;
        const data = document.getElementById("data").value;
        const observacao = document.getElementById("observacao").value;
        function formatarValor(valor) {
    // Remove pontos (milhar) e substitui vírgula decimal por ponto
    return parseFloat(valor.replace(/\./g, "").replace(",", "."));
}

// Obtém os valores dos inputs
const valorLocalizacao = formatarValor(document.getElementById("valorlocalizacao").value || "0");
const valorReparo = formatarValor(document.getElementById("valorreparo").value || "0");

// Soma os valores
const total = valorLocalizacao + valorReparo;

// Formata o total como moeda brasileira (R$)
        const totalFormatado = total.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
        const formatLocalizacao = valorLocalizacao.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
        const formatReparo = valorReparo.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
        //const totalFormatado = total.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
        //const total = document.getElementById("total").value;
        //const formaPagamento = document.getElementById("forma-pagamento").value;
        //const empresaSolicitacao = document.getElementById("empresaSolicitacao").value;

        
        

        const larguraMaximaLinha = 180; // Ajuste conforme necessário

        pdf.setFontSize(14);
        pdf.text(`${nome}`, 10, 55);
        pdf.setFontSize(10);
        pdf.text(`CPF/CNPJ: ${cpf}`, 10, 62);
        pdf.text(`Endereço: ${endereco}`, 10, 69);
        pdf.text(`Bairro: ${bairro}`, 10, 76);
        pdf.text(`Cidade: ${cidade}`, 10, 83);
        pdf.text(`-------------------------------------------------------------------------------------------------------------------------------------------------------------------`, 10, 87);
        pdf.setFont("helvetica", "bold");
        pdf.setFontSize(16);
        pdf.text("ORÇAMENTO", 85, 95);
        pdf.setFont("helvetica", "normal");
        pdf.setFontSize(10);


        const telefonesMap = {
            "Maceió": "(82) 92001-4853",
            "Satuba": "(82) 92001-4853",
            "Santa Luzia do Norte": "(82) 92001-4853",
            "Coqueiro Seco": "(82) 92001-4853",
            "Cadoz": "(82) 92001-4853",
            "Rio Largo": "(82) 92001-4853",
            "Marechal Deodoro": "(82) 92001-4853",
            "Santa Luzia": "(82) 92001-4853",
            "Pilar": "(82) 92001-4853",
            "Barra de São Miguel": "(82) 92001-4853",
            "Atalaia": "(82) 92001-4853",
            "Murici": "(82) 92001-4853",
            "Messias": "(82) 92001-4853",
            "Barra de Santo Antônio": "(82) 92001-4853",
            "Paripueira": "(82) 92001-4853",


            "Salvador": "(71) 93300-1134",
            "Camaçari": "(71) 93300-1134",
            "Feira de Santana": "(75) 93300-2063",
            "Lauro de Freitas": "(71) 93300-1134",
            "Simões Filho": "(71) 93300-1134",
            "Gamboa": "(71) 93300-1134",
            "Vera Cruz": "(71) 93300-1134",
            "Itaparica": "(71) 93300-1134",
            "Mata de São João": "(71) 93300-1134",
            "Alagoinhas": "(71) 93300-1134",
            "Madre De Deus": "(71) 93300-1134",


            "Goiânia": "(62) 93300-6961",
            "Aparecida de Goiânia": "(62) 93300-6961",
            "Senador Canedo": "(62) 93300-6961",
            "Trindade": "(62) 93300-6961",
            "Anápolis": "(62) 93300-6961",
            "Goianira": "(62) 93300-6961",

            "São Paulo": "(11) 93300-3231",
            "Osasco": "(11) 93300-3231",
            "Barueri": "(11) 93300-3231",
            "Campinas": "(19) 92001-6371",
            "Itupeva": "(19) 92001-6371",
            "Franco Da Rocha": "(19) 92001-6371",
            "Jundiaí": "(19) 92001-6371",
            "Campo Limpo Paulista": "(19) 92001-6371",
            "Louveira": "(19) 98563-4600",
            "Várzea Paulista": "(19) 92001-6371",
            "Vinhedo": "(19) 92001-6371",
            "Valinhos": "(19) 92001-6371",
            "Hortolândia": "(19) 92001-6371",
            "Paulínia": "(19) 92001-6371",
            "Itatiba": "(19) 92001-6371",
            "Indaiatuba": "(19) 92001-6371",
            "Jaguariúna": "(19) 92001-6371",
            "Sumaré": "(11) 93300-3231",
            "Diadema": "(11) 93300-3231",
            "Santo André": "(11) 93300-3231",
            "São Bernardo do Campo": "(11) 93300-3231",
            "São Caetano do Sul": "(19) 92001-6371",
            "Mauá": "(19) 92001-6371",
            "Jaguariúna": "(19) 92001-6371",
            "Nova Odessa": "(19) 92001-6371",
            "Americana": "(19) 92001-6371",
            "Atibaia": "(19) 92001-6371",
            "Guarulhos": "(11) 93300-3231",
            "Poa": "(11) 93300-3231",
            "Mogi das Cruzes": "(11) 93300-3231",
            "Itaquacetuba": "(11) 93300-3231",
            "Cajamar": "(19) 92001-6371",
            "Amparo": "(19) 92001-6371",
            "Capivari": "(19) 92001-6371",

            "Florianópolis": "(48) 93300-4291",
            "São José": "(48) 93300-4291",
            "Palhoça": "(48) 93300-4291",
            "Biguaçu": "(48) 93300-4291",

            "Porto Alegre": "(51) 92001-5474",
            "Canoas": "(51) 92001-5474",
            "Glorinha": "(51) 92001-5474",
            "Guaíba": "(51) 92001-5474",

        };

        const telefone = telefonesMap[cidade] || "Telefone não disponível";
        
        pdf.setFontSize(14);
        pdf.setTextColor(255, 255, 255);
        pdf.setFont("helvetica", "bold");
        pdf.text(`Central Vazamentos`, 130, 20);
        pdf.setFont("helvetica", "normal");
        pdf.setFontSize(10);
        pdf.text(`CNPJ: 43.973.146/0001-26`, 130, 25);
        pdf.text(`Tel: ${telefone}`, 130, 30);
        pdf.text(`E-mail: comercial@centralvazamentos.com.br`, 130, 35);


        pdf.setTextColor(0, 0, 0);
        pdf.setFontSize(10);

        const selectedTechniques = [];
        const allTechniques = {
    "geofonamentoCheckbox": "Geofonamento com o geofone eletrônico",
    "pressurizacaoCheckbox": "Pressurização da Rede",
    "cameraTermograficaCheckbox": "Inspeção com câmera termográfica",
    "sensorDeUmidadeCheckbox": "Verificação de umidade com o sensor de umidade"
};

        
pdf.setFont("helvetica", "bold"); 
            pdf.text("Descrição:", 10, 110);
            pdf.setFont("helvetica", "normal");        
        
// Verifica quais técnicas foram selecionadas
const checkboxes = Object.keys(allTechniques);
checkboxes.forEach(id => {
    if (document.getElementById(id).checked) {
        selectedTechniques.push(allTechniques[id]);
    }
});

// Construção da frase final
let techniquesText = "";

if (selectedTechniques.length > 0) {
    // Remove a última técnica da lista para formatação correta
    const lastSelected = selectedTechniques.pop();
    let mainText = `Será realizado o serviço de vistoria na rede hidráulica utilizando a técnica de ${selectedTechniques.join(", ")}${selectedTechniques.length > 0 ? " e " : ""}${lastSelected}`;

    // Calcula as técnicas NÃO selecionadas
    const unselectedTechniques = checkboxes
        .map(id => allTechniques[id])
        .filter(tech => !selectedTechniques.includes(tech) && tech !== lastSelected);

    if (unselectedTechniques.length > 0) {
        const lastOptional = unselectedTechniques.pop();
        mainText += `, se necessário será realizado ${unselectedTechniques.join(", ")}${unselectedTechniques.length > 0 ? " e " : ""}${lastOptional}`;
    }

    techniquesText = mainText + ".";
} else {
    techniquesText = "Nenhuma técnica foi selecionada.";
}

// Geração do PDF com o texto formatado
const techniquesTextLinhas = pdf.splitTextToSize(techniquesText, larguraMaximaLinha);
pdf.text(techniquesTextLinhas, 10, 117);

        let verifica_detalhes_existe = false;

        
        
        
        // OBSERVAÇÃO
        const linhasTextoObservacao = pdf.splitTextToSize(observacao, larguraMaximaLinha);
        

        if (verifica_detalhes_existe == true) {
            pdf.setFont("helvetica", "bold"); 
            pdf.text("Observação:", 10, 220);
            pdf.setFont("helvetica", "normal");

            if (observacao.length === 0) {
            pdf.text(`Nenhuma observação`, 10, 227);
            }
            else {
                pdf.text(linhasTextoObservacao, 10, 227);
            }
        }
        else {
            pdf.setFont("helvetica", "bold"); 
            pdf.text("Observação:", 10, 140);
            pdf.setFont("helvetica", "normal");

            if (observacao.length === 0) {
            pdf.text(`Nenhuma observação`, 10, 147);
            }
            else {
                pdf.text(linhasTextoObservacao, 10, 147);
            }
        }

        // Define a cor do fundo (por exemplo, cinza claro)
        pdf.setFillColor(13, 85, 144); // RGB: 220, 220, 220

        // Desenha o fundo retangular antes do texto
        pdf.rect(10, 174, 190, 9, "F"); // x, y, largura, altura, modo 'F' = filled
        
        //pdf.text(`-------------------------------------------------------------------------------------------------------------------------------------------------------------------`, 10, 177);
        pdf.setTextColor(255, 255, 255); // Define a cor do texto (RGB)

        // Texto em negrito e colorido
        pdf.setFont("helvetica", "bold"); 
        pdf.text("SERVIÇO", 15, 180);
        pdf.text("VALOR", 175, 180);

        // Restaura a cor para preto e fonte normal após o título
        pdf.setTextColor(0, 0, 0);
        pdf.setFont("helvetica", "normal");

        //pdf.text(`-------------------------------------------------------------------------------------------------------------------------------------------------------------------`, 10, 183);
        pdf.text(`Vistoria`, 15, 187);
        pdf.text(`${formatLocalizacao}`, 170, 187);
        //pdf.text(`Reparo`, 15, 192);
        //pdf.text(`${formatReparo}`, 170, 192);
        pdf.text(`-------------------------------------------------------------------------------------------------------------------------------------------------------------------`, 10, 195);
        pdf.text(`${totalFormatado}`, 170, 198);
        pdf.text(`TOTAL`, 15, 198);
        

        // Obter o técnico selecionado e o CNPJ
        const selectTecnico = document.getElementById('tecnico');
        const tecnicoSelecionado = selectTecnico.options[selectTecnico.selectedIndex];
        const tecnicoNome = tecnicoSelecionado.value; // Nome do técnico
        const imagemAssinatura = tecnicoSelecionado.getAttribute('data-imagem');

        if (imagemAssinatura) {
            const imagemAssinaturaURL = `../static/img/${imagemAssinatura}`;
            const imgAssinatura = new Image();
            imgAssinatura.src = imagemAssinaturaURL;

            // Esperar o carregamento da imagem
            await new Promise((resolve, reject) => {
                imgAssinatura.onload = resolve;
                imgAssinatura.onerror = reject;
            });

            // Adicionar a assinatura no PDF
            pdf.addImage(imgAssinatura, "PNG", 24, 262, 45, 20); // Ajuste as dimensões conforme necessário
        }
        // Adicionar informações do técnico
        pdf.text(`-----------------------------------`, 24, 280);    
        pdf.text(`${tecnicoNome}`, 32, 285);
        pdf.text(`Gerente Comercial`, 29, 290);


        // SHAPE INFERIOR
        try {
            const shapeBottom = new Image();
            shapeBottom.src = "../static/img/shape_inferior.png"; // Caminho do seu shape inferior
    
            await new Promise((resolve, reject) => {
                shapeBottom.onload = resolve;
                shapeBottom.onerror = reject;
            });
    
            // Adiciona o shape no rodapé (posição Y geralmente no fim da página A4)
            pdf.addImage(shapeBottom, "PNG", 0, 285, 210, 17); // 280 = quase final da página
        } catch (e) {
            console.warn("Shape inferior não carregado:", e);
        }

        pdf.setTextColor(255, 255, 255);

        //pdf.setTextColor(255, 255, 255); // Define a cor do texto (RGB)
        if (data) {
            // Dividindo a string no formato ISO
            const [ano, mes, dia] = data.split('-');
            
            // Montando a data no formato dd/mm/yyyy
            const dataFormatada = `${dia}/${mes}/${ano}`;
            
            // Inserindo no PDF
            pdf.text(`${dataFormatada}, ${cidade}`, 140, 292);
        }

        


    } catch (error) {
        console.warn("Erro ao carregar uma ou mais imagens:", error);
    }

        
    // Salvar PDF
    pdf.save(`Orcamento_${nome}.pdf`);
}


async function logo(pdf) {
    try {
        // Definir logo
        const logoURL = "../static/img/logo.png";
        const imgLogo = new Image();
        imgLogo.src = logoURL;

        // Esperar o carregamento da logo
        await new Promise((resolve, reject) => {
            imgLogo.onload = resolve;
            imgLogo.onerror = reject;
        });

        // Adicionar logo no PDF
        pdf.addImage(imgLogo, "PNG", 1, 1, 45, 45);
    } catch (error) {
        console.warn("Logo não carregada. Continuando sem logo.");
    }
}
