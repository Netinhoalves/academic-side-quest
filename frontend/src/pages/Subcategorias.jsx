import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import ListaEntidades from '../components/ListaEntidades';
import { getPpc } from '../services/api';

export default function Subcategorias() {
    const navigate = useNavigate();
    const { projetoId, categoriaId } = useParams();
    const [projeto, setProjeto] = useState(null);
    const [erro, setErro] = useState('');
    const categoria = projeto?.categorias.find((item) => String(item.id) === categoriaId);

    useEffect(() => {
        getPpc(projetoId, localStorage.getItem('asq_token')).then(setProjeto).catch((error) => setErro(error.message || 'Não foi possível carregar as subcategorias'));
    }, [projetoId]);

    return <LayoutCoordenador>
        {erro && <p className="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p>}
        {categoria && <ListaEntidades
            titulo={`Subcategorias - ${categoria.nome}`}
            textoAdicionar="Subcategoria"
            itens={categoria.subcategorias || []}
            onAdicionar={() => navigate(`/projeto/${projetoId}/categoria/${categoriaId}/subcategorias/adicionar`)}
            onEditar={(id) => navigate(`/projeto/${projetoId}/categoria/${categoriaId}/subcategorias/${id}/editar`)}
            renderTitulo={(subcategoria) => <><span className="mr-3">{subcategoria.codigo}</span>{subcategoria.nome}</>}
            renderDescricao={(subcategoria) => subcategoria.documentacao_pedida}
            renderExtra={(subcategoria) => <span className="shrink-0 text-lg">{subcategoria.limite_semestre} pontos</span>}
            renderAcoes={(subcategoria) => <span className="block px-4 py-2 text-left">{subcategoria.regras?.length || 0} regra(s) de pontuação</span>}
        />}
        {categoria && categoria.subcategorias?.length === 0 && <p className="mt-4 rounded-md bg-[#FFDBAD] px-4 py-3 text-lg">Nenhuma subcategoria foi criada para esta categoria.</p>}
    </LayoutCoordenador>;
}