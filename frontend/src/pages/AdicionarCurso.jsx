import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import CursoForm from '../components/CursoForm';
import { createCurso } from '../services/api';

export default function AdicionarCurso() {
    const navigate = useNavigate();
    const [erro, setErro] = useState('');
    const [carregando, setCarregando] = useState(false);

    useEffect(() => {
        document.title = 'Adicionar Curso | Academic Side Quest';
    }, []);

    async function handleSubmit(event) {
        event.preventDefault();
        setErro('');
        setCarregando(true);

        const dados = Object.fromEntries(new FormData(event.currentTarget));

        try {
            await createCurso(
                {
                    nome: dados.nome,
                    sigla: dados.sigla,
                    instituicao: dados.instituicao,
                },
                localStorage.getItem('asq_token')
            );
            navigate('/gerenciar-cursos');
        } catch (error) {
            setErro(error.message || 'Não foi possível cadastrar o curso');
        } finally {
            setCarregando(false);
        }
    }

    return (
        <LayoutCoordenador>
            <div className="flex min-h-[calc(100vh-156px)] items-start justify-center pt-10">
                <div className="w-full max-w-[1000px]">
                    {erro && <p className="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p>}
                    <CursoForm
                        titulo="Adicionar Curso"
                        onSubmit={handleSubmit}
                        onCancelar={() => navigate('/gerenciar-cursos')}
                        mostrarVoltar
                        carregando={carregando}
                    />
                </div>
            </div>
        </LayoutCoordenador>
    );
}