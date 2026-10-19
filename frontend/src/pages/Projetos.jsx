import { useNavigate } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import ListaEntidades from '../components/ListaEntidades';
import { carregarProjetos } from '../services/projetosMock';

export default function Projetos() {
    const navigate = useNavigate();
    const projetos = carregarProjetos();

    return (
        <LayoutCoordenador>
            <ListaEntidades
                titulo="Projetos"
                itens={projetos}
                onAdicionar={() => navigate('/adicionar-projeto')}
                onEditar={(id) => navigate(`/editar-projeto/${id}`)}
                renderTitulo={(projeto) => <>{projeto.titulo}<span className="mx-3 text-lg font-normal">•</span><span className="text-lg font-normal">{projeto.ano}</span>{projeto.ativo === false && <span className="ml-3 text-lg font-normal">Inativo</span>}</>}
                renderDescricao={(projeto) => projeto.descricao}
                renderExtra={(projeto) => <span className="shrink-0 text-lg">{projeto.pontos} pontos</span>}
                renderAcoes={() => <><button type="button" className="block w-full px-4 py-2 text-left hover:bg-[#FFDBAD]">Gerenciar categorias</button><button type="button" className="block w-full px-4 py-2 text-left hover:bg-[#FFDBAD]">Gerenciar alunos</button></>}
                itemInativo={(projeto) => projeto.ativo === false}
            />
        </LayoutCoordenador>
    );
}