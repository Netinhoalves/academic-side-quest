import { Link} from 'react-router-dom';
import LayoutPadrao from '../components/LayoutPadrao';
import DashboardButton from '../components/DashboardButton';
import { Upload, Eye, ArrowLeft} from 'lucide-react';
import { lerUsuario, limparSessao } from '../services/sessao';

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

            <Link to="/" onClick={limparSessao}
                className="mt-8 bg-color-blue text-white font-jaro tracking-widest px-6 py-2 rounded-md hover:scale-105 transition-transform flex items-center gap-2 shadow-md"
                >
                Voltar ao Login <ArrowLeft size={20} strokeWidth={3} />
            </Link>
        </LayoutPadrao>
    );
}