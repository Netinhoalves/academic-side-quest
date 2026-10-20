import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import ProjetoForm from '../components/ProjetoForm';
import { createPpc } from '../services/api';

export default function AdicionarProjeto() {
    const navigate = useNavigate();
    const [erro, setErro] = useState('');
    const [carregando, setCarregando] = useState(false);

    async function handleSubmit(event) {
        event.preventDefault();
        setErro('');
        setCarregando(true);
        const dados = Object.fromEntries(new FormData(event.currentTarget));
        try {
            await createPpc({
                id_curso: Number(dados.id_curso),
                nome: dados.titulo,
                ano: Number(dados.ano),
                descricao: dados.descricao,
                total_pontos: Number(dados.pontos),
                categorias: [],
            }, localStorage.getItem('asq_token'));
            navigate('/gerenciar-projetos');
        } catch (error) {
            setErro(error.message || 'Não foi possível adicionar o projeto');
        } finally {
            setCarregando(false);
        }
    }

    return (
        <LayoutCoordenador>
            <div className="flex min-h-[calc(100vh-156px)] items-start justify-center pt-10">
                <div className="w-full max-w-[1000px]">
                    {erro && <p className="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p>}
                    <ProjetoForm titulo="Adicionar Projeto" onSubmit={handleSubmit} carregando={carregando} />
                </div>
            </div>
        </LayoutCoordenador>
    );
}