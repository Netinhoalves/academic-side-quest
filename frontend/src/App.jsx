import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Inicio from './pages/Inicio';
import Login from './pages/Login';
import Cadastro from './pages/Cadastro';

function App() {
  return(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/login/:tipo" element={<Login />} />
        <Route path="/cadastro/:tipo" element={<Cadastro />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;