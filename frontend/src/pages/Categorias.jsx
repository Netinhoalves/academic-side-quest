import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import ListaEntidades from '../components/ListaEntidades';
import { getPpc } from '../services/api';

export default function Categorias() {
    const navigate = useNavigate();
    const { projetoId } = useParams();
    const [projeto, setProjeto] = useState(null);
    const [erro, setErro] = useState('');

    useEffect(() => {
        getPpc(projetoId, localStorage.getItem('asq_token'))
            .then(setProjeto)
            .catch((error) => setErro(error.message || 'Não foi possível carregar as categorias'));
    }, [projetoId]);

    return (
        <LayoutCoordenador>
            {erro && <p className="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p>}
            {projeto && <ListaEntidades
                titulo="Categorias"
                itens={projeto.categorias || []}
                onAdicionar={() => navigate(`/projeto/${projetoId}/categorias/adicionar`)}
                onEditar={(id) => navigate(`/projeto/${projetoId}/categorias/${id}/editar`)}
                renderTitulo={(categoria) => categoria.nome}
                renderDescricao={(categoria) => categoria.descricao || 'Sem descrição cadastrada'}
                renderExtra={(categoria) => <span className="shrink-0 text-lg">{categoria.limite_total} pontos</span>}
                renderAcoes={(categoria) => <button type="button" onClick={() => navigate(`/projeto/${projetoId}/categoria/${categoria.id}/subcategorias`)} className="block w-full px-4 py-2 text-left hover:bg-[#FFDBAD]">Gerenciar subcategorias</button>}
            />}
            {projeto && projeto.categorias?.length === 0 && <p className="mt-4 rounded-md bg-[#FFDBAD] px-4 py-3 text-lg">Nenhuma categoria foi criada para este projeto.</p>}
        </LayoutCoordenador>
    );
}