import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Inicio from './pages/Inicio';
import Login from './pages/Login';
import Cadastro from './pages/Cadastro';
import PainelADM from './pages/PainelADM';
import DashboardAluno from './pages/DashboardAluno';
import DashboardCoordenador from './pages/DashboardCoordenador';
import Projetos from './pages/Projetos';
import AdicionarProjeto from './pages/AdicionarProjeto';
import EditarProjeto from './pages/EditarProjeto';
import Categorias from './pages/Categorias';
import AdicionarCategoria from './pages/AdicionarCategoria';
import EditarCategoria from './pages/EditarCategoria';
import Subcategorias from './pages/Subcategorias';
import AdicionarSubcategoria from './pages/AdicionarSubcategoria';
import EditarSubcategoria from './pages/EditarSubcategoria';
import Cursos from './pages/Cursos';
import AdicionarCurso from './pages/AdicionarCurso';
import EditarCurso from './pages/EditarCurso';
import EmBreve from './pages/EmBreve';

function App() {
  return(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/login" element={<Login />} />
        <Route path="/login/:tipo" element={<Login />} />
        <Route path="/cadastro/aluno" element={<Cadastro />} />
        <Route path="/painel-adm" element={<PainelADM />} />
        <Route path="/aluno" element={<DashboardAluno />} />
        <Route path="/coordenador" element={<DashboardCoordenador />} />
        <Route path="/comprovar-horas" element={<EmBreve titulo="Comprovar horas" perfisPermitidos={['Aluno']} />} />
        <Route path="/visualizar-resultados" element={<EmBreve titulo="Visualizar resultados" perfisPermitidos={['Aluno']} />} />
        <Route path="/visualizar-alunos" element={<EmBreve titulo="Visualizar alunos" perfisPermitidos={['Coordenador', 'Professor']} />} />
        <Route path="/gerenciar-projetos" element={<Projetos />} />
        <Route path="/adicionar-projeto" element={<AdicionarProjeto />} />
        <Route path="/adicionar-projeto/categoria" element={<AdicionarCategoria />} />
        <Route path="/adicionar-projeto/subcategoria" element={<AdicionarSubcategoria />} />
        <Route path="/editar-projeto/:id" element={<EditarProjeto />} />
        <Route path="/projeto/:projetoId/categorias" element={<Categorias />} />
        <Route path="/projeto/:projetoId/categorias/adicionar" element={<AdicionarCategoria />} />
        <Route path="/projeto/:projetoId/categorias/adicionar/subcategoria" element={<AdicionarSubcategoria />} />
        <Route path="/projeto/:projetoId/categorias/:categoriaId/editar" element={<EditarCategoria />} />
        <Route path="/projeto/:projetoId/categoria/:categoriaId/subcategorias" element={<Subcategorias />} />
        <Route path="/projeto/:projetoId/categoria/:categoriaId/subcategorias/adicionar" element={<AdicionarSubcategoria />} />
        <Route path="/projeto/:projetoId/categoria/:categoriaId/subcategorias/:subcategoriaId/editar" element={<EditarSubcategoria />} />
        <Route path="/gerenciar-cursos" element={<Cursos />} />
        <Route path="/adicionar-curso" element={<AdicionarCurso />} />
        <Route path="/editar-curso/:id" element={<EditarCurso />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;