import { ChevronDown, Plus } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import LayoutCoordenador from '../components/LayoutCoordenador';
import { carregarProjetos } from '../services/projetosMock';

export default function Projetos() {
    const navigate = useNavigate();
    const [projetos] = useState(carregarProjetos);
    const [acoesAbertas, setAcoesAbertas] = useState(null);

    return (
        <LayoutCoordenador>
            <section className="mx-auto w-full max-w-[1250px]">
                <div className="mb-2 flex items-center justify-between gap-4">
                    <h1 className="text-4xl md:text-5xl">Projetos</h1>
                    <Link to="/adicionar-projeto" className="flex shrink-0 items-center gap-2 rounded-md bg-color-blue px-5 py-3 text-lg text-white shadow-sm hover:bg-color-blue-light">
                        <Plus size={21} /> Adicionar Projeto
                    </Link>
                </div>

                <div className="rounded-lg shadow-md">
                    {projetos.map((projeto, index) => {
                        const menuAberto = acoesAbertas === projeto.id;
                        const projetoInativo = projeto.ativo === false;
                        const estiloLinha = projetoInativo
                            ? 'bg-gray-300 text-gray-500'
                            : index % 2 === 0 ? 'bg-color-yellow' : 'bg-[#FFD394]';

                        return (
                            <div key={projeto.id} className={`relative flex items-center gap-4 px-5 py-3 ${estiloLinha} ${index === 0 ? 'rounded-t-lg' : ''} ${index === projetos.length - 1 ? 'rounded-b-lg' : ''}`}>
                                    <span className={`h-4 w-4 shrink-0 rounded-full ${projetoInativo ? 'bg-gray-500' : 'bg-color-blue'}`} />
                                    <span className="min-w-0 flex-1">
                                        <strong className="block truncate text-2xl">
                                            {projeto.titulo}
                                            <span className="mx-3 text-lg font-normal">•</span>
                                            <span className="text-lg font-normal">{projeto.ano}</span>
                                            {projetoInativo && <span className="ml-3 text-lg font-normal">Inativo</span>}
                                        </strong>
                                        <small className="block truncate text-base">{projeto.descricao}</small>
                                    </span>

                                    <span className="shrink-0 text-lg">{projeto.pontos} pontos</span>

                                <div className="relative shrink-0">
                                    <button type="button" onClick={() => setAcoesAbertas(menuAberto ? null : projeto.id)} className={`flex items-center gap-3 rounded-md px-5 py-2 text-lg text-white ${projetoInativo ? 'bg-gray-500 hover:bg-gray-600' : 'bg-color-blue hover:bg-color-blue-light'}`}>
                                        Ações <ChevronDown size={20} />
                                    </button>

                                    <div className={`absolute right-0 top-full z-20 mt-1 min-w-[220px] origin-top-right rounded-md bg-color-creme py-2 text-lg text-color-blue shadow-lg transition-all duration-200 ease-out ${menuAberto ? 'visible translate-y-0 scale-100 opacity-100' : 'invisible pointer-events-none -translate-y-2 scale-95 opacity-0'}`}>
                                            <button type="button" className="block w-full px-4 py-2 text-left hover:bg-[#FFDBAD]">Gerenciar categorias</button>
                                            <button type="button" className="block w-full px-4 py-2 text-left hover:bg-[#FFDBAD]">Gerenciar alunos</button>
                                            <button type="button" onClick={() => navigate(`/editar-projeto/${projeto.id}`)} className="block w-full px-4 py-2 text-left hover:bg-[#FFDBAD]">Editar Projeto</button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </section>
        </LayoutCoordenador>
    );
}