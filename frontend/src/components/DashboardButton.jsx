import {Link} from 'react-router-dom';

export default function DashboardButton({ icone, texto, linkPara, notificacao}) {
    return (
        <Link to={linkPara} className="flex flex-col items-center gap-3 group hover:scale-105 transition-transform duration-300">
            <div className="relative w-[150px] h-[150px] bg-color-blue rounded-[15px] flex justify-center items-center shadow-md text-white">
                {icone}

                {notificacao > 0 && (
                    <div className="absolute -top-3 -right-3 bg-red-600 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold shadow-sm">
                        {notificacao}
                    </div>
                )}
            </div>

            <span className="font-jaro text-color-blue text-xl text-center whitespace-nowrap leading-tight">
                {texto}
            </span>
        </Link>
    );
}