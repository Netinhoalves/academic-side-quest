import { useNavigate } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import ProjetoForm from '../components/ProjetoForm';
import { carregarProjetos, salvarProjetos } from '../services/projetosMock';

export default function AdicionarProjeto() {
    const navigate = useNavigate();

    function handleSubmit(event) {
        event.preventDefault();
        const dados = Object.fromEntries(new FormData(event.currentTarget));
        const projetos = carregarProjetos();
        salvarProjetos([...projetos, { ...dados, id: `${Date.now()}`, curso: 'Tecnologia em analise e desenvolvimento de sistemas - 1' }]);
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