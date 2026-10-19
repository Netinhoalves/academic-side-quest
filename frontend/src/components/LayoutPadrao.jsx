import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from './Header';
import pixelInf from '../assets/pixel-inferior-cinza.svg';
import { lerUsuario, rotaDoPerfil } from '../services/sessao';

export default function LayoutPadrao({ children, perfilPermitido, perfisPermitidos = [] }) {
    const navigate = useNavigate();
    const token = localStorage.getItem('asq_token');
    const usuario = lerUsuario();
    const perfil = usuario?.perfil?.toLowerCase() || '';
    const perfis = perfisPermitidos.length ? perfisPermitidos : (perfilPermitido ? [perfilPermitido] : []);
    const permitido = Boolean(token && usuario) && perfis.some((p) => p.toLowerCase() === perfil);
    const destino = token && usuario ? rotaDoPerfil(perfil) : '/';

    useEffect(() => {
        if (!permitido) {
            navigate(destino, {replace: true});
        }
    }, [permitido, destino, navigate]);

    if (!permitido) {
        return null;
    }

    return(
        <div className="relative bg-color-cream min-h-screen overflow-hidden flex flex-col">
            <Header nome={usuario.nome} /> 

            <main className="relative z-10 flex-1 flex flex-col items-center px-4 mt-12">
                {children}
            </main>

            <img src={pixelInf} alt="" className="absolute bottom-0 right-0 w-32 md:w-auto max-w-[265px] opacity-30 pointer-events-none" />
        </div>
    );
}