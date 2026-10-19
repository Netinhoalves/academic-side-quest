import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Inicio from './pages/Inicio';
import Login from './pages/Login';
import Cadastro from './pages/Cadastro';
import PainelADM from './pages/PainelADM';
import DashboardAluno from './pages/DashboardAluno';
import DashboardCoordenador from './pages/DashboardCoordenador';

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
      </Routes>
    </BrowserRouter>
  )
}

export default App;