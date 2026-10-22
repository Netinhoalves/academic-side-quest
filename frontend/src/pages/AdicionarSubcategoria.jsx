import { useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import SubcategoriaForm from '../components/SubcategoriaForm';
import { createPpc, getPpc, updatePpc } from '../services/api';

export default function AdicionarSubcategoria() {
    const navigate = useNavigate();
    const location = useLocation();
    const { projetoId, categoriaId } = useParams();
    const categoriaInicial = location.state?.categoria;
    const projetoInicial = location.state?.projeto;
    const [erro, setErro] = useState('');
    const [carregando, setCarregando] = useState(false);

    async function handleSubmit(dados) {
        setErro('');
        setCarregando(true);
        try {
            if (projetoInicial) {
                await createPpc({ ...projetoInicial, categorias: [{ ...categoriaInicial, subcategorias: [dados] }] }, localStorage.getItem('asq_token'));
                navigate('/gerenciar-projetos');
                return;
            }

            if (!projetoId || !categoriaId) {
                throw new Error('Dados do projeto não encontrados. Volte ao cadastro do projeto e tente novamente.');
            }

            const projeto = await getPpc(projetoId, localStorage.getItem('asq_token'));
            const categorias = categoriaInicial
                ? [...projeto.categorias, { ...categoriaInicial, subcategorias: [dados] }]
                : projeto.categorias.map((categoria) => categoria.id === Number(categoriaId)
                    ? { ...categoria, subcategorias: [...categoria.subcategorias, dados] }
                    : categoria);
            await updatePpc(projetoId, { ...projeto, categorias }, localStorage.getItem('asq_token'));
            navigate(`/projeto/${projetoId}/categoria/${categoriaId}/subcategorias`);
        } catch (error) {
            setErro(error.message || 'Não foi possível adicionar a subcategoria');
        } finally {
            setCarregando(false);
        }
    }

    return <LayoutCoordenador><div className="flex min-h-[calc(100vh-156px)] items-start justify-center pt-10"><div className="w-full max-w-[1000px]">{erro && <p className="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p>}<SubcategoriaForm titulo="Adicionar Subcategoria" onSubmit={handleSubmit} onCancelar={() => navigate(projetoInicial ? '/adicionar-projeto/categoria' : `/projeto/${projetoId}/categoria/${categoriaId}/subcategorias`, projetoInicial ? { state: { projeto: projetoInicial } } : undefined)} carregando={carregando} /></div></div></LayoutCoordenador>;
}