async function gerarPDF() {
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
        pdf.text("Relatório Técnico", 85, 45);

        // Exemplo de conteúdo da primeira página
         nome = document.getElementById("nome").value;
        const cpf = document.getElementById("cpf").value;
        const endereco = document.getElementById("endereco").value;
        const bairro = document.getElementById("bairro").value;
        const cidade = document.getElementById("cidade").value;
        const data = document.getElementById("data").value;
        const observacao = document.getElementById("observacao").value;
        //const total = document.getElementById("total").value;
        //const formaPagamento = document.getElementById("forma-pagamento").value;
        const empresaSolicitacao = document.getElementById("empresaSolicitacao").value;

        const detalhesFrente = document.getElementById("detalhes_frente").value.trim();
        const detalhesFundo = document.getElementById("detalhes_fundos").value.trim();
        const detalhesAreaServico = document.getElementById("detalhes_area_servico").value.trim();
        const detalhesDispensa = document.getElementById("detalhes_dispensa").value.trim();
        const detalhesCozinha = document.getElementById("detalhes_cozinha").value.trim();
        const detalhesBanheiro = document.getElementById("detalhes_banheiro").value.trim();
        const detalhesJardim = document.getElementById("detalhes_jardim").value.trim();
        const detalhesSala = document.getElementById("detalhes_sala").value.trim();

        const detalhesAreaComum = document.getElementById("detalhes_areacomum").value.trim();
        const detalhesGaragem = document.getElementById("detalhes_garagem").value.trim();
        const detalhesPiscina = document.getElementById("detalhes_piscina").value.trim();
        const detalhesRedeDeIncendio = document.getElementById("detalhes_rededeincendio").value.trim();


        const geofonamentoCheckbox = document.getElementById("geofonamentoCheckbox");
        const pressurizacaoCheckbox = document.getElementById("pressurizacaoCheckbox");
        const cameraTermograficaCheckbox = document.getElementById("cameraTermograficaCheckbox");
        const sensorDeUmidadeCheckbox = document.getElementById("sensorDeUmidadeCheckbox");
        
        

        const larguraMaximaLinha = 180; // Ajuste conforme necessário

        pdf.setFontSize(10);
        pdf.text(`Nome: ${nome}`, 10, 55);
        pdf.text(`CPF/CNPJ: ${cpf}`, 10, 62);
        pdf.text(`Endereço: ${endereco}`, 10, 69);
        pdf.text(`Bairro: ${bairro}`, 10, 76);
        pdf.text(`Cidade: ${cidade}`, 10, 83);
        pdf.text(`-------------------------------------------------------------------------------------------------------------------------------------------------------------------`, 10, 87);
        pdf.setFont("helvetica", "bold");
        pdf.text("SERVIÇO EXECUTADO", 85, 95);
        pdf.setFont("helvetica", "normal");

        const selectedTechniques = [];

        // Verifica os checkboxes e adiciona os textos ao array
        if (geofonamentoCheckbox.checked) {
            selectedTechniques.push("Geofonamento com o geofone eletrônico");
        }
        if (pressurizacaoCheckbox.checked) {
            selectedTechniques.push("Pressurização da Rede");
        }
        if (cameraTermograficaCheckbox.checked) {
            selectedTechniques.push("Inspeção com câmera termográfica");
        }
        if (sensorDeUmidadeCheckbox.checked) {
            selectedTechniques.push("Verificação de umidade com o sensor de umidade");
        }

        let solicitacaoUM = true;
        let solicitacaoDois = true;

        // Formata o texto final de forma dinâmica
        let techniquesText = "";
        if (selectedTechniques.length > 0) {
            const lastTechnique = selectedTechniques.pop(); // Remove o último elemento
            techniquesText = `Técnicas utilizadas: ${selectedTechniques.join(", ")}${selectedTechniques.length > 0 ? " e " : ""}${lastTechnique}.`;

            const techniquesTextLinhas = pdf.splitTextToSize(techniquesText, larguraMaximaLinha);
            pdf.text(techniquesTextLinhas, 10, 105);
        } else {
            techniquesText = "Nenhuma técnica foi selecionada.";
        }

        if(geofonamentoCheckbox.checked){
            let primeiroSetorVerificacao = ''; 
            const primeiroSetor = document.querySelector('input[name="primeirosetor"]:checked')?.value;

            

            if (primeiroSetor === 'vazamento') {
                primeiroSetorVerificacao = '1º Setor - Com o uso do geofone eletrônico identificamos um VAZAMENTO não aparente no solo nas instalações hidráulicas, conforme às fotos em anexo.';
                solicitacaoUM = true;
            } else {
                primeiroSetorVerificacao = '1º Setor - Com o uso do geofone eletrônico foi realizado uma vistoria nas instalações hidráulicas e não foi identificado vazamentos.';
                solicitacaoUM = false;
            }

            const linhasTextoPrimeiroSetor = pdf.splitTextToSize(primeiroSetorVerificacao, larguraMaximaLinha);
            pdf.text(linhasTextoPrimeiroSetor, 10, 117);

            const segundoSetor = document.querySelector('input[name="segundosetor"]:checked')?.value;
            let segundoSetorVerificacao = ''; 

            
            if (segundoSetor == 'vazamento') {
                segundoSetorVerificacao = '2º Setor - Com o uso do geofone eletrônico identificamos um VAZAMENTO não aparente no solo nas instalações hidráulicas, conforme às fotos em anexo.';
                solicitacaoDois = true;
            }
            else {
                segundoSetorVerificacao = '2º Setor - Com o uso do geofone eletrônico foi realizado uma vistoria nas instalações hidráulicas e não foi identificado vazamentos.';
                solicitacaoDois = false;
            }

            const linhasTextoSegundoSetor = pdf.splitTextToSize(segundoSetorVerificacao, larguraMaximaLinha);
            pdf.text(linhasTextoSegundoSetor, 10, 129);
                
        };

        
        // Função para formatar os itens
        function formatarLocalizacao(nome, valor) {
            if (valor) {
                return `(X) ${nome}: ${valor}`;
            } else {
                return `() ${nome}:`;
            }
        }


        const larguraLinhaLocalVazamento = 80;
        // Construção do texto
        const locaisDireita = [
            formatarLocalizacao("Frente do imóvel", detalhesFrente),
            formatarLocalizacao("Fundos do imóvel", detalhesFundo),
            formatarLocalizacao("Área de Serviço", detalhesAreaServico),
            formatarLocalizacao("Dispensa", detalhesDispensa),
            formatarLocalizacao("Cozinha", detalhesCozinha),
            formatarLocalizacao("Banheiro", detalhesBanheiro),
        ];
        const locaisEsquerda = [
            formatarLocalizacao("Sala", detalhesSala),
            formatarLocalizacao("Jardim", detalhesJardim),
            formatarLocalizacao("Garagem", detalhesGaragem),
            formatarLocalizacao("Piscina", detalhesPiscina),
            formatarLocalizacao("Área Comum", detalhesAreaComum),
            formatarLocalizacao("Rede de Incêndio", detalhesRedeDeIncendio),
        ];

        // Adicionar título e itens ao PDF apenas se houver pelo menos um preenchido
        if (locaisDireita.some(texto => texto.includes("(X)")) || locaisEsquerda.some(texto => texto.includes("(X)"))) {
            pdf.setFont("helvetica", "bold");
            pdf.text("LOCAL DO VAZAMENTO", 85, 140);
            pdf.setFont("helvetica", "normal");

            let posicaoY = 150; // Posição inicial Y
            locaisDireita.forEach((local) => {
                pdf.text( pdf.splitTextToSize(local, larguraLinhaLocalVazamento), 20, posicaoY); // Escreve cada item no PDF
                posicaoY += 12; // Incrementa a posição Y
            });

            let posicaoYD = 150; // Posição inicial Y
            locaisEsquerda.forEach((local) => {
                pdf.text(pdf.splitTextToSize(local, larguraLinhaLocalVazamento), 110, posicaoYD); // Escreve cada item no PDF
                posicaoYD += 12; // Incrementa a posição Y
            });
        }
        
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


        // SOLICITAÇÃO
        let solicitacao = '';
        
        if (empresaSolicitacao !== 'selecionar') {
            
            if (solicitacaoUM == true || solicitacaoDois == true) {
                solicitacao = `Por meio desse relatório, solicitamos à ${empresaSolicitacao}, a refazer as contas altas.`;
            }
            else {
                solicitacao = `Por meio desse relatório, solicitamos à ${empresaSolicitacao} a refazer as contas altas já que essa água não foi consumida e sim perdida no solo, sem o conhecimento e a intenção do cliente.`;
            }

            const linhasTextoSolicitacaoEmpresa = pdf.splitTextToSize(solicitacao, larguraMaximaLinha);
            pdf.setFont("helvetica", "bold"); 
            pdf.text("SOLICITAÇÃO", 90, 245);
            pdf.setFont("helvetica", "normal");
            pdf.text(linhasTextoSolicitacaoEmpresa, 10, 253);
     
        };
        //const garantiaUm = `Garantia total no local localizado pelo técnico. ( Prazo máximo de 30 dias para acionar a garantia) caso solicite a mesma sem a necessidade devida, será cobrado novamente o valor do serviço de localização.`;
        //const linhasTextoGaramtiaUm = pdf.splitTextToSize( garantiaUm, larguraMaximaLinha);
        //pdf.text(linhasTextoGaramtiaUm, 10, 245);

        //const garantiaDois = `Garantia de 180 dias em todos os serviços  hidráulicos reparados pela empresa. Porém se o reparo for executado por terceiros, prevalece a garantia de 30 dias da localização.`;
        //const linhasTextoGaramtiaDois = pdf.splitTextToSize( garantiaDois, larguraMaximaLinha);
        //pdf.text(linhasTextoGaramtiaDois, 10, 255);

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

        // Adicionar uma nova página para começar a inserir as imagens
        if (imagensDataUrls.length != 0){
        pdf.addPage();

        pdf.setFont("helvetica", "bold");
        pdf.text("ANEXO", 95, 10);
        pdf.setFont("helvetica", "normal");
        // Configura a posição inicial na segunda página
        // Configura a posição inicial na segunda página
        // Configura a posição inicial na segunda página
        let yPosition = 22;
        let positionAnexo = 20;
        let countAnexo = 1;

        // Adicionar cada imagem a partir da segunda página
        for (const dataUrl of imagensDataUrls) {
            // Criar uma instância de imagem
            const img = new Image();
            img.src = dataUrl;

            // Esperar a imagem carregar antes de obter dimensões
            await new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = reject;
            });

            // Dimensões reais da imagem
            const imgWidth = img.naturalWidth;
            const imgHeight = img.naturalHeight;

            // Tamanho máximo permitido no PDF
            const maxWidth = 150; // Largura máxima no PDF
            const maxHeight = 100; // Altura máxima no PDF

            // Calcular as dimensões proporcionalmente
            let width = imgWidth;
            let height = imgHeight;

            if (imgWidth > maxWidth || imgHeight > maxHeight) {
                const widthRatio = maxWidth / imgWidth;
                const heightRatio = maxHeight / imgHeight;
                const scale = Math.min(widthRatio, heightRatio); // Usa o menor fator de escala

                width = imgWidth * scale;
                height = imgHeight * scale;
            }

            // Verificar se há espaço suficiente na página para a próxima imagem
            if (yPosition + height > 280) { // Limite vertical da página
                pdf.addPage(); // Cria uma nova página se a imagem não couber
                yPosition = 22; // Reseta a posição inicial
                positionAnexo = 20; // Reseta a posição do texto
            }

            // Adicionar texto e imagem ao PDF
            pdf.text(`Imagem: ${countAnexo}`, 10, positionAnexo);
            pdf.addImage(dataUrl, "PNG", 10, yPosition, width, height);

            // Atualizar posição para a próxima imagem
            yPosition += height + 10; // Move a posição para a próxima imagem, considerando a altura ajustada
            positionAnexo = yPosition - 5; // Ajusta a posição do texto da próxima imagem
            countAnexo += 1;
        }
        }

    } catch (error) {
        console.warn("Erro ao carregar uma ou mais imagens:", error);
    }

    // Salvar PDF
    pdf.save(`Laudo_Tecnico_${nome}.pdf`);
}