const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE !== 'false';

const DEMO_USERS = {
	aluno: {
		token: 'demo-token-aluno',
		usuario: { id: 1, nome: 'Ana Souza', email: 'ana.demo@academic-side-quest.local', perfil: 'aluno' },
	},
	coordenador: {
		token: 'demo-token-coordenador',
		usuario: { id: 2, nome: 'Carlos Oliveira', email: 'carlos.demo@academic-side-quest.local', perfil: 'coordenador' },
	},
};

export function startDemoSession(tipo) {
	const sessao = DEMO_USERS[tipo] || DEMO_USERS.aluno;
	localStorage.setItem('asq_token', sessao.token);
	localStorage.setItem('asq_usuario', JSON.stringify(sessao.usuario));
}

async function request(path, { method = 'GET', body, token } = {}) {
	const headers = {};

	if (body !== undefined) {
		headers['Content-Type'] = 'application/json';
	}

	if (token) {
		headers.Authorization = `Bearer ${token}`;
	}

	const response = await fetch(`${API_BASE_URL}${path}`, {
		method,
		headers,
		body: body !== undefined ? JSON.stringify(body) : undefined,
	});

	const contentType = response.headers.get('content-type') || '';
	const isJson = contentType.includes('application/json');
	const raw = isJson ? await response.text() : null;
	const data = raw ? JSON.parse(raw) : null;

	if (!response.ok) {
		throw new Error(data?.detail || data?.message || 'Falha ao comunicar com a API');
	}

	return data;
}

export function login(payload) {
	if (DEMO_MODE) {
		const tipo = payload?.tipo === 'docente' ? 'coordenador' : 'aluno';
		return Promise.resolve(DEMO_USERS[tipo]);
	}

	return request('/login', {
		method: 'POST',
		body: payload,
	});
}

export function getProfiles() {
	return request('/profiles');
}

export function getUsers(token) {
	return request('/usuarios', { token });
}

export function createUser(payload) {
	return request('/usuarios', {
		method: 'POST',
		body: payload,
	});
}

export function updateUser(userId, payload, token) {
	return request(`/usuarios/${userId}`, {
		method: 'PUT',
		body: payload,
		token,
	});
}

export function deleteUser(userId, token) {
	return request(`/usuarios/${userId}`, {
		method: 'DELETE',
		token,
	});
}