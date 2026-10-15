import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import logoAsq from '../assets/logo-sigla.png';
import pixelInf from '../assets/pixel-inferior-cinza.svg';
import MenuCoordenador from './MenuCoordenador';

export default function LayoutCoordenador({ children }) {
    const navigate = useNavigate();
    const location = useLocation();
    const [menuRecolhido, setMenuRecolhido] = useState(() => localStorage.getItem('asq_menu_recolhido') !== 'false');
    const [usuario, setUsuario] = useState(() => {
        const dados = localStorage.getItem('asq_usuario');
        return dados ? JSON.parse(dados) : null;
    });

    useEffect(() => {
        const dados = localStorage.getItem('asq_usuario');

        if (!dados) {
            navigate('/');
            return;
        }

        setUsuario(JSON.parse(dados));
    }, [navigate, location.pathname]);

    const nome = usuario?.nome || 'Coordenador';
    const iniciais = nome.split(' ').map((item) => item[0]).join('').slice(0, 2).toUpperCase();

    function alternarMenu() {
        setMenuRecolhido((estadoAtual) => {
            const novoEstado = !estadoAtual;
            localStorage.setItem('asq_menu_recolhido', String(novoEstado));
            return novoEstado;
        });
    }

    return (
        <div className="relative min-h-screen bg-color-creme overflow-hidden font-jaro text-color-blue">
            <header className="relative z-20 h-[60px] bg-color-orange-bright px-5 flex items-center justify-between shadow-md">
                <div className="flex items-center gap-3 text-white">
                    <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-color-blue text-sm font-bold">
                        {iniciais}
                    </div>
                    <div className="leading-tight text-sm">
                        <p>Coordenador</p>
                        <p>IFMS - TL</p>
                    </div>
                </div>
                <img src={logoAsq} alt="ASQ" className="h-11 w-auto" />
            </header>

            <div className="relative z-10 flex min-h-[calc(100vh-60px)]">
                <MenuCoordenador recolhido={menuRecolhido} onAlternar={alternarMenu} />
                <main className="relative flex-1 px-5 py-12 md:px-12 lg:px-16">
                    {children}
                </main>
            </div>

            <img src={pixelInf} alt="" className="pointer-events-none absolute bottom-0 right-0 z-0 w-32 md:w-auto max-w-[265px] opacity-70" />
        </div>
    );
}