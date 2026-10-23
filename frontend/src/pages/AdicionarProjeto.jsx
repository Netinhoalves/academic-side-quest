import { Plus, Save } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import ProjetoForm from '../components/ProjetoForm';
import CategoriaForm from '../components/CategoriaForm';
import SubcategoriaForm from '../components/SubcategoriaForm';
import { createPpc } from '../services/api';

export default function AdicionarProjeto() {
    const navigate = useNavigate();
    const [etapa, setEtapa] = useState(0);
    const [dados, setDados] = useState({ projeto: {}, categorias: [], categoriaAtual: null });
    const [erro, setErro] = useState('');
    const [carregando, setCarregando] = useState(false);

    function avancarProjeto(event) {
        event.preventDefault();
        const formulario = Object.fromEntries(new FormData(event.currentTarget));
        const idCurso = Number(formulario.id_curso);
        if (!Number.isInteger(idCurso) || idCurso < 1) {
            return;
        }

        setDados((atual) => ({ ...atual, projeto: {
                    ...atual.projeto,
                    id_curso: idCurso,
                    nome: formulario.titulo,
                    ano: Number(formulario.ano),
                    descricao: formulario.descricao || null,
                    total_pontos: Number(formulario.pontos),
                } }));
        setEtapa(1);
    }

    function avancarCategoria(event) {
        event.preventDefault();
        const formulario = Object.fromEntries(new FormData(event.currentTarget));
        setDados((atual) => ({ ...atual, categoriaAtual: {
            nome: formulario.nome,
            descricao: formulario.descricao || null,
            limite_total: Number(formulario.limite_total),
            limite_semestre: Number(formulario.limite_semestre),
        } }));
        setEtapa(2);
    }

    function adicionarSubcategoria(subcategoria) {
        setDados((atual) => {
            const ultimaCategoria = atual.categorias[atual.categorias.length - 1];
            const anexarNaUltima = atual.categoriaAtual && ultimaCategoria?.nome === atual.categoriaAtual.nome;
            const categorias = anexarNaUltima
                ? atual.categorias.map((categoria, index) => index === atual.categorias.length - 1
                    ? { ...categoria, subcategorias: [...categoria.subcategorias, subcategoria] }
                    : categoria)
                : [...atual.categorias, { ...atual.categoriaAtual, subcategorias: [subcategoria] }];

            return { ...atual, categorias, categoriaAtual: categorias[categorias.length - 1] };
        });
        setEtapa(3);
    }

    function adicionarOutraSubcategoria() {
        const ultimaCategoria = dados.categorias[dados.categorias.length - 1];
        setDados((atual) => ({ ...atual, categoriaAtual: ultimaCategoria }));
        setEtapa(2);
    }

    function adicionarOutraCategoria() {
        setDados((atual) => ({ ...atual, categoriaAtual: null }));
        setEtapa(1);
    }

    async function salvarPpc() {
        setErro('');
        setCarregando(true);
        try {
            await createPpc({
                ...dados.projeto,
                categorias: dados.categorias,
            }, localStorage.getItem('asq_token'));
            navigate('/gerenciar-projetos');
        } catch (error) {
            setErro(error.message || 'Não foi possível adicionar o projeto');
        } finally {
            setCarregando(false);
        }
    }

    const valoresProjeto = dados.projeto.id_curso ? { ...dados.projeto, titulo: dados.projeto.nome, pontos: dados.projeto.total_pontos } : undefined;
    const limiteAcumulado = dados.categorias.reduce((total, categoria) => total + Number(categoria.limite_total || 0), 0);
    const limitePpc = Number(dados.projeto.total_pontos || 0);
    const podeSalvar = limiteAcumulado >= limitePpc && dados.categorias.length > 0;
    const etapas = ['Projeto', 'Categoria', 'Subcategoria'];

    return (
        <LayoutCoordenador>
            <div className="flex min-h-[calc(100vh-156px)] items-start justify-center pt-10">
                <div className="w-full max-w-[1000px]">
                    <div className="mb-6 grid grid-cols-3 gap-2">
                        {etapas.map((nome, index) => <div key={nome} className={`border-b-4 pb-2 text-center text-lg ${index === etapa ? 'border-color-blue text-color-blue' : index < etapa ? 'border-color-orange-bright text-color-blue' : 'border-[#D7C5B2] text-[#8A7868]'}`}>
                            <span className="mr-2 inline-flex h-7 w-7 items-center justify-center rounded-full bg-current text-sm text-white">{index + 1}</span>{nome}
                        </div>)}
                    </div>
                    {erro && <p className="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p>}
                    {etapa === 0 && <ProjetoForm titulo="Adicionar Projeto" projeto={valoresProjeto} onSubmit={avancarProjeto} submitLabel="Continuar" />}
                    {etapa === 1 && <CategoriaForm key={dados.categoriaAtual?.nome || 'nova-categoria'} titulo="Adicionar Categoria" categoria={dados.categoriaAtual || undefined} onSubmit={avancarCategoria} onCancelar={() => setEtapa(0)} mostrarVoltar submitLabel="Continuar" />}
                    {etapa === 2 && <SubcategoriaForm key={`${dados.categoriaAtual?.nome || 'categoria'}-${dados.categorias.length}`} titulo="Adicionar Subcategoria" onSubmit={adicionarSubcategoria} onCancelar={() => setEtapa(1)} carregando={carregando} />}
                    {etapa === 3 && <section className="rounded-lg bg-color-yellow px-8 py-6 shadow-sm">
                        <h1 className="border-b-2 border-color-blue pb-2 text-2xl md:text-3xl">Categorias do projeto</h1>
                        <div className="mt-4 rounded-md bg-[#FFDBAD] px-4 py-3 text-lg">
                            Limite total acumulado: <strong>{limiteAcumulado}</strong> / <strong>{limitePpc}</strong> pontos
                        </div>
                        {limiteAcumulado < limitePpc && <p className="mt-3 rounded-md bg-red-100 px-4 py-3 text-red-700">Adicione categorias até atingir pelo menos {limitePpc} pontos.</p>}
                        <div className="mt-4 space-y-2">
                            {dados.categorias.map((categoria, index) => <div key={`${categoria.nome}-${index}`} className="rounded-md bg-[#FFD394] px-4 py-3">
                                <strong>{categoria.nome}</strong> <span className="ml-2">{categoria.limite_total} pontos</span>
                                <small className="mt-1 block">{categoria.subcategorias.length} subcategoria(s)</small>
                            </div>)}
                        </div>
                        <div className="mt-5 flex flex-wrap justify-end gap-3">
                            <button type="button" onClick={adicionarOutraSubcategoria} className="flex items-center gap-2 rounded-md bg-color-blue px-4 py-2 text-lg text-white hover:bg-color-blue-light"><Plus size={18} /> Outra subcategoria</button>
                            <button type="button" onClick={adicionarOutraCategoria} className="flex items-center gap-2 rounded-md bg-color-blue px-4 py-2 text-lg text-white hover:bg-color-blue-light"><Plus size={18} /> Outra categoria</button>
                            <button type="button" onClick={salvarPpc} disabled={!podeSalvar || carregando} className="flex items-center gap-2 rounded-md bg-color-blue px-4 py-2 text-lg text-white hover:bg-color-blue-light disabled:cursor-not-allowed disabled:opacity-50"><Save size={18} /> {carregando ? 'Salvando...' : 'Salvar PPC'}</button>
                        </div>
                    </section>}
                </div>
            </div>
        </LayoutCoordenador>
    );
}