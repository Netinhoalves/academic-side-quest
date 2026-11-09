import { useEffect } from 'react';
import LayoutPadrao from '../components/LayoutPadrao';
import DashboardButton from '../components/DashboardButton';
import { Upload, Eye } from 'lucide-react';
import { lerUsuario } from '../services/sessao';

export default function DashboardAluno() {
    const usuario = lerUsuario();

    useEffect(() => {
        document.title = "Portal do Aluno | Academic Side Quest";
    }, []);

    return(
        <LayoutPadrao perfisPermitidos={['Aluno']}>
            <h1 className="font-jaro text-color-blue text-4xl md:text-[64px] text-center mb-6">
                Bem-vindo {usuario?.nome}!
            </h1>

            <div className="bg-color-yellow w-full max-w-[615px] min-h-[402px] rounded-[10px] shadow-lg flex flex-wrap items-center justify-center gap-8 md:gap-12 p-8">
                <DashboardButton 
                    linkPara="/comprovar-horas" 
                    texto="Comprovar horas" 
                    icone={<Upload size={64} strokeWidth={2} />} 
                />
                <DashboardButton 
                    linkPara="/visualizar-resultados" 
                    texto="Visualizar resultados" 
                    icone={<Eye size={64} strokeWidth={2} />}
                />
            </div>
        </LayoutPadrao>
    );
}