import { useEffect, useState } from 'react';
import FormularioEntidade from './FormularioEntidade';
import { getCursos } from '../services/api';

export default function ProjetoForm({
    titulo,
    projeto,
    onSubmit,
    onCancelar,
    modoEdicao = false,
    carregando = false,
    submitLabel,
}) {
    const [opcoesCursos, setOpcoesCursos] = useState(null)
    useEffect(() => {
        getCursos()
            .then((lista) => {
                if (lista.length === 0) {
                    setOpcoesCursos([{ value: '', label: 'Nenhum curso cadastrado' }]);
                    return;
                }
                setOpcoesCursos(
                    lista.map((curso) => ({
                        value: String(curso.id),
                        label: `${curso.nome} (${curso.sigla})`,
                    }))
                );
            })
            .catch(() => {
                setOpcoesCursos([{ value: '', label: 'Erro ao carregar cursos' }]);
            });
    }, []);

const camposProjeto = [
{
        name: 'id_curso',
        label: 'Curso',
        type: 'select',
        options: opcoesCursos,
    },
    { name: 'titulo', label: 'Título', placeholder: 'Título do PPC' },
    { name: 'ano', label: 'Ano', type: 'number', min: 1900, max: 2100, placeholder: 'Ano do PPC' },
    { name: 'pontos', label: 'Máximo de pontos', type: 'number', min: 0.01, step: 0.01, placeholder: 'Ex: 100' },
    { name: 'descricao', label: 'Descrição', type: 'textarea', placeholder: 'Descrição do projeto', fullWidth: true, required: false },
];

    return (
        <FormularioEntidade titulo={titulo} campos={camposProjeto} valoresIniciais={projeto ? { ...projeto, id_curso: String(projeto.id_curso) } : undefined} modoEdicao={modoEdicao} onSubmit={onSubmit} onCancelar={onCancelar} carregando={carregando} submitLabel={submitLabel} />
    );
}