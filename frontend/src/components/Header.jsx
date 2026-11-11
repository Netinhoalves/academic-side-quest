import { Link, useNavigate } from 'react-router-dom';
import { Menu, LogOut } from 'lucide-react';
import logoAsq from '../assets/logo-sigla.png';
import { limparSessao, rotaDoPerfil } from '../services/sessao';

export default function Header({ usuario, temMenu, onAbrirMenu }) {
    const navigate = useNavigate();
    const nome = usuario?.nome || 'Usuário';
    const perfil = usuario?.perfil || '';
    const iniciais = nome.split(' ').map((n) => n[0]).join('').substring(0, 2).toUpperCase();
    const linkInicial = rotaDoPerfil(perfil.toLowerCase());

    const handleSair = () => {
        limparSessao();
        navigate('/');
    };

    return (
        <header className="relative z-20 bg-color-orange-bright h-[75px] w-full px-5 flex justify-between items-center shadow-md shrink-0">
            <div className="flex items-center gap-3 text-white min-w-0">
                {temMenu && (
                    <button
                        type="button"
                        onClick={onAbrirMenu}
                        aria-label="Abrir menu"
                        className="md:hidden p-1 rounded hover:opacity-80 transition-opacity shrink-0"
                    >
                        <Menu size={28} />
                    </button>
                )}

                <div className="w-11 h-11 bg-white rounded-full flex items-center justify-center text-color-blue font-bold text-base shrink-0">
                    {iniciais}
                </div>

                <div className="leading-tight min-w-0">
                    <p className="font-bold text-base sm:text-lg truncate">{nome}</p>
                    <p className="text-xs sm:text-sm opacity-95 capitalize truncate">{perfil} / IFMS - TL</p>
                </div>
            </div>

            <div className="flex items-center gap-4 shrink-0">
                <Link to={linkInicial} title="Ir para a tela inicial" className="hidden sm:block hover:opacity-90 transition-opacity">
                    <img src={logoAsq} alt="Logo ASQ" className="h-11 w-auto" />
                </Link>

                <button
                    type="button"
                    onClick={handleSair}
                    className="bg-color-blue text-white font-jaro tracking-wider px-3 sm:px-4 py-2 rounded-md hover:bg-color-blue-light transition-colors flex items-center gap-2 shadow-md text-sm sm:text-base"
                >
                    <span>Sair</span>
                    <LogOut size={18} />
                </button>
            </div>
        </header>
    );
}