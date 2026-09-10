import { useState } from "react";
import { useNavigate } from "react-router-dom";
import logoProjeto from '../assets/logo.png';
import tituloProjeto from '../assets/titulo.svg';
export default function Inicio() {
    const [mostrarPerfis, setMostrarPerfis] = useState(false);
    const navigate = useNavigate();

    const estiloBotao = "bg-color-blue text-white font-jaro tracking-widest rounded-md border-b-4 border-[#0c1840] hover:bg-color-blue-light active:border-b-0 active:translate-y-1 transition-all flex items-center justify-center";

    return (
        <div className="min-h-screen bg-color-creme flex flex-col items-center justify-center p-4">
            <img src={logoProjeto} alt="Academic Side Quest Logo" className="w-[150px] max-w-full" />
            <img src={tituloProjeto} alt="Academic Side Quest" className="w-[600px] max-w-full mb-12"/>

            {!mostrarPerfis ? (
                <button onClick={() => setMostrarPerfis(true)} className={`${estiloBotao} text-2xl px-12 py-3`}>
                    Start
                </button>
            ) : (
                <div className="flex flex-col sm:flex-row gap-6">
                    <button onClick={() => navigate('/login/aluno')} className={`${estiloBotao} text-xl w-[200px] py-3`}>
                    Aluno
                    </button>

                    <button onClick={() => navigate('/login/docente')} className={`${estiloBotao} text-xl w-[200px] py-3`}>
                    Docente
                    </button>
                </div>
            )}
        </div>

    )
}