import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import SubcategoriaForm from '../components/SubcategoriaForm';
import { getPpc, updatePpc } from '../services/api';

export default function EditarSubcategoria() {
    const navigate = useNavigate();
    const { projetoId, categoriaId, subcategoriaId } = useParams();
    const [projeto, setProjeto] = useState(null);
    const [erro, setErro] = useState('');
    const [carregando, setCarregando] = useState(false);

    useEffect(() => {
        getPpc(projetoId, localStorage.getItem('asq_token'))
            .then(setProjeto)
            .catch((error) => setErro(error.message || 'Não foi possível carregar a subcategoria'));
    }, [projetoId]);

    const categoria = projeto?.categorias.find((item) => String(item.id) === categoriaId);
    const subcategoria = categoria?.subcategorias.find((item) => String(item.id) === subcategoriaId);

    async function handleSubmit(dados) {
        setErro('');
        setCarregando(true);
        try {
            const categorias = projeto.categorias.map((item) => item.id === categoria.id
                ? { ...item, subcategorias: item.subcategorias.map((subitem) => subitem.id === subcategoria.id ? dados : subitem) }
                : item);
            const atualizado = await updatePpc(projetoId, { ...projeto, categorias }, localStorage.getItem('asq_token'));
            // o PUT recria a árvore do PPC com ids novos: a categoria continua na mesma posição
            const indice = projeto.categorias.findIndex((item) => item.id === categoria.id);
            navigate(`/projeto/${projetoId}/categoria/${atualizado.categorias[indice].id}/subcategorias`);
        } catch (error) {
            setErro(error.message || 'Não foi possível editar a subcategoria');
        } finally {
            setCarregando(false);
        }
    }

    return <LayoutCoordenador><div className="flex min-h-[calc(100vh-156px)] items-start justify-center pt-10"><div className="w-full max-w-[1000px]">{erro && <p className="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p>}{subcategoria && <SubcategoriaForm titulo="Editar Subcategoria" subcategoria={subcategoria} onSubmit={handleSubmit} onCancelar={() => navigate(`/projeto/${projetoId}/categoria/${categoriaId}/subcategorias`)} carregando={carregando} />}</div></div></LayoutCoordenador>;
}