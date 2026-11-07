import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

export function CampoSenha({ label, name, id, required, value, onChange, className = '' }) {
    const [visivel, setVisivel] = useState(false);

    return (
        <label htmlFor={id} className={`flex flex-col ${className}`}>
            {label && (
                <span className="text-color-blue font-bold text-base sm:text-lg mb-1">
                    {required && <span className="text-color-red mr-1">*</span>} {label}
                </span>
            )}
            <span className="relative w-full">
                <input
                    type={visivel ? 'text' : 'password'}
                    name={name}
                    id={id}
                    value={value}
                    onChange={onChange}
                    required={required}
                    className="w-full bg-[#D5800BD4] border border-[#B8731D] rounded-[10px] px-3 py-2 sm:py-3 pr-11
                               text-gray-900 outline-none focus:ring-2 focus:ring-color-blue transition-shadow shadow-[inset_0_4px_8px_rgba(0,0,0,0.15)]"
                />
                <button
                    type="button"
                    onClick={() => setVisivel((atual) => !atual)}
                    aria-label={visivel ? 'Ocultar senha' : 'Mostrar senha'}
                    className="absolute inset-y-0 right-0 flex items-center px-3 text-color-blue hover:text-color-blue-light"
                >
                    {visivel ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
            </span>
        </label>
    );
}