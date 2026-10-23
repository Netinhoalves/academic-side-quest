import FormularioEntidade from './FormularioEntidade';

const camposCurso = [
    { name: 'nome', label: 'Nome do curso', placeholder: 'Ex: Tecnologia em Análise e Desenvolvimento de Sistemas' },
    { name: 'sigla', label: 'Sigla', placeholder: 'Ex: TADS' },
    { name: 'instituicao', label: 'Instituição', placeholder: 'Ex: IFMS - Campus Três Lagoas', fullWidth: true },
];

export default function CursoForm({
    titulo,
    curso,
    onSubmit,
    onCancelar,
    modoEdicao = false,
    carregando = false,
    mostrarVoltar = false,
    submitLabel,
}) {
    return (
        <FormularioEntidade
            titulo={titulo}
            campos={camposCurso}
            valoresIniciais={curso}
            modoEdicao={modoEdicao}
            mostrarAtivo={false}
            onSubmit={onSubmit}
            onCancelar={onCancelar}
            carregando={carregando}
            mostrarVoltar={mostrarVoltar}
            submitLabel={submitLabel}
        />
    );
}