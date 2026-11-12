import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

export default function Breadcrumbs({ itens }) {
    return (
        <nav aria-label="Breadcrumb" className="w-full max-w-[920px] mb-4 flex items-center gap-2 text-color-blue text-lg font-bold">
            {itens.map((item, index) => {
                const ultimo = index === itens.length - 1;

                return (
                    <div key={item.label} className="flex items-center gap-2">
                        {index > 0 && <ChevronRight size={18} className="opacity-70" />}
                        {ultimo || !item.rota ? (
                            <span className="opacity-80 font-normal">{item.label}</span>
                        ) : (
                            <Link to={item.rota} className="hover:underline hover:text-color-orange-bright transition-colors">
                                {item.label}
                            </Link>
                        )}
                    </div>
                );
            })}
        </nav>
    );
}