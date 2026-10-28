import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Hourglass } from 'lucide-react';
import LayoutPadrao from '../components/LayoutPadrao';
import { lerUsuario, rotaDoPerfil } from '../services/sessao';

// Tela provisória das rotas da entrega final: as telas de verdade entram nestas mesmas rotas
export default function EmBreve({ titulo, perfisPermitidos }) {
    const telaInicial = rotaDoPerfil(lerUsuario()?.perfil);

    useEffect(() => {
        document.title = `${titulo} | Academic Side Quest`;
    }, [titulo]);

    return (
        <LayoutPadrao perfisPermitidos={perfisPermitidos}>
            <h1 className="font-jaro text-color-blue text-4xl md:text-[64px] text-center mb-6">
                {titulo}
            </h1>

            <div className="bg-color-yellow w-full max-w-[615px] rounded-[10px] shadow-lg flex flex-col items-center gap-4 p-8 text-center text-color-blue">
                <Hourglass size={64} strokeWidth={2} />
                <h2 className="font-jaro text-3xl md:text-4xl">Em breve</h2>
                <p className="text-lg">Esta funcionalidade está em desenvolvimento.</p>
            </div>

            <Link to={telaInicial}
                className="mt-8 bg-color-blue text-white font-jaro tracking-widest px-6 py-2 rounded-md hover:scale-105 transition-transform flex items-center gap-2 shadow-md"
                >
                Voltar ao início <ArrowLeft size={20} strokeWidth={3} />
            </Link>
        </LayoutPadrao>
    );
}
