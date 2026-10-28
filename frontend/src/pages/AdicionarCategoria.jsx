import { useNavigate, useParams, useLocation } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import CategoriaForm from '../components/CategoriaForm';

export default function AdicionarCategoria() {
    const navigate = useNavigate();
    const { projetoId } = useParams();
    const location = useLocation();
    const projetoInicial = location.state?.projeto;

    function voltar() {
        if (projetoInicial) {
            navigate('/adicionar-projeto', { state: { projeto: projetoInicial } });
            return;
        }

        navigate(`/projeto/${projetoId}/categorias`);
    }

    function handleSubmit(event) {
        event.preventDefault();
        const dados = Object.fromEntries(new FormData(event.currentTarget));
        const categoria = {
            nome: dados.nome,
            descricao: dados.descricao || null,
            limite_total: Number(dados.limite_total),
            limite_semestre: Number(dados.limite_semestre),
        };
        navigate(projetoInicial ? '/adicionar-projeto/subcategoria' : `/projeto/${projetoId}/categorias/adicionar/subcategoria`, {
            state: {
                projeto: projetoInicial,
                categoria,
            },
        });
    }

    return <LayoutCoordenador><div className="flex min-h-[calc(100vh-156px)] items-start justify-center pt-10"><div className="w-full max-w-[1000px]"><CategoriaForm titulo="Adicionar Categoria" onSubmit={handleSubmit} onCancelar={voltar} mostrarVoltar /></div></div></LayoutCoordenador>;
}