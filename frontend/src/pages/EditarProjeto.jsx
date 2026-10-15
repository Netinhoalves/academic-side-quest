import { useNavigate, useParams } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import ProjetoForm from '../components/ProjetoForm';
import { carregarProjetos, salvarProjetos } from '../services/projetosMock';

export default function EditarProjeto() {
    const navigate = useNavigate();
    const { id } = useParams();
    const projeto = carregarProjetos().find((item) => item.id === id);

    function handleSubmit(event) {
        event.preventDefault();
        const dados = Object.fromEntries(new FormData(event.currentTarget));
        dados.ativo = event.currentTarget.elements.ativo.checked;
        const projetos = carregarProjetos().map((item) => item.id === id ? { ...item, ...dados } : item);
        salvarProjetos(projetos);
        navigate('/gerenciar-projetos');
    }

    return (
        <LayoutCoordenador>
            <div className="flex min-h-[calc(100vh-156px)] items-start justify-center pt-10">
                <ProjetoForm titulo="Editar Projeto" projeto={projeto} onSubmit={handleSubmit} onCancelar={() => navigate('/gerenciar-projetos')} modoEdicao />
            </div>
        </LayoutCoordenador>
    );
}