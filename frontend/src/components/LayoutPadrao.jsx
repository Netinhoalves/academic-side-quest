import { useEffect, useState, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { BookOpen, Eye, FolderKanban, Home, Menu, Users, FileCheck, Award, X } from 'lucide-react';
import Header from './Header';
import pixelInf from '../assets/pixel-inferior-cinza.svg';
import useFecharAoClicarFora from '../hooks/useFecharAoClicarFora';
import { lerUsuario, rotaDoPerfil } from '../services/sessao';

function obterItensMenu(perfil, telaInicial) {
    if (perfil === 'coordenador') {
        return [
            { texto: 'Tela inicial', rota: telaInicial, icone: Home },
            { texto: 'Visualizar alunos', rota: '/visualizar-alunos', icone: Eye },
            { texto: 'Gerenciar projetos', rota: '/gerenciar-projetos', icone: FolderKanban },
            { texto: 'Gerenciar cursos', rota: '/gerenciar-cursos', icone: BookOpen },
            { texto: 'Gerenciar servidores', rota: '/painel-adm', icone: Users },
        ];
    }

    if (perfil === 'professor' || perfil === 'docente') {
        return [
            { texto: 'Tela inicial', rota: telaInicial, icone: Home },
            { texto: 'Visualizar alunos', rota: '/visualizar-alunos', icone: Eye },
        ];
    }

    if (perfil === 'aluno') {
        return [
            { texto: 'Tela inicial', rota: telaInicial, icone: Home },
            { texto: 'Comprovar horas', rota: '/comprovar-horas', icone: FileCheck },
            { texto: 'Visualizar resultados', rota: '/visualizar-resultados', icone: Award },
        ];
    }

    return [];
}

export default function LayoutPadrao({ children, perfisPermitidos = ['Coordenador'] }) {
    const navigate = useNavigate();
    const location = useLocation();
    
    const [menuRecolhido, setMenuRecolhido] = useState(
        () => localStorage.getItem('asq_menu_recolhido') !== 'false'
    );
    const [menuMobileAberto, setMenuMobileAberto] = useState(false);
    const menuMobileRef = useRef(null);

    const token = localStorage.getItem('asq_token');
    const usuario = lerUsuario();
    const perfil = usuario?.perfil?.toLowerCase() || '';

    const listaPerfis = Array.isArray(perfisPermitidos) ? perfisPermitidos : [perfisPermitidos];
    const permitido = Boolean(token && usuario) && listaPerfis.some((p) => p.toLowerCase() === perfil);
    const destino = token && usuario ? rotaDoPerfil(perfil) : '/';

    useFecharAoClicarFora(menuMobileRef, () => setMenuMobileAberto(false), menuMobileAberto);

    useEffect(() => {
        if (!permitido) {
            navigate(destino, { replace: true });
        }
    }, [permitido, destino, navigate]);

    if (!permitido) {
        return null;
    }

    const telaInicial = rotaDoPerfil(perfil);
    const itensMenu = obterItensMenu(perfil, telaInicial);
    const temMenu = itensMenu.length > 0;
    const itemInicial = itensMenu[0];
    const restantesItens = itensMenu.slice(1);

    function alternarMenu() {
        setMenuRecolhido((estadoAtual) => {
            const novoEstado = !estadoAtual;
            localStorage.setItem('asq_menu_recolhido', String(novoEstado));
            return novoEstado;
        });
    }

    return (
        <div className="relative min-h-screen bg-color-creme overflow-hidden flex flex-col font-jaro text-color-blue">
            <Header
                usuario={usuario}
                temMenu={temMenu}
                onAbrirMenu={() => setMenuMobileAberto(true)}
            />

            {temMenu && menuMobileAberto && (
                <div className="md:hidden fixed inset-0 z-40 bg-black/40">
                    <aside
                        ref={menuMobileRef}
                        className="w-[240px] h-full bg-color-blue text-white flex flex-col justify-between py-6 px-5 shadow-xl"
                    >
                        <div>
                            <div className="flex items-center justify-between mb-12">
                                {itemInicial && (
                                    <Link
                                        to={itemInicial.rota}
                                        onClick={() => setMenuMobileAberto(false)}
                                        className={`flex items-center gap-3 text-2xl transition-colors hover:text-color-yellow ${
                                            location.pathname === itemInicial.rota ? 'text-color-yellow' : ''
                                        }`}
                                    >
                                        <Home size={25} />
                                        <span>{itemInicial.texto}</span>
                                    </Link>
                                )}
                                <button
                                    type="button"
                                    onClick={() => setMenuMobileAberto(false)}
                                    aria-label="Fechar menu"
                                    className="p-1 hover:text-color-yellow transition-colors"
                                >
                                    <X size={24} />
                                </button>
                            </div>

                            <nav className="flex flex-col gap-6 text-lg">
                                {restantesItens.map(({ texto, rota, icone: Icon }) => (
                                    <Link
                                        key={rota}
                                        to={rota}
                                        onClick={() => setMenuMobileAberto(false)}
                                        className={`flex items-center gap-3 transition-colors ${
                                            location.pathname === rota ? 'text-color-yellow' : 'hover:text-color-yellow'
                                        }`}
                                    >
                                        <Icon size={18} />
                                        <span>{texto}</span>
                                    </Link>
                                ))}
                            </nav>
                        </div>
                    </aside>
                </div>
            )}

            <div className="relative z-10 flex flex-1 min-h-[calc(100vh-75px)]">
                {temMenu && (
                    <aside
                        className={`hidden md:flex shrink-0 bg-color-blue text-white flex-col justify-between py-6 transition-all duration-300 ${
                            menuRecolhido ? 'w-[58px] items-center px-0' : 'w-[225px] px-5'
                        }`}
                    >
                        <div>
                            {itemInicial && (
                                <Link
                                    to={itemInicial.rota}
                                    title={menuRecolhido ? itemInicial.texto : undefined}
                                    className={`mb-20 flex items-center gap-3 text-2xl transition-colors hover:text-color-yellow ${
                                        menuRecolhido ? 'justify-center' : ''
                                    } ${location.pathname === itemInicial.rota ? 'text-color-yellow' : ''}`}
                                >
                                    <Home size={25} />
                                    {!menuRecolhido && <span>{itemInicial.texto}</span>}
                                </Link>
                            )}

                            <nav className={`flex flex-col gap-6 text-lg ${menuRecolhido ? 'items-center' : ''}`}>
                                {restantesItens.map(({ texto, rota, icone: Icon }) => (
                                    <Link
                                        key={rota}
                                        to={rota}
                                        title={menuRecolhido ? texto : undefined}
                                        className={`flex items-center gap-3 transition-colors ${
                                            menuRecolhido ? 'justify-center' : ''
                                        } ${location.pathname === rota ? 'text-color-yellow' : 'hover:text-color-yellow'}`}
                                    >
                                        <Icon size={18} />
                                        {!menuRecolhido && <span>{texto}</span>}
                                    </Link>
                                ))}
                            </nav>
                        </div>

                        <button
                            type="button"
                            onClick={alternarMenu}
                            title={menuRecolhido ? 'Exibir menu' : 'Exibir menos'}
                            className={`flex items-center gap-3 text-lg hover:text-color-yellow transition-colors ${
                                menuRecolhido ? 'justify-center' : ''
                            }`}
                        >
                            <Menu size={27} />
                            {!menuRecolhido && <span>Exibir menos</span>}
                        </button>
                    </aside>
                )}

                <main className="relative min-w-0 flex-1 flex flex-col items-center px-5 py-10 md:px-12 lg:px-16">
                    {children}
                </main>
            </div>

            <img
                src={pixelInf}
                alt=""
                className="pointer-events-none absolute bottom-0 right-0 z-0 w-32 md:w-auto max-w-[265px] opacity-70"
            />
        </div>
    );
}
