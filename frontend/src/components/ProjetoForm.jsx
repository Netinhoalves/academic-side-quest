import FormularioEntidade from './FormularioEntidade';

const camposProjeto = [
    { name: 'id_curso', label: 'ID do curso', type: 'number', placeholder: 'ID do curso no banco' },
    { name: 'titulo', label: 'Título', placeholder: 'Título do PPC' },
    { name: 'ano', label: 'Ano', type: 'number', placeholder: 'Ano do PPC' },
    { name: 'pontos', label: 'Máximo de pontos', type: 'number', placeholder: 'Ex: 100' },
    { name: 'descricao', label: 'Descrição', type: 'textarea', placeholder: 'Descrição do projeto', fullWidth: true },
];

export default function ProjetoForm({ titulo, projeto, onSubmit, onCancelar, modoEdicao = false, carregando = false }) {
    return <FormularioEntidade titulo={titulo} campos={camposProjeto} valoresIniciais={projeto} modoEdicao={modoEdicao} onSubmit={onSubmit} onCancelar={onCancelar} carregando={carregando} />;
}