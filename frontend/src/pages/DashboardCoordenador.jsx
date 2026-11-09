import { useEffect } from 'react';
import LayoutPadrao from '../components/LayoutPadrao';
import DashboardButton from '../components/DashboardButton';
import {Eye, FileText,Users } from 'lucide-react';
import { lerUsuario} from '../services/sessao';

export default function DashboardCoordenador() {
    const usuario = lerUsuario();
    const perfil = usuario?.perfil?.toLowerCase() || '';

    useEffect(() => {
        document.title = "Portal da Coordenação | Academic Side Quest";
    }, []);

    return(
        <LayoutPadrao perfisPermitidos={['Coordenador', 'Professor']}>
            <h1 className="font-jaro text-color-blue text-4xl md:text-[64px] text-center mb-6">
                Bem-vindo {usuario?.nome}!
            </h1>

            <div className="bg-color-yellow w-full max-w-[900px] min-h-[402px] rounded-[10px] shadow-lg flex flex-wrap items-center justify-center gap-8 md:gap-12 p-8">
                <DashboardButton 
                    linkPara="/visualizar-alunos" 
                    texto="Visualizar alunos" 
                    icone={<Eye size={64} strokeWidth={2} />} 
                />
                
                {perfil === 'coordenador' && (
                    <>
                        <DashboardButton 
                            linkPara="/gerenciar-projetos" 
                            texto="Gerenciar Projetos" 
                            icone={<FileText size={64} strokeWidth={2} />} 
                        />
                        
                        <DashboardButton 
                            linkPara="/gerenciar-cursos" 
                            texto="Gerenciar Cursos" 
                            icone={<FileText size={64} strokeWidth={2} />}
                        />

                        <DashboardButton 
                            linkPara="/painel-adm" 
                            texto="Gerenciar Servidores" 
                            icone={<Users size={64} strokeWidth={2} />}
                        />
                    </>
                )}
            </div>
        </LayoutPadrao>
    );
}