import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LayoutCoordenador from '../components/LayoutCoordenador';
import ListaEntidades from '../components/ListaEntidades';
import { deleteCurso, getCursos } from '../services/api';

export default function Cursos() {
    const navigate = useNavigate();
    const [cursos, setCursos] = useState([]);
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState('');

    useEffect(() => {
        document.title = 'Gerenciar Cursos | Academic Side Quest';
        getCursos()
            .then(setCursos)
            .catch((error) => setErro(error.message || 'Não foi possível carregar os cursos'))
            .finally(() => setCarregando(false));
    }, []);

    async function handleDesativar(curso) {
        setErro('');
        try {
            await deleteCurso(curso.id, localStorage.getItem('asq_token'));
            setCursos((atuais) => atuais.filter((item) => item.id !== curso.id));
        } catch (error) {
            setErro(error.message || 'Não foi possível desativar o curso');
        }
    }

    return (
        <LayoutCoordenador>
            {erro && <p className="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-700">{erro}</p>}
            {carregando ? (
                <p>Carregando cursos...</p>
            ) : (
                <ListaEntidades
                    titulo="Cursos"
                    textoAdicionar="Curso"
                    itens={cursos}
                    onAdicionar={() => navigate('/adicionar-curso')}
                    onEditar={(id) => navigate(`/editar-curso/${id}`)}
                    renderTitulo={(curso) => (
                        <>
                            {curso.nome}
                            <span className="mx-3 text-lg font-normal">•</span>
                            <span className="text-lg font-normal">{curso.sigla}</span>
                        </>
                    )}
                    renderDescricao={(curso) => curso.instituicao}
                    renderAcoes={(curso) => (
                        <button
                            type="button"
                            onClick={() => handleDesativar(curso)}
                            className="block w-full px-4 py-2 text-left text-red-700 hover:bg-[#FFDBAD]"
                        >
                            Desativar
                        </button>
                    )}
                />
            )}
            {!carregando && cursos.length === 0 && (
                <p className="mt-4 rounded-md bg-[#FFDBAD] px-4 py-3 text-lg">
                    Nenhum curso cadastrado no momento.
                </p>
            )}
        </LayoutCoordenador>
    );
}