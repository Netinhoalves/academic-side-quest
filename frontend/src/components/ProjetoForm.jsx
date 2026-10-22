import FormularioEntidade from './FormularioEntidade';

const camposProjeto = [
    { name: 'id_curso', label: 'ID do curso', type: 'number', min: 1, step: 1, placeholder: 'ID do curso no banco' },
    { name: 'titulo', label: 'Título', placeholder: 'Título do PPC' },
    { name: 'ano', label: 'Ano', type: 'number', min: 1900, max: 2100, placeholder: 'Ano do PPC' },
    { name: 'pontos', label: 'Máximo de pontos', type: 'number', min: 0.01, step: 0.01, placeholder: 'Ex: 100' },
    { name: 'descricao', label: 'Descrição', type: 'textarea', placeholder: 'Descrição do projeto', fullWidth: true, required: false },
];

export default function ProjetoForm({ titulo, projeto, onSubmit, onCancelar, modoEdicao = false, carregando = false, submitLabel }) {
    return <FormularioEntidade titulo={titulo} campos={camposProjeto} valoresIniciais={projeto} modoEdicao={modoEdicao} onSubmit={onSubmit} onCancelar={onCancelar} carregando={carregando} submitLabel={submitLabel} />;
}