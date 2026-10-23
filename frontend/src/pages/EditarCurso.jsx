import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import CursoForm from '../components/CursoForm';
import { getCursos, updateCurso } from '../services/api';

export default function EditarCurso() {
    const navigate = useNavigate();
    const { id } = useParams();
    const [curso, setCurso] = useState(null);
    const [erro, setErro] = useState('');
    const [carregando, setCarregando] = useState(false);

    useEffect(() => {
        document.title = 'Editar Curso | Academic Side Quest';
        getCursos()
            .then((lista) => {
                const encontrado = lista.find((item) => String(item.id) === id);
                if (!encontrado) {
                    setErro('Curso não encontrado');
                    return;
                }
                setCurso(encontrado);
            })
            .catch((error) => setErro(error.message || 'Não foi possível carregar o curso'));
    }, [id]);

    async function handleSubmit(event) {
        event.preventDefault();
        setErro('');
        setCarregando(true);

        const dados = Object.fromEntries(new FormData(event.currentTarget));

        try {
            await updateCurso(
                id,
                {
                    nome: dados.nome,
                    sigla: dados.sigla,
                    instituicao: dados.instituicao,
                },
                localStorage.getItem('asq_token')
            );
            navigate('/gerenciar-cursos');
        } catch (error) {
            setErro(error.message || 'Não foi possível atualizar o curso');
        } finally {
            setCarregando(false);
        }
    }

    return (
        <LayoutCoordenador>
            <div className="flex min-h-[calc(100vh-156px)] items-start justify-center pt-10">
                <div className="w-full max-w-[1000px]">
                    {erro && <p className="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p>}
                    {curso && (
                        <CursoForm
                            titulo="Editar Curso"
                            curso={curso}
                            onSubmit={handleSubmit}
                            onCancelar={() => navigate('/gerenciar-cursos')}
                            modoEdicao
                            carregando={carregando}
                        />
                    )}
                </div>
            </div>
        </LayoutCoordenador>
    );
}