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

    return (
        <LayoutPadrao perfisPermitidos={['Aluno']}>
            <div className="flex flex-col flex-1 justify-center w-full">
                <h1 className="font-jaro text-color-blue text-4xl md:text-[56px] 2xl:text-[64px] text-center mb-6 transition-all duration-300">
                    Bem-vindo {usuario?.nome}!
                </h1>

                <div className="mx-auto bg-color-yellow w-full max-w-[615px] 2xl:max-w-[1300px] min-h-[402px] 2xl:min-h-[480px] rounded-[10px] 2xl:rounded-[16px] shadow-lg flex flex-wrap items-center justify-center gap-8 md:gap-12 2xl:gap-16 p-8 2xl:p-12 transition-all duration-300">
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
            </div>
        </LayoutPadrao>
    );
}