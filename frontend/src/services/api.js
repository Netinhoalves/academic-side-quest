const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

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
	const data = contentType.includes('application/json') ? await response.json() : null;

	if (!response.ok) {
		throw new Error(data?.detail || data?.message || 'Falha ao comunicar com a API');
	}

	return data;
}

export function login(payload) {
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