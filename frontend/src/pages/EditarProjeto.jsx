import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import ProjetoForm from '../components/ProjetoForm';
import { alterarAtivoPpc, getPpc, updatePpc } from '../services/api';

export default function EditarProjeto() {
    const navigate = useNavigate();
    const { id } = useParams();
    const [projeto, setProjeto] = useState(null);
    const [erro, setErro] = useState('');
    const [carregando, setCarregando] = useState(false);

    useEffect(() => {
        async function carregarProjeto() {
            try {
                setProjeto(await getPpc(id, localStorage.getItem('asq_token')));
            } catch (error) {
                setErro(error.message || 'Não foi possível carregar o projeto');
            }
        }

        carregarProjeto();
    }, [id]);

    async function handleSubmit(event) {
        event.preventDefault();
        setErro('');
        setCarregando(true);
        const dados = Object.fromEntries(new FormData(event.currentTarget));
        const ativo = event.currentTarget.elements.ativo.checked;
        try {
            await updatePpc(id, {
                ...projeto,
                id_curso: Number(dados.id_curso),
                nome: dados.titulo,
                ano: Number(dados.ano),
                descricao: dados.descricao,
                total_pontos: Number(dados.pontos),
            }, localStorage.getItem('asq_token'));

            if (ativo !== projeto.ativo) {
                await alterarAtivoPpc(id, ativo, localStorage.getItem('asq_token'));
            }
            navigate('/gerenciar-projetos');
        } catch (error) {
            setErro(error.message || 'Não foi possível editar o projeto');
        } finally {
            setCarregando(false);
        }
    }

    return (
        <LayoutCoordenador>
            <div className="flex min-h-[calc(100vh-156px)] items-start justify-center pt-10">
                {erro ? <p className="rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p> : projeto && <ProjetoForm titulo="Editar Projeto" projeto={{ ...projeto, titulo: projeto.nome, pontos: projeto.total_pontos }} onSubmit={handleSubmit} onCancelar={() => navigate('/gerenciar-projetos')} modoEdicao carregando={carregando} />}
            </div>
        </LayoutCoordenador>
    );
}