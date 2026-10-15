export function InputField({label, type = 'text', name, id, required}) {
    return (
        <div className="flex flex-col w-full max-w-[442px] mb-3">
            <label htmlFor={id} className="text-color-blue font-bold text-base sm:text-lg mb-1 flex items-center">
                {required && <span className="text-color-red mr-1">*</span>} {label}
            </label>
            <input 
                type={type} 
                name={name} 
                id={id} 
                required={required}
                className="w-full bg-[#D5800BD4] border border-[#B8731D] rounded-[10px] px-3 py-2 sm:py-3
                           text-gray-900 outline-none focus:ring-2 focus:ring-color-blue transition-shadow shadow-[inset_0_4px_8px_rgba(0,0,0,0.15)]"
            />
        </div>
    ); 
}