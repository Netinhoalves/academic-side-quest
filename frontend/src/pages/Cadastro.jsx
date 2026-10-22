import { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { InputField } from "../components/InputField";
import { SelectField } from "../components/SelectField";
import pixelSupAzul from '../assets/pixel-superior-azul.svg';
import pixelInfAzul from '../assets/pixel-inferior-azul.png';
import { cadastrarAluno, getCursos, getPpcsPorCurso } from '../services/api';

export default function Cadastro() {
  const { tipo = 'aluno' } = useParams();
  const navigate = useNavigate();
  const [etapa, setEtapa] = useState(1);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState('');
  const [cursos, setCursos] = useState([]);
  const [ppcs, setPpcs] = useState([]);
  const [cursoSelecionado, setCursoSelecionado] = useState('');
  const [ppcSelecionado, setPpcSelecionado] = useState('');

  useEffect(() => {
    document.title = "Cadastro | Academic Side Quest";
  }, []);

  useEffect(() => {
    if (tipo === 'aluno') {
      getCursos()
        .then((dados) => {
          const opcoesFormatadas = dados.map(c => ({ value: String(c.id), label: c.nome }));
          setCursos(opcoesFormatadas);
        })
        .catch(() => setErro('Falha ao carregar a lista de cursos.'));
    }
  }, [tipo]);

  useEffect(() => {
    if (!cursoSelecionado) return;

    getPpcsPorCurso(cursoSelecionado)
      .then((dados) => {
        const opcoesFormatadas = dados.map(p => ({ value: String(p.id), label: `${p.nome} (${p.ano})` }));
        setPpcs(opcoesFormatadas);
      })
      .catch(() => setErro('Falha ao carregar a lista de PPCs.'));
  }, [cursoSelecionado]);

  const trocarCurso = (e) => {
    if (e.target.value === cursoSelecionado) return;
    setCursoSelecionado(e.target.value);
    setPpcs([]);
    setPpcSelecionado('');
  };

  const avancarEtapa = () => {
    const nome = document.getElementById('nome');
    const email = document.getElementById('email');
    const senha = document.getElementById('senha');

    if (!nome.checkValidity()) { nome.reportValidity(); return; }
    if (!email.checkValidity()) { email.reportValidity(); return; }
    if (!senha.checkValidity()) { senha.reportValidity(); return; }
    
    setErro('');
    setEtapa(2); 
  };

  const handleCadastro = async (e) => {
    e.preventDefault();

    if (!ppcSelecionado) {
      setErro('Selecione o curso e o PPC.');
      return;
    }

    setCarregando(true);
    setErro('');

    const formData = new FormData(e.target);
    const dados = Object.fromEntries(formData);

    try {
      await cadastrarAluno({
        nome: dados.nome,
        email: dados.email,
        senha: dados.senha,
        matricula: dados.codigo_aluno,
        id_ppc: Number(dados.ppc)
      });

      navigate('/login/aluno', { state: { mensagemSucesso: 'Cadastro realizado com sucesso! Faça seu login.' }});
      
    } catch (error) {
      setErro(error.message || 'Falha ao cadastrar, verifique os dados.');
    } finally {
      setCarregando(false);
    }
  };

  const estiloBotao = "bg-color-blue text-white font-jaro tracking-widest rounded-md border-b-4 border-[#0c1840] hover:bg-color-blue-light active:border-b-0 active:translate-y-1 transition-all flex items-center justify-center";

  return (
    <div className="relative min-h-screen bg-color-creme flex items-center justify-center p-4 overflow-hidden font-jaro">
      <img src={pixelSupAzul} alt="" className="absolute top-0 left-0 w-32 md:w-auto max-w-[265px]" />
      <img src={pixelInfAzul} alt="" className="absolute bottom-0 right-0 w-32 md:w-auto max-w-[265px]" />

      <div className="relative z-10 bg-color-yellow rounded-[15px] shadow-lg w-full max-w-[560px] px-6 py-4 sm:p-6 flex flex-col items-center">
        <h1 className="text-color-blue text-3xl sm:text-[40px] font-normal mb-6 self-start md:ml-6">
          Cadastro de Aluno
        </h1>

        {erro && (
          <div className="w-full max-w-[442px] mb-3 rounded-[10px] bg-red-100 border border-red-300 px-3 py-2 text-red-700 text-sm">
            {erro}
          </div>
        )}

        <form className="w-full flex flex-col items-center mb-10 gap-2" onSubmit={handleCadastro}>
          <div className={`w-full flex-col items-center gap-2 ${etapa === 1 ? 'flex' : 'hidden'}`}>
            <InputField label="Nome completo:" type="text" id="nome" name="nome" required />
            <InputField label="Seu e-mail:" type="email" id="email" name="email" required />
            <InputField label="Sua senha:" type="password" id="senha" name="senha" required />

            <div className="flex gap-4 sm:gap-20 mt-4 w-full justify-center">
              <Link to="/login/aluno" className={`${estiloBotao} w-[130px] py-2 text-lg`}>
                Voltar
              </Link>
              <button type="button" onClick={avancarEtapa} className={`${estiloBotao} w-[130px] py-2 text-lg`}>
                Continuar
              </button>
            </div>
          </div>

          <div className={`w-full flex-col items-center gap-2 ${etapa === 2 ? 'flex' : 'hidden'}`}>
            <InputField label="Sua Matrícula:" type="text" id="codigo_aluno" name="codigo_aluno" required />
            
            <SelectField 
              label="Selecione seu curso:" 
              id="curso" 
              name="curso" 
              options={cursos} 
              value={cursoSelecionado}
              onChange={trocarCurso}
              required 
            />
            
            <SelectField 
              label="Selecione seu PPC:" 
              id="ppc" 
              name="ppc" 
              options={ppcs}
              value={ppcSelecionado}
              onChange={(e) => setPpcSelecionado(e.target.value)}
              required 
              disabled={!cursoSelecionado} 
            />

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

        </form>
      </div>
    </div>
  );
}
