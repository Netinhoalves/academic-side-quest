import { BookOpen, Eye, FolderKanban, Home, Menu } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { lerUsuario } from '../services/sessao';

const itensMenu = [
    { texto: 'Visualizar alunos', rota: '/visualizar-alunos', icone: Eye },
    { texto: 'Gerenciar projetos', rota: '/gerenciar-projetos', icone: FolderKanban },
    { texto: 'Gerenciar cursos', rota: '/gerenciar-cursos', icone: BookOpen },
];

export default function MenuCoordenador({ recolhido, onAlternar }) {
    const location = useLocation();
    const usuario = lerUsuario();
    const perfil = usuario?.perfil?.toLowerCase();
    const telaInicial = ['coordenador', 'docente', 'professor'].includes(perfil) ? '/coordenador' : '/aluno';

    return (
        <aside className={`hidden md:flex shrink-0 bg-color-blue text-white flex-col justify-between min-h-[calc(100vh-60px)] py-6 transition-all duration-300 ${recolhido ? 'w-[58px] items-center px-0' : 'w-[225px] px-5'}`}>
            <div>
                <Link
                    to={telaInicial}
                    title={recolhido ? 'Tela inicial' : undefined}
                    className={`mb-20 flex items-center gap-3 text-2xl transition-colors hover:text-color-yellow ${recolhido ? 'justify-center' : ''} ${location.pathname === telaInicial ? 'text-color-yellow' : ''}`}
                >
                    <Home size={25} />
                    {!recolhido && <span>Tela inicial</span>}
                </Link>

                <nav className={`flex flex-col gap-6 text-lg ${recolhido ? 'items-center' : ''}`}>
                    {itensMenu.map(({ texto, rota, icone: Icon }) => (
                        <Link
                            key={rota}
                            to={rota}
                            title={recolhido ? texto : undefined}
                            className={`flex items-center gap-3 transition-colors ${recolhido ? 'justify-center' : ''} ${location.pathname === rota ? 'text-color-yellow' : 'hover:text-color-yellow'}`}
                        >
                            <Icon size={18} />
                            {!recolhido && <span>{texto}</span>}
                        </Link>
                    ))}
                </nav>
            </div>

            <button type="button" onClick={onAlternar} title={recolhido ? 'Exibir menu' : 'Exibir menos'} className={`flex items-center gap-3 text-lg hover:text-color-yellow transition-colors ${recolhido ? 'justify-center' : ''}`}>
                <Menu size={27} />
                {!recolhido && <span>Exibir menos</span>}
            </button>
        </aside>
    );
}