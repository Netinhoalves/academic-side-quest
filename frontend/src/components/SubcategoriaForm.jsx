import { Plus, Trash2, Check, ArrowLeft } from 'lucide-react';
import { useState } from 'react';

const regraVazia = { titulo_exibicao: '', tipo: '', multiplicador: '', operacao: 'SOMA' };

export default function SubcategoriaForm({ titulo, subcategoria, onSubmit, onCancelar, carregando = false }) {
    const [regras, setRegras] = useState(() => subcategoria?.regras?.length ? subcategoria.regras.map((regra) => ({ ...regra, multiplicador: String(regra.multiplicador) })) : [regraVazia]);

    function alterarRegra(index, campo, valor) {
        setRegras((atuais) => atuais.map((regra, regraIndex) => regraIndex === index ? { ...regra, [campo]: valor } : regra));
    }

    function adicionarRegra() {
        setRegras((atuais) => [...atuais, { ...regraVazia }]);
    }

    function removerRegra(index) {
        setRegras((atuais) => atuais.filter((_, regraIndex) => regraIndex !== index));
    }

    function enviar(event) {
        event.preventDefault();
        const dados = Object.fromEntries(new FormData(event.currentTarget));
        onSubmit({
            nome: dados.nome,
            codigo: dados.codigo,
            descricao: dados.descricao,
            documentacao_pedida: dados.documentacao_pedida,
            limite_semestre: Number(dados.limite_semestre),
            regras: regras.map((regra) => ({
                titulo_exibicao: regra.titulo_exibicao,
                tipo: regra.tipo,
                multiplicador: Number(regra.multiplicador),
                operacao: regra.operacao,
                tipo_documento: dados.documentacao_pedida,
            })),
        });
    }

    return (
        <form onSubmit={enviar} className="w-full max-w-[1000px] rounded-lg bg-color-yellow px-8 py-6 shadow-sm">
            <h1 className="border-b-2 border-color-blue pb-2 text-2xl md:text-3xl">{titulo}</h1>
            <div className="mt-4 grid gap-3 md:grid-cols-[1fr_210px_210px]">
                <label className="text-lg">Título da subcategoria:
                    <input name="nome" required defaultValue={subcategoria?.nome || ''} placeholder="Título da subcategoria" className="mt-1 block h-10 w-full rounded-md bg-[#FFDBAD] px-2 text-base outline-none focus:ring-2 focus:ring-color-blue" />
                </label>
                <label className="text-lg">Código:
                    <input name="codigo" required defaultValue={subcategoria?.codigo || ''} placeholder="Código" className="mt-1 block h-10 w-full rounded-md bg-[#FFDBAD] px-2 text-base outline-none focus:ring-2 focus:ring-color-blue" />
                </label>
                <label className="text-lg">Máximo no semestre:
                    <input name="limite_semestre" required type="number" min="0.01" step="0.01" defaultValue={subcategoria?.limite_semestre || ''} placeholder="Ex: 30" className="mt-1 block h-10 w-full rounded-md bg-[#FFDBAD] px-2 text-base outline-none focus:ring-2 focus:ring-color-blue" />
                </label>
                <label className="text-lg md:col-span-3">Descrição da subcategoria:
                    <textarea name="descricao" defaultValue={subcategoria?.descricao || ''} placeholder="Descrição da subcategoria" rows="3" className="mt-1 block w-full resize-none rounded-md bg-[#FFDBAD] px-2 py-2 text-base outline-none focus:ring-2 focus:ring-color-blue" />
                </label>
                <label className="text-lg md:col-span-2">Documentação pedida:
                    <input name="documentacao_pedida" required defaultValue={subcategoria?.documentacao_pedida || ''} placeholder="Ex: Certificado/Declaração" className="mt-1 block h-10 w-full rounded-md bg-[#FFDBAD] px-2 text-base outline-none focus:ring-2 focus:ring-color-blue" />
                </label>
            </div>

            <div className="mt-6 border-t-2 border-color-blue pt-3">
                <div className="mb-2 flex items-center justify-between gap-3">
                    <h2 className="text-xl">Regras de pontuação</h2>
                    <button type="button" onClick={adicionarRegra} className="flex items-center gap-2 rounded-md bg-color-blue px-3 py-2 text-base text-white hover:bg-color-blue-light"><Plus size={17} /> Adicionar regra</button>
                </div>
                <div className="space-y-3">
                    {regras.map((regra, index) => <div key={index} className="grid gap-3 rounded-md bg-[#FFD394] p-3 md:grid-cols-[1.5fr_1fr_150px_180px_auto]">
                        <label className="text-base">Título de exibição:
                            <input required value={regra.titulo_exibicao} onChange={(event) => alterarRegra(index, 'titulo_exibicao', event.target.value)} placeholder="Ex: 5 pontos por atividade" className="mt-1 block h-9 w-full rounded-md bg-[#FFDBAD] px-2 outline-none focus:ring-2 focus:ring-color-blue" />
                        </label>
                        <label className="text-base">Tipo:
                            <input required value={regra.tipo} onChange={(event) => alterarRegra(index, 'tipo', event.target.value)} placeholder="Ex: atividade" className="mt-1 block h-9 w-full rounded-md bg-[#FFDBAD] px-2 outline-none focus:ring-2 focus:ring-color-blue" />
                        </label>
                        <label className="text-base">Multiplicador:
                            <input required type="number" min="0.01" step="0.01" value={regra.multiplicador} onChange={(event) => alterarRegra(index, 'multiplicador', event.target.value)} placeholder="Ex: 5" className="mt-1 block h-9 w-full rounded-md bg-[#FFDBAD] px-2 outline-none focus:ring-2 focus:ring-color-blue" />
                        </label>
                        <label className="text-base">Operação:
                            <select value={regra.operacao} onChange={(event) => alterarRegra(index, 'operacao', event.target.value)} className="mt-1 block h-9 w-full rounded-md bg-[#FFDBAD] px-2 outline-none focus:ring-2 focus:ring-color-blue">
                                <option value="SOMA">SOMA</option>
                                <option value="MULTIPLICACAO">MULTIPLICAÇÃO</option>
                            </select>
                        </label>
                        {regras.length > 1 && <button type="button" title="Remover regra" onClick={() => removerRegra(index)} className="mt-6 text-color-blue hover:text-red-700"><Trash2 size={20} /></button>}
                    </div>)}
                </div>
            </div>

            <div className="mt-4 flex justify-end gap-3">
                {onCancelar && <button type="button" onClick={onCancelar} className="flex items-center gap-2 rounded-md bg-color-blue px-5 py-2 text-lg text-white hover:bg-color-blue-light"><ArrowLeft size={18} /> Voltar</button>}
                <button type="submit" disabled={carregando || regras.length === 0} className="flex items-center gap-2 rounded-md bg-color-blue px-5 py-2 text-lg text-white hover:bg-color-blue-light disabled:cursor-not-allowed disabled:opacity-70"><Check size={18} /> {carregando ? 'Aguarde...' : 'Finalizar'}</button>
            </div>
        </form>
    );
}