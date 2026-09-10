import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { InputField } from "../components/InputField";
import { SelectField } from "../components/SelectField";
import pixelSupAzul from '../assets/pixel-superior-azul.svg';
import pixelInfAzul from '../assets/pixel-inferior-azul.png';

export default function Cadastro() {
  const { tipo } = useParams();
  const [etapa, setEtapa] = useState(1); 
  const [carregando, setCarregando] = useState(false);
  const navigate = useNavigate();

  const handleCadastro = (e) => {
    e.preventDefault();
    setCarregando(true); 

    const formData = new FormData(e.target);
    const dados = Object.fromEntries(formData);

    console.log(`SÓ UM TESTE = Novo cadastro de ${tipo}:`, dados);
    
    setTimeout(() => {
      alert('Simulação: Cadastro realizado');
      setCarregando(false);
      navigate(`/login/${tipo}`);
    }, 1500);
  }

  const avancarEtapa = () => {
    const nome = document.getElementById('nome');
    const email = document.getElementById('email');
    const senha = document.getElementById('senha');

    if (!nome.checkValidity()) { nome.reportValidity(); return; }
    if (!email.checkValidity()) { email.reportValidity(); return; }
    if (!senha.checkValidity()) { senha.reportValidity(); return; }

    setEtapa(2);
  }

  const estiloBotao = "bg-color-blue text-white font-jaro tracking-widest rounded-md border-b-4 border-[#0c1840] hover:bg-color-blue-light active:border-b-0 active:translate-y-1 transition-all flex items-center justify-center";

  const opcoesCurso = [
    { value: "ads", label: "Análise e Desenvolvimento de Sistemas" },
    { value: "eng_software", label: "Engenharia de Software" }
  ];

  const opcoesPPC = [
    { value: "2020", label: "PPC 2020" },
    { value: "2024", label: "PPC 2024" }
  ];

  return (
    <div className="relative min-h-screen bg-color-creme flex items-center justify-center p-4 overflow-hidden font-jaro">
      <img src={pixelSupAzul} alt="" className="absolute top-0 left-0 w-32 md:w-auto max-w-[265px]" />
      <img src={pixelInfAzul} alt="" className="absolute bottom-0 right-0 w-32 md:w-auto max-w-[265px]" />

      <div className="relative z-10 bg-color-yellow rounded-[15px] shadow-lg w-full max-w-[560px] px-6 py-4 sm:p-6 flex flex-col items-center">
        
        <h1 className="text-color-blue text-3xl sm:text-[40px] font-normal mb-6 self-start md:ml-6">
          Cadastro
        </h1>

        <form className="w-full flex flex-col items-center mb-10 gap-2" onSubmit={handleCadastro}>
          {/* FLUXO DO DOCENTE */}
          {tipo === 'docente' && (
            <>
              <InputField label="Nome completo:" type="text" id="nome" name="nome" required />
              <InputField label="Seu código de docente:" type="text" id="codigo_servidor" name="codigo_servidor" required />
              <InputField label="Seu e-mail:" type="email" id="email" name="email" required/>
              <InputField label="Sua senha:" type="password" id="senha" name="senha" required/>

              <div className="flex gap-4 sm:gap-20 mt-4 w-full justify-center">
                <Link to={`/login/${tipo}`} className={`${estiloBotao} w-[130px] py-2 text-lg`}>
                    Voltar
                </Link>
                <button 
                  type="submit" 
                  disabled={carregando}
                  className={`${estiloBotao} w-[130px] py-2 text-lg ${carregando ? 'opacity-70 cursor-not-allowed' : ''}`}
                >
                    {carregando ? 'Aguarde...' : 'Cadastrar'}
                </button>
              </div>
            </>
          )}

          {/* FLUXO DO ALUNO */}
          {tipo === 'aluno' && (
            <>
              {/* ETAPA 1 */}
              <div className={`w-full flex-col items-center gap-2 ${etapa === 1 ? 'flex' : 'hidden'}`}>
                <InputField label="Nome completo:" type="text" id="nome" name="nome" required/>
                <InputField label="Seu e-mail:" type="email" id="email" name="email" required/>
                <InputField label="Sua senha:" type="password" id="senha" name="senha" required/>

                <div className="flex gap-4 sm:gap-20 mt-4 w-full justify-center">
                  <Link to={`/login/${tipo}`} className={`${estiloBotao} w-[130px] py-2 text-lg`}>
                      Voltar
                  </Link>
                  <button type="button" onClick={avancarEtapa} className={`${estiloBotao} w-[130px] py-2 text-lg`}>
                      Continuar
                  </button>
                </div>
              </div>

              {/* ETAPA 2 */}
              <div className={`w-full flex-col items-center gap-2 ${etapa === 2 ? 'flex' : 'hidden'}`}>
                <InputField label="Seu código de aluno:" type="text" id="codigo_aluno" name="codigo_aluno" required />
                <SelectField label="Selecione seu curso:" id="curso" name="curso" options={opcoesCurso} required />
                <SelectField label="Selecione seu PPC:" id="ppc" name="ppc" options={opcoesPPC} required />

                <div className="flex gap-4 sm:gap-20 mt-4 w-full justify-center">
                  <button type="button" onClick={() => setEtapa(1)} className={`${estiloBotao} w-[130px] py-2 text-lg`}>
                      Voltar
                  </button>
                  <button 
                    type="submit" 
                    disabled={carregando}
                    className={`${estiloBotao} w-[130px] py-2 text-lg ${carregando ? 'opacity-70 cursor-not-allowed' : ''}`}
                  >
                      {carregando ? 'Aguarde...' : 'Cadastrar'}
                  </button>
                </div>
              </div>
            </>
          )}
        </form>
      </div>
    </div>
  )
}