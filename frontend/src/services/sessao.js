const ROTA_DO_PERFIL = {
    administrador: '/painel-adm',
    coordenador: '/coordenador',
    professor: '/coordenador',
    aluno: '/aluno',
};

export function lerUsuario() {
    try {
        const usuario = JSON.parse(localStorage.getItem('asq_usuario'));
        return usuario && typeof usuario === 'object' ? usuario : null;
    } catch {
        return null;
    }
} 

export function rotaDoPerfil(perfil) {
    return ROTA_DO_PERFIL[(perfil || '').toLowerCase()] || '/';
}

export function limparSessao() {
    localStorage.removeItem('asq_token');
    localStorage.removeItem('asq_usuario');
}