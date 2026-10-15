import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Header from './Header';
import pixelInf from '../assets/pixel-inferior-cinza.svg';
import { DEMO_MODE, startDemoSession } from '../services/api';

export default function LayoutPadrao({ children, perfilPermitido }) {
    const [nomeUsuario, setNomeUsuario] = useState('Visitante');
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const token = localStorage.getItem('asq_token');
        const dadosSalvos = localStorage.getItem('asq_usuario');

        if ((!token || !dadosSalvos) && DEMO_MODE) {
            startDemoSession(perfilPermitido?.toLowerCase() === 'professor' ? 'coordenador' : 'aluno');
            return;
        }

        if (!token || !dadosSalvos) {
            navigate('/');
            return;
        }

        const usuarioObjeto = JSON.parse(dadosSalvos);

        const perfilUsuario = usuarioObjeto.perfil ? usuarioObjeto.perfil.toLowerCase() : '';
        const perfilExigido = perfilPermitido ? perfilPermitido.toLowerCase() : '';

        if (perfilExigido && perfilUsuario !== perfilExigido) {
            if (perfilUsuario === 'administrador' && location.pathname !== '/painel-adm') {
                navigate('/painel-adm');
            } else if ((perfilUsuario === 'coordenador' || perfilUsuario === 'docente' || perfilUsuario === 'professor') && location.pathname !== '/coordenador') {
                navigate('/coordenador');
            } else if (perfilUsuario === 'aluno' && location.pathname !== '/aluno') {
                navigate('/aluno');
            }
            return; 
        }

        setNomeUsuario(usuarioObjeto.nome);
        
    }, [navigate, perfilPermitido, location.pathname]);

    return(
        <div className="relative bg-color-cream min-h-screen overflow-hidden flex flex-col">
            <Header nome={nomeUsuario} /> 

            <main className="relative z-10 flex-1 flex flex-col items-center px-4 mt-12">
                {children}
            </main>

            <img src={pixelInf} alt="" className="absolute bottom-0 right-0 w-32 md:w-auto max-w-[265px] opacity-30 pointer-events-none" />
        </div>
    );
}