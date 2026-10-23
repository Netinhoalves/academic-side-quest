import FormularioEntidade from './FormularioEntidade';

const camposCategoria = [
    { name: 'nome', label: 'Título da categoria', placeholder: 'Título da categoria' },
    { name: 'limite_total', label: 'Máximo de pontos no curso', type: 'number', placeholder: 'Ex: 100' },
    { name: 'descricao', label: 'Descrição da categoria', type: 'textarea', placeholder: 'Descrição da categoria', fullWidth: true, required: false },
    { name: 'limite_semestre', label: 'Máximo de pontos no semestre', type: 'number', placeholder: 'Ex: 25' },
];

export default function CategoriaForm({ titulo, categoria, onSubmit, onCancelar, modoEdicao = false, carregando = false, mostrarVoltar = false, submitLabel }) {
    return <FormularioEntidade
        titulo={titulo}
        campos={camposCategoria}
        valoresIniciais={categoria}
        modoEdicao={modoEdicao}
        mostrarAtivo={false}
        onSubmit={onSubmit}
        onCancelar={onCancelar}
        carregando={carregando}
        submitLabel={submitLabel || (categoria ? 'Finalizar' : 'Continuar')}
        mostrarVoltar={mostrarVoltar}
    />;
}