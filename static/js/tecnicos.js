const tecnicos = [
  // --- GOIÂNIA ---
  {
    nome: "Roberto Rodrigues",
    cnpj: "45.782.998/0001-61",
    imagem: "assinaturaroberto.png",
    cidade: "Goiânia"
  },
  {
    nome: "Natanael Souza",
    cnpj: "45.782.998/0001-61",
    imagem: "assinaturanatanaelsouza.png",
    cidade: "Goiânia"
  },
  {
    nome: "Joel Oliveira",
    cnpj: "45.782.998/0001-61",
    imagem: "assinaturajoeloliveira.png",
    cidade: "Goiânia"
  },
  {
    nome: "Marcio Cleber",
    cnpj: "45.782.998/0001-61",
    imagem: "assinaturamarciocleber.png",
    cidade: "Goiânia"
  },

  // --- SALVADOR ---
  {
    nome: "Alessandro Lima",
    cnpj: "52.139.237/0001-51",
    imagem: "assinaturaalessandrolima.png",
    cidade: "Salvador"
  },
  {
    nome: "Lucas Freire",
    cnpj: "52.139.237/0001-51",
    imagem: "assinaturalucasfreire.png",
    cidade: "Salvador"
  },
  {
    nome: "Reinaldo Cirqueira",
    cnpj: "52.139.237/0001-51",
    imagem: "assinaturareinaldo.png",
    cidade: "Salvador"
  },

  // --- SÃO PAULO ---
  {
    nome: "Marcos Carvalho",
    cnpj: "47.872.998/0001-61",
    imagem: "assinaturamarscosmarquito.png",
    cidade: "São Paulo"
  },
  {
    nome: "Eduardo Santos",
    cnpj: "26.552.351/0001-07",
    imagem: "assinaturaeduardosantos.png",
    cidade: "São Paulo"
  },

  // --- PORTO ALEGRE ---
  {
    nome: "Marcio Gorrese",
    cnpj: "24.549.249/0001-19",
    imagem: "assinaturamarciogorrese.png",
    cidade: "Porto Alegre"
  },

  // --- SOROCABA / SP INTERIOR ---
  {
    nome: "Erick Carvalho",
    cnpj: "47.056.501/0001-53",
    imagem: "assinaturaericksorocaba.png",
    cidade: "Sorocaba"
  },

  // --- OUTROS (MESMO CNPJ DA EMPRESA PRINCIPAL) ---
  {
    nome: "Alan Honorato",
    cnpj: "43.973.146/0001-26",
    imagem: "assinaturaalanhonorato.png"
  },
  {
    nome: "Gildson Dos Santos",
    cnpj: "43.973.146/0001-26",
    imagem: "assinaturagildson.png"
  },
  {
    nome: "Edinei Francisco",
    cnpj: "43.973.146/0001-26",
    imagem: "assinaturaedinei.png"
  },
  {
    nome: "Paulo Ferrandin",
    cnpj: "43.973.146/0001-26",
    imagem: "assinaturapauloferrandin.png"
  },
  {
    nome: "Jociane Fagundes",
    cnpj: "49.311.391/0001-54",
    imagem: "assinaturajocianefagundes.png"
  },
  {
    nome: "Jeiel Oliveira",
    cnpj: "44.515.356/0001-33",
    imagem: "assinaturajeieloliveira.png"
  },
  {
    nome: "Venancio Benevides",
    cnpj: "98.765.432/0001-45",
    imagem: "assinaturavenancio.png"
  },
  {
    nome: "Thaian Bispo",
    cnpj: "43.973.146/0001-26",
    imagem: "assinaturathaian.png"
  }
];


// Função para preencher selects de técnicos
function preencherSelectTecnicos(selectId) {
  const select = document.getElementById(selectId);
  select.innerHTML = '<option value="">Selecionar Técnico</option>';

  tecnicos.forEach(t => {
    const option = document.createElement('option');
    option.value = t.nome;
    option.textContent = `${t.nome}${t.cidade ? " - " + t.cidade : ""}`;
    option.setAttribute('data-cnpj', t.cnpj);
    option.setAttribute('data-imagem', t.imagem);
    select.appendChild(option);
  });
}