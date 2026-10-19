import { useNavigate } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import ProjetoForm from '../components/ProjetoForm';
import { createPpc } from '../services/api';

export default function AdicionarProjeto() {
    const navigate = useNavigate();

    async function handleSubmit(event) {
        event.preventDefault();
        const dados = Object.fromEntries(new FormData(event.currentTarget));
        await createPpc({
            id_curso: Number(dados.id_curso),
            nome: dados.titulo,
            ano: Number(dados.ano),
            descricao: dados.descricao,
            total_pontos: Number(dados.pontos),
        }, localStorage.getItem('asq_token'));
        navigate('/gerenciar-projetos');
    }

    return (
        <LayoutCoordenador>
            <div className="flex min-h-[calc(100vh-156px)] items-start justify-center pt-10">
                <ProjetoForm titulo="Adicionar Projeto" onSubmit={handleSubmit} />
            </div>
        </LayoutCoordenador>
    );
}