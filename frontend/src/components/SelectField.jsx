import { Funnel } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

export function SelectField({label, name, id, options, required, className = '', value, onChange, placeholderLabel = 'Selecione...', ...props}) {
    const rootRef = useRef(null);
    const [interno, setInterno] = useState('');
    const [aberto, setAberto] = useState(false);

    const controlado = value !== undefined;
    const valorAtual = controlado ? value : interno;
    const opcaoAtual = options.find((opt) => opt.value === valorAtual);

    useEffect(() => {
        const handleClickFora = (event) => {
            if (rootRef.current && !rootRef.current.contains(event.target)) {
                setAberto(false);
            }
        };

        window.addEventListener('mousedown', handleClickFora);

        return () => window.removeEventListener('mousedown', handleClickFora);
    }, []);

    const selecionar = (novoValor) => {
        if (!controlado) {
            setInterno(novoValor);
        }

        if (onChange) {
            onChange({ target: { value: novoValor, name, id } });
        }

        setAberto(false);
    };

    return (
        <div ref={rootRef} className={`flex flex-col w-full max-w-[442px] relative ${label ? 'mb-3' : 'mb-0'}`}>
            {label && (
                <label htmlFor={id} className="text-color-blue font-bold text-base sm:text-lg mb-1 flex items-center font-jaro">
                    {required && <span className="text-color-red mr-1">*</span>} {label}
                </label>
            )}

            <input type="hidden" name={name} value={valorAtual} required={required} />

            <button
                type="button"
                id={id}
                aria-label={label || id}
                aria-haspopup="listbox"
                aria-expanded={aberto}
                onClick={() => setAberto((atual) => !atual)}
                className={`w-full relative text-left appearance-none bg-[#ffd08b] rounded-[10px] px-3 py-2 sm:py-3 pr-10
                           text-gray-900 font-jaro outline-none focus:ring-2 focus:ring-color-blue transition-shadow shadow-[inset_0_4px_8px_rgba(0,0,0,0.15)] ${className}`}
                {...props}
            >
                <span className="text-[#172B68]">
                    {opcaoAtual?.label || placeholderLabel}
                </span>

                <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-color-blue">
                    <Funnel aria-hidden="true" className="h-4 w-4" />
                </span>
            </button>

            {aberto && (
                <div className="absolute left-0 right-0 top-full z-20 mt-1 overflow-hidden rounded-[10px] bg-[#ffd08b] shadow-[0_12px_24px_rgba(0,0,0,0.18)]">
                    {placeholderLabel && (
                        <button
                            type="button"
                            onClick={() => selecionar('')}
                            className="block w-full px-3 py-2 text-left text-[#172B68] font-jaro hover:bg-[#ffd08b] transition-colors"
                        >
                            {placeholderLabel}
                        </button>
                    )}
                    {options.map((opt) => (
                        <button
                            key={opt.value}
                            type="button"
                            onClick={() => selecionar(opt.value)}
                            className={`block w-full px-3 py-2 text-left font-jaro hover:bg-[#FFB44E] transition-colors ${opt.value === valorAtual ? 'bg-[#c37c18] text-[#172B68]' : 'text-[#172B68]'}`}
                        >
                            {opt.label}
                        </button>
                    ))}
                </div>
            )}
        </div>
    ); 
}