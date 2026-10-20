import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Inicio from './pages/Inicio';
import Login from './pages/Login';
import PainelADM from './pages/PainelADM';
import DashboardAluno from './pages/DashboardAluno';
import DashboardCoordenador from './pages/DashboardCoordenador';
import Projetos from './pages/Projetos';
import AdicionarProjeto from './pages/AdicionarProjeto';
import EditarProjeto from './pages/EditarProjeto';

function App() {
  return(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/login/:tipo" element={<Login />} />
        <Route path="/painel-adm" element={<PainelADM />} />
        <Route path="/aluno" element={<DashboardAluno />} />
        <Route path="/coordenador" element={<DashboardCoordenador />} />
        <Route path="/gerenciar-projetos" element={<Projetos />} />
        <Route path="/adicionar-projeto" element={<AdicionarProjeto />} />
        <Route path="/editar-projeto/:id" element={<EditarProjeto />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;