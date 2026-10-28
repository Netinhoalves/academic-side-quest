import { ArrowLeft, Check, X } from 'lucide-react';

export default function FormularioEntidade({
    titulo,
    campos,
    valoresIniciais = {},
    modoEdicao = false,
    onSubmit,
    onCancelar,
    carregando = false,
    mostrarAtivo = modoEdicao,
    submitLabel = 'Finalizar',
    mostrarVoltar = false,
}) {
    return (
        <form onSubmit={onSubmit} className="w-full max-w-[1000px] rounded-lg bg-color-yellow px-8 py-6 shadow-sm">
            <h1 className="border-b-2 border-color-blue pb-2 text-2xl md:text-3xl">{titulo}</h1>

            <div className="mt-4 grid gap-3 md:grid-cols-2">
                {campos.map((campo) => (
                    <label key={campo.name} className={`text-lg ${campo.fullWidth ? 'md:col-span-2' : ''}`}>
                        {campo.label}:
                        {campo.type === 'textarea' ? (
                            <textarea name={campo.name} defaultValue={valoresIniciais[campo.name] || ''} placeholder={campo.placeholder} required={campo.required !== false} rows="3" className="mt-1 block w-full resize-none rounded-md bg-[#FFDBAD] px-2 py-2 text-base outline-none focus:ring-2 focus:ring-color-blue" />
                        ) : campo.type === 'select' ? (
                            <select name={campo.name} defaultValue={valoresIniciais[campo.name] || campo.options[0].value} required={campo.required !== false} className="mt-1 block h-10 w-full rounded-md bg-[#FFDBAD] px-2 text-base outline-none focus:ring-2 focus:ring-color-blue">
                                {campo.options.map((opcao) => <option key={opcao.value} value={opcao.value}>{opcao.label}</option>)}
                            </select>
                        ) : (
                            <input name={campo.name} type={campo.type || 'text'} min={campo.min} max={campo.max} step={campo.step} defaultValue={valoresIniciais[campo.name] || ''} placeholder={campo.placeholder} required={campo.required !== false} className="mt-1 block h-10 w-full rounded-md bg-[#FFDBAD] px-2 text-base outline-none focus:ring-2 focus:ring-color-blue" />
                        )}
                    </label>
                ))}
            </div>

            {mostrarAtivo && (
                <label className="mt-4 flex items-center gap-3 text-lg">
                    <input name="ativo" type="checkbox" defaultChecked={valoresIniciais.ativo !== false} className="h-5 w-5 accent-color-blue" />
                    Ativo
                </label>
            )}

            <div className="mt-4 flex justify-end gap-3">
                {(modoEdicao || mostrarVoltar) && onCancelar && (
                    <button type="button" onClick={onCancelar} className="flex items-center gap-2 rounded-md bg-color-blue px-5 py-2 text-lg text-white hover:bg-color-blue-light">
                        {modoEdicao ? <X size={18} /> : <ArrowLeft size={18} />} {modoEdicao ? 'Cancelar' : 'Voltar'}
                    </button>
                )}
                <button type="submit" disabled={carregando} className="flex items-center gap-2 rounded-md bg-color-blue px-5 py-2 text-lg text-white hover:bg-color-blue-light disabled:cursor-not-allowed disabled:opacity-70">
                    <Check size={18} /> {carregando ? 'Aguarde...' : submitLabel}
                </button>
            </div>
        </form>
    );
}
