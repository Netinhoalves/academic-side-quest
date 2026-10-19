import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import ListaEntidades from '../components/ListaEntidades';
import { getPpcs } from '../services/api';

export default function Projetos() {
    const navigate = useNavigate();
    const [projetos, setProjetos] = useState([]);
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState('');

    useEffect(() => {
        const token = localStorage.getItem('asq_token');

        getPpcs(token)
            .then(setProjetos)
            .catch((error) => setErro(error.message || 'Não foi possível carregar os projetos'))
            .finally(() => setCarregando(false));
    }, []);

    return (
        <LayoutCoordenador>
            {erro && <p className="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p>}
            {carregando ? <p>Carregando projetos...</p> : <ListaEntidades
                titulo="Projetos"
                itens={projetos}
                onAdicionar={() => navigate('/adicionar-projeto')}
                onEditar={(id) => navigate(`/editar-projeto/${id}`)}
                renderTitulo={(projeto) => <>{projeto.nome}<span className="mx-3 text-lg font-normal">•</span><span className="text-lg font-normal">{projeto.ano}</span>{projeto.ativo === false && <span className="ml-3 text-lg font-normal">Inativo</span>}</>}
                renderDescricao={(projeto) => projeto.descricao}
                renderExtra={(projeto) => <span className="shrink-0 text-lg">{projeto.total_pontos} pontos</span>}
                renderAcoes={() => <><button type="button" className="block w-full px-4 py-2 text-left hover:bg-[#FFDBAD]">Gerenciar categorias</button><button type="button" className="block w-full px-4 py-2 text-left hover:bg-[#FFDBAD]">Gerenciar alunos</button></>}
                itemInativo={(projeto) => projeto.ativo === false}
            />}
        </LayoutCoordenador>
    );
}