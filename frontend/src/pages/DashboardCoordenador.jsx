import {useState, useEffect} from 'react';
import {Link} from 'react-router-dom';
import LayoutPadrao from '../components/LayoutPadrao';
import DashboardButton from '../components/DashboardButton';
import {Eye, FileText, ArrowLeft} from 'lucide-react';

export default function DashboardCoordenador() {
    const [nomeUsuario, setNomeUsuario] = useState('Visitante');

    useEffect(() => {
        const dadosSalvos = localStorage.getItem('asq_usuario');

        if (dadosSalvos) {
            const usuarioObjeto = JSON.parse(dadosSalvos);
            setNomeUsuario(usuarioObjeto.nome);
        }
    }, [])

    return(
        <LayoutPadrao perfilPermitido="Professor">
            <h1 className="font-jaro text-color-blue text-4xl md:text-[64px] text-center mb-6">
                Bem vindo {nomeUsuario}!
            </h1>

            <div className="bg-color-yellow w-full max-w-[900px] min-h-[402px] rounded-[10px] shadow-lg flex flex-wrap items-center justify-center gap-8 md:gap-12 p-8">
                <DashboardButton 
                    linkPara="/visualizar-alunos" 
                    texto="Visualizar alunos" 
                    icone={<Eye size={64} strokeWidth={2} />} 
                />
                
                <DashboardButton 
                    linkPara="/gerenciar-projetos" 
                    texto="Gerenciar Projetos" 
                    icone={<FileText size={64} strokeWidth={2} />} 
                />
                
                <DashboardButton 
                    linkPara="/gerenciar-cursos" 
                    texto="Gerenciar Cursos" 
                    icone={<FileText size={64} strokeWidth={2} />}
                    notificacao={2}
                />
            </div>

            <Link to="/" onClick={() => {
                localStorage.removeItem('asq_usuario');
                localStorage.removeItem('asq_token');
                }} 
                className="mt-8 bg-color-blue text-white font-jaro tracking-widest px-6 py-2 rounded-md hover:scale-105 transition-transform flex items-center gap-2 shadow-md"
                >
                Voltar ao Login <ArrowLeft size={30} strokeWidth={3} />
            </Link>
        </LayoutPadrao>
    );
}