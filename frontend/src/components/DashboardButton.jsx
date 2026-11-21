import { Link } from 'react-router-dom';

export default function DashboardButton({ icone, texto, linkPara, notificacao }) {
    return (
        <Link to={linkPara} className="flex flex-col items-center gap-3 2xl:gap-4 group hover:scale-105 transition-transform duration-300">
            <div className="relative w-[150px] h-[150px] 2xl:w-[190px] 2xl:h-[190px] bg-color-blue rounded-[15px] 2xl:rounded-[20px] flex justify-center items-center shadow-md text-white 2xl:[&_svg]:w-20 2xl:[&_svg]:h-20 transition-all duration-300">
                {icone}

                {notificacao > 0 && (
                    <div className="absolute -top-3 -right-3 bg-red-600 text-white w-8 h-8 2xl:w-9 2xl:h-9 2xl:text-lg rounded-full flex items-center justify-center font-bold shadow-sm">
                        {notificacao}
                    </div>
                )}
            </div>

            <span className="font-jaro text-color-blue text-xl 2xl:text-2xl text-center whitespace-nowrap leading-tight">
                {texto}
            </span>
        </Link>
    );
}