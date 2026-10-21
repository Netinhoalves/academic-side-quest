import { ChevronDown, Plus } from 'lucide-react';

export default function ListaEntidades({
    titulo,
    itens,
    onAdicionar,
    onEditar,
    renderTitulo,
    renderDescricao,
    renderExtra,
    renderAcoes,
    itemInativo,
    podeEditar,
    mostrarAdicionar = true,
}) {
    return (
        <section className="mx-auto w-full max-w-[1250px]">
            <div className="mb-2 flex items-center justify-between gap-4">
                <h1 className="text-4xl md:text-5xl">{titulo}</h1>
                {mostrarAdicionar && <button type="button" onClick={onAdicionar} className="flex shrink-0 items-center gap-2 rounded-md bg-color-blue px-5 py-3 text-lg text-white shadow-sm hover:bg-color-blue-light">
                    <Plus size={21} /> Adicionar {titulo.slice(0, -1)}
                </button>}
            </div>

            <div className="rounded-lg shadow-md">
                {itens.map((item, index) => {
                    const inativo = itemInativo?.(item) ?? false;
                    const estiloLinha = inativo
                        ? 'bg-gray-300 text-gray-500'
                        : index % 2 === 0 ? 'bg-color-yellow' : 'bg-[#FFD394]';

                    return (
                        <div key={item.id} className={`relative flex items-center gap-4 px-5 py-3 ${estiloLinha} ${index === 0 ? 'rounded-t-lg' : ''} ${index === itens.length - 1 ? 'rounded-b-lg' : ''}`}>
                            <span className={`h-4 w-4 shrink-0 rounded-full ${inativo ? 'bg-gray-500' : 'bg-color-blue'}`} />
                            <span className="min-w-0 flex-1">
                                <strong className="block truncate text-2xl">{renderTitulo(item)}</strong>
                                <small className="block truncate text-base">{renderDescricao(item)}</small>
                            </span>

                            {renderExtra?.(item)}

                            <EntityActions
                                item={item}
                                inativo={inativo}
                                onEditar={onEditar}
                                podeEditar={podeEditar?.(item) ?? true}
                                renderAcoes={renderAcoes}
                            />
                        </div>
                    );
                })}
            </div>
        </section>
    );
}

function EntityActions({ item, inativo, onEditar, podeEditar, renderAcoes }) {
    return (
        <div className="relative shrink-0">
            <details className="group">
                <summary className={`flex cursor-pointer list-none items-center gap-3 rounded-md px-5 py-2 text-lg text-white ${inativo ? 'bg-gray-500 hover:bg-gray-600' : 'bg-color-blue hover:bg-color-blue-light'}`}>
                    Ações <ChevronDown size={20} />
                </summary>
                <div onClick={(event) => { event.currentTarget.parentElement.open = false; }} className="absolute right-0 top-full z-20 mt-1 min-w-[220px] rounded-md bg-color-creme py-2 text-lg text-color-blue shadow-lg">
                    {renderAcoes?.(item)}
                    {podeEditar && <button type="button" onClick={() => onEditar(item.id)} className="block w-full px-4 py-2 text-left hover:bg-[#FFDBAD]">Editar</button>}
                </div>
            </details>
        </div>
    );
}
