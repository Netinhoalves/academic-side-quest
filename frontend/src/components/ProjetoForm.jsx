import { Check, X } from 'lucide-react';

export default function ProjetoForm({ titulo, projeto, onSubmit, onCancelar, modoEdicao = false }) {
    return (
        <form onSubmit={onSubmit} className="w-full max-w-[1000px] rounded-lg bg-color-yellow px-8 py-6 shadow-sm">
            <h1 className="border-b-2 border-color-blue pb-2 text-2xl md:text-3xl">{titulo}</h1>

            <div className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_150px]">
                <label className="text-lg">
                    Título:
                    <input name="titulo" defaultValue={projeto?.titulo || ''} placeholder="Título do PPC" required className="mt-1 block h-10 w-full rounded-md bg-[#FFDBAD] px-2 text-base outline-none focus:ring-2 focus:ring-color-blue" />
                </label>
                <label className="text-lg">
                    Ano:
                    <input name="ano" type="number" defaultValue={projeto?.ano || ''} placeholder="Ano do PPC" required className="mt-1 block h-10 w-full rounded-md bg-[#FFDBAD] px-2 text-base outline-none focus:ring-2 focus:ring-color-blue" />
                </label>
                <label className="text-lg">
                    Máximo de pontos:
                    <input name="pontos" type="number" defaultValue={projeto?.pontos || ''} placeholder="Ex: 100" required className="mt-1 block h-10 w-full rounded-md bg-[#FFDBAD] px-2 text-base outline-none focus:ring-2 focus:ring-color-blue" />
                </label>
            </div>

            <label className="mt-2 block text-lg">
                Descrição:
                <textarea name="descricao" defaultValue={projeto?.descricao || ''} placeholder="Descrição do projeto" required rows="3" className="mt-1 block w-full resize-none rounded-md bg-[#FFDBAD] px-2 py-2 text-base outline-none focus:ring-2 focus:ring-color-blue" />
            </label>

            {modoEdicao && (
                <label className="mt-4 flex items-center gap-3 text-lg">
                    <input name="ativo" type="checkbox" defaultChecked={projeto?.ativo !== false} className="h-5 w-5 accent-color-blue" />
                    Projeto ativo
                </label>
            )}

            <div className="mt-4 flex justify-end gap-3">
                {modoEdicao && (
                    <button type="button" onClick={onCancelar} className="flex items-center gap-2 rounded-md bg-color-blue px-5 py-2 text-lg text-white hover:bg-color-blue-light">
                        <X size={18} /> Cancelar
                    </button>
                )}
                <button type="submit" className="flex items-center gap-2 rounded-md bg-color-blue px-5 py-2 text-lg text-white hover:bg-color-blue-light">
                    <Check size={18} /> Finalizar
                </button>
            </div>
        </form>
    );
}