async function gerarReciboPDF() {
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF();
    let nome;
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
        // Carregar as imagens do input
        const imagensDataUrls = await carregarImagensDoInput("imagens");

        // Primeira página: conteúdo textual do relatório
        pdf.setFontSize(16);
        pdf.text("CLIENTE", 90, 45);

        // Exemplo de conteúdo da primeira página
         nome = document.getElementById("nome").value;
        const cpf = document.getElementById("cpf").value;
        const endereco = document.getElementById("endereco").value;
        const bairro = document.getElementById("bairro").value;
        const cidade = document.getElementById("cidade").value;
        const data = document.getElementById("data").value;
        const observacao = document.getElementById("observacao").value;

        
        

        const larguraMaximaLinha = 180; // Ajuste conforme necessário

        pdf.setFontSize(10);
        pdf.text(`Nome: ${nome}`, 10, 55);
        pdf.text(`CPF/CNPJ: ${cpf}`, 10, 62);
        pdf.text(`Endereço: ${endereco}`, 10, 69);
        pdf.text(`Bairro: ${bairro}`, 10, 76);
        pdf.text(`Cidade: ${cidade}`, 10, 83);
        pdf.text(`-------------------------------------------------------------------------------------------------------------------------------------------------------------------`, 10, 87);
        pdf.setFont("helvetica", "bold");
        pdf.text("RECIBO DE PAGAMENTO", 85, 95);
        pdf.setFont("helvetica", "normal");

        

        
        
        
        // OBSERVAÇÃO
        const linhasTextoObservacao = pdf.splitTextToSize(observacao, larguraMaximaLinha);
        pdf.setFont("helvetica", "bold"); 
        pdf.text("Observação:", 10, 220);
        pdf.setFont("helvetica", "normal");
        
        if (observacao.length === 0) {
            pdf.text(`Nenhuma observação`, 10, 227);
        }
        else {
            pdf.text(linhasTextoObservacao, 10, 227);
        }
        
        pdf.text(`-------------------------------------------------------------------------------------------------------------------------------------------------------------------`, 10, 240);


    
    

        // Obter o técnico selecionado e o CNPJ
        const selectTecnico = document.getElementById('tecnico');
        const tecnicoSelecionado = selectTecnico.options[selectTecnico.selectedIndex];
        const tecnicoNome = tecnicoSelecionado.value; // Nome do técnico
        const tecnicoCNPJ = tecnicoSelecionado.getAttribute('data-cnpj'); // CNPJ do técnico
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
            pdf.addImage(imgAssinatura, "PNG", 15, 262, 45, 20); // Ajuste as dimensões conforme necessário
        }
        // Adicionar informações do técnico
        pdf.text(`-----------------------------------`, 15, 280);    
        pdf.text(`${tecnicoNome}`, 15, 285);
        pdf.text(`CNPJ ${tecnicoCNPJ}`, 15, 290);



        
        if (data) {
            // Dividindo a string no formato ISO
            const [ano, mes, dia] = data.split('-');
            
            // Montando a data no formato dd/mm/yyyy
            const dataFormatada = `${dia}/${mes}/${ano}`;
            
            // Inserindo no PDF
            pdf.text(`${dataFormatada}, ${cidade}`, 140, 285);
        }

    } catch (error) {
        console.warn("Erro ao carregar uma ou mais imagens:", error);
    }

    // Salvar PDF
    pdf.save(`Laudo_Tecnico_${nome}.pdf`);
}
