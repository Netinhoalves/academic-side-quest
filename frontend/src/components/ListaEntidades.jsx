import { ChevronDown, Plus } from 'lucide-react';
import { useRef, useState } from 'react';
import useFecharAoClicarFora from '../hooks/useFecharAoClicarFora';

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
    textoAdicionar,
}) {
    const [acaoAberta, setAcaoAberta] = useState(null);

    return (
        <section className="mx-auto w-full max-w-[1250px]">
            <div className="mb-2 flex flex-wrap items-center justify-between gap-4">
                <h1 className="min-w-0 break-words text-4xl md:text-5xl">{titulo}</h1>
                {mostrarAdicionar && <button type="button" onClick={onAdicionar} className="flex shrink-0 items-center gap-2 rounded-md bg-color-blue px-5 py-3 text-lg text-white shadow-sm hover:bg-color-blue-light">
                    <Plus size={21} /> Adicionar {textoAdicionar || titulo.slice(0, -1)}
                </button>}
            </div>

            <div className="rounded-lg shadow-md">
                {itens.map((item, index) => {
                    const inativo = itemInativo?.(item) ?? false;
                    const isUltimo = index === itens.length - 1;
                    const estiloLinha = inativo
                        ? 'bg-gray-300 text-gray-500'
                        : index % 2 === 0 ? 'bg-color-yellow' : 'bg-[#FFD394]';

                    return (
                        <div key={item.id} className={`relative flex flex-wrap items-center gap-x-4 gap-y-2 px-5 py-3 ${estiloLinha} ${index === 0 ? 'rounded-t-lg' : ''} ${isUltimo ? 'rounded-b-lg' : ''}`}>
                            <div className="flex min-w-0 grow basis-72 items-center gap-4">
                                <span className={`h-4 w-4 shrink-0 rounded-full ${inativo ? 'bg-gray-500' : 'bg-color-blue'}`} />
                                <span className="min-w-0 flex-1">
                                    <strong className="line-clamp-2 text-2xl md:line-clamp-1">{renderTitulo(item)}</strong>
                                    <small className="line-clamp-2 text-base md:line-clamp-1">{renderDescricao(item)}</small>
                                </span>
                            </div>

                            <div className="ml-auto flex shrink-0 items-center gap-4">
                                {renderExtra?.(item)}

                                <EntityActions
                                    item={item}
                                    inativo={inativo}
                                    onEditar={onEditar}
                                    podeEditar={podeEditar?.(item) ?? true}
                                    renderAcoes={renderAcoes}
                                    aberta={acaoAberta === item.id}
                                    onAlternar={() => setAcaoAberta((atual) => atual === item.id ? null : item.id)}
                                    onFechar={() => setAcaoAberta(null)}
                                />
                            </div>
                        </div>
                    );
                })}
            </div>
        </section>
    );
}

function EntityActions({ item, inativo, onEditar, podeEditar, renderAcoes, aberta, onAlternar, onFechar }) {
    const menuRef = useRef(null);
    const [paraCima, setParaCima] = useState(false);

    useFecharAoClicarFora(menuRef, onFechar, aberta);

    function alternar() {
        if (!aberta) {
            const botao = menuRef.current.getBoundingClientRect();
            const alturaMenu = menuRef.current.lastElementChild.offsetHeight;
            const espacoAbaixo = document.documentElement.scrollHeight - (botao.bottom + window.scrollY);
            setParaCima(espacoAbaixo < alturaMenu + 8);
        }
        onAlternar();
    }

    const alinhamentoMenu = paraCima ? 'bottom-full mb-1 origin-bottom-right' : 'top-full mt-1 origin-top-right';
    const animacaoFechado = paraCima ? 'translate-y-2' : '-translate-y-2';

    return (
        <div ref={menuRef} className="relative shrink-0">
            <button type="button" onClick={alternar} className={`flex cursor-pointer items-center gap-3 rounded-md px-5 py-2 text-lg text-white transition-colors ${inativo ? 'bg-gray-500 hover:bg-gray-600' : 'bg-color-blue hover:bg-color-blue-light'}`}>
                Ações <ChevronDown size={20} className={`transition-transform duration-200 ${aberta ? 'rotate-180' : ''}`} />
            </button>
            <div onClick={onFechar} className={`absolute right-0 z-50 min-w-[220px] rounded-md bg-color-creme py-2 text-lg text-color-blue shadow-lg transition-all duration-200 ${alinhamentoMenu} ${aberta ? 'pointer-events-auto translate-y-0 scale-100 opacity-100' : `pointer-events-none scale-95 opacity-0 ${animacaoFechado}`}`}>
                {renderAcoes?.(item)}
                {podeEditar && (
                    <button type="button" onClick={() => { onFechar(); onEditar(item.id); }} className="block w-full px-4 py-2 text-left hover:bg-[#FFDBAD]">
                        Editar
                    </button>
                )}
            </div>
        </div>
    );
}
