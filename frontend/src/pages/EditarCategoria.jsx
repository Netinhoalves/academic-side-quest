import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import CategoriaForm from '../components/CategoriaForm';
import { getPpc, updatePpc } from '../services/api';

export default function EditarCategoria() {
    const navigate = useNavigate();
    const { projetoId, categoriaId } = useParams();
    const [projeto, setProjeto] = useState(null);
    const [erro, setErro] = useState('');
    const [carregando, setCarregando] = useState(false);

    useEffect(() => {
        getPpc(projetoId, localStorage.getItem('asq_token')).then(setProjeto).catch((error) => setErro(error.message || 'Não foi possível carregar a categoria'));
    }, [projetoId]);

    const categoria = projeto?.categorias.find((item) => String(item.id) === categoriaId);

    async function handleSubmit(event) {
        event.preventDefault();
        setCarregando(true);
        const dados = Object.fromEntries(new FormData(event.currentTarget));
        try {
            const categorias = projeto.categorias.map((item) => item.id === categoria.id ? { ...item, nome: dados.nome, descricao: dados.descricao, limite_total: Number(dados.limite_total), limite_semestre: Number(dados.limite_semestre) } : item);
            await updatePpc(projetoId, { ...projeto, categorias }, localStorage.getItem('asq_token'));
            navigate(`/projeto/${projetoId}/categorias`);
        } catch (error) {
            setErro(error.message || 'Não foi possível editar a categoria');
        } finally {
            setCarregando(false);
        }
    }

    return <LayoutCoordenador><div className="flex min-h-[calc(100vh-156px)] items-start justify-center pt-10"><div className="w-full max-w-[1000px]">{erro && <p className="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p>}{categoria && <CategoriaForm titulo="Editar Categoria" categoria={categoria} onSubmit={handleSubmit} onCancelar={() => navigate(`/projeto/${projetoId}/categorias`)} modoEdicao carregando={carregando} />}</div></div></LayoutCoordenador>;
}