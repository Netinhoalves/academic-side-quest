const CHAVE_PROJETOS = 'asq_projetos_demo';

const projetosIniciais = [
    { id: '2016', titulo: 'Projeto pedagógico TADS - 2016', ano: '2016', curso: 'Tecnologia em analise e desenvolvimento de sistemas - 1', descricao: 'Projeto pedagogico do curso de Tecnologia em analise e desenvolvimento de sistemas.', pontos: '100' },
    { id: '2018', titulo: 'Projeto pedagógico TADS - 2018', ano: '2018', curso: 'Tecnologia em analise e desenvolvimento de sistemas - 1', descricao: 'Projeto pedagogico do curso de Tecnologia em analise e desenvolvimento de sistemas.', pontos: '100' },
    { id: '2020', titulo: 'Projeto pedagógico TADS - 2020', ano: '2020', curso: 'Tecnologia em analise e desenvolvimento de sistemas - 2', descricao: 'Projeto pedagogico do curso de Tecnologia em analise e desenvolvimento de sistemas.', pontos: '100' },
    { id: '2022', titulo: 'Projeto pedagógico TADS - 2022', ano: '2022', curso: 'Tecnologia em analise e desenvolvimento de sistemas - 1', descricao: 'Projeto pedagogico do curso de Tecnologia em analise e desenvolvimento de sistemas.', pontos: '100' },
];

export function carregarProjetos() {
    const dados = localStorage.getItem(CHAVE_PROJETOS);

    if (!dados) {
        return projetosIniciais;
    }

    try {
        return JSON.parse(dados).filter((projeto) => projeto.titulo?.trim().toLowerCase() !== 'pppc doido');
    } catch {
        return projetosIniciais;
    }
}

export function salvarProjetos(projetos) {
    localStorage.setItem(CHAVE_PROJETOS, JSON.stringify(projetos));
}