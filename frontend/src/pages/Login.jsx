import { useParams, Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { InputField } from "../components/InputField";
import pixelSup from '../assets/pixel-superior.png';
import pixelInf from '../assets/pixel-inferior.png';

export default function Login() {
  const { tipo } = useParams();
  const navigate = useNavigate();
  const [carregando, setCarregando] = useState(false);
  const tituloFormatado = tipo === 'docente' ? 'Docente' : 'Aluno';
  const estiloBotao = "bg-color-blue text-white font-jaro tracking-widest rounded-md border-b-4 border-[#0c1840] hover:bg-color-blue-light active:border-b-0 active:translate-y-1 transition-all flex items-center justify-center";

  const handleLogin = (e) => {
    e.preventDefault();
    setCarregando(true);

    const formData = new FormData(e.target);
    const dados = Object.fromEntries(formData);
    console.log(`[TESTE HARDCODED] Login do ${tipo}:`, dados);

    setTimeout(() => {
      alert(`Simulação: ${tipo} logado com sucesso`);
      setCarregando(false);
      navigate('/'); 
    }, 1500);
  };

  return (
    <div className="relative min-h-screen bg-color-orange-bright flex items-center justify-center p-4 overflow-hidden font-jaro">
      <img src={pixelSup} alt="" className="absolute top-0 left-0 w-32 md:w-auto max-w-[265px]" />
      <img src={pixelInf} alt="" className="absolute bottom-0 right-0 w-32 md:w-auto max-w-[265px]" />

      <div className="relative z-10 bg-color-yellow rounded-[15px] shadow-lg w-full max-w-[560px] p-6 sm:p-8 flex flex-col items-center">
        <h1 className="text-color-blue text-[40px] font-normal mb-6 self-start md:ml-6">Login do {tituloFormatado}</h1>

        <form className="w-full flex flex-col items-center gap-2" onSubmit={handleLogin}>
          <InputField label="Seu e-mail:" type="email" id="email" name="email" required />
          <InputField label="Sua senha:" type="password" id="senha" name="senha" required />

          <div className="flex gap-4 sm:gap-20 mt-4 w-full justify-center">
            <Link to="/" className={`${estiloBotao} w-[130px] py-2 text-lg`}>
                Voltar
            </Link>
            
            <button 
                type="submit" 
                disabled={carregando}
                className={`${estiloBotao} w-[130px] py-2 text-lg ${carregando ? 'opacity-70 cursor-not-allowed' : ''}`}
            >
                {carregando ? 'Aguarde...' : 'Entrar'}
            </button>
          </div>
        </form>

        <p className="mt-8 text-color-blue text-lg tracking-wide text-center">
          Caso não tenha um acesso, <Link to={`/cadastro/${tipo}`} className="text-color-blue-light hover:underline">clique aqui</Link> para criar
        </p>
      </div>
    </div>
  )
}
