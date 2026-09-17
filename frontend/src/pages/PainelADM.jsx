import { useMemo, useState } from 'react';
import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Pencil } from 'lucide-react';
import { SelectField } from '../components/SelectField';
import logoSigla from '../assets/logo-sigla.png';
import { deleteUser, getProfiles, getUsers, updateUser } from '../services/api';

const camposEdicao = [
	{ id: 'nome', label: 'Nome completo', type: 'text' },
	{ id: 'email', label: 'E-mail', type: 'email' },
	{ id: 'matricula', label: 'Matrícula', type: 'text' },
];

const statusOptions = [
	{ value: 'true', label: 'Ativo' },
	{ value: 'false', label: 'Inativo' },
];

const formatarData = (valor) => {
	if (!valor) {
		return '—';
	}

	const data = new Date(valor);

	if (Number.isNaN(data.getTime())) {
		return valor;
	}

	return new Intl.DateTimeFormat('pt-BR').format(data);
};

export default function PainelADM() {
	const [token] = useState(() => localStorage.getItem('asq_token'));
	const [pesquisa, setPesquisa] = useState('');
	const [filtro, setFiltro] = useState('todos');
	const [dados, setDados] = useState([]);
	const [perfis, setPerfis] = useState([]);
	const [linhaAberta, setLinhaAberta] = useState(null);
	const [modalAberto, setModalAberto] = useState(false);
	const [formulario, setFormulario] = useState(null);
	const [carregando, setCarregando] = useState(() => Boolean(token));
	const [salvando, setSalvando] = useState(false);
	const [erro, setErro] = useState(() => (token ? '' : 'Faça login novamente para acessar o painel administrativo.'));

	useEffect(() => {
		let ativo = true;

		if (!token) {
			return () => {
				ativo = false;
			};
		}

		Promise.all([getProfiles(), getUsers(token)])
			.then(([listaPerfis, listaUsuarios]) => {
				if (!ativo) {
					return;
				}

				setPerfis(listaPerfis);
				setDados(listaUsuarios);
			})
			.catch((error) => {
				if (ativo) {
					setErro(error.message || 'Falha ao carregar os dados do painel');
				}
			})
			.finally(() => {
				if (ativo) {
					setCarregando(false);
				}
			});

		return () => {
			ativo = false;
		};
	}, [token]);

	const perfisPorId = useMemo(() => {
		return new Map(perfis.map((perfil) => [String(perfil.id), perfil.nome_perfil]));
	}, [perfis]);

	const filtrosPerfil = useMemo(() => {
		return [
			{ value: 'todos', label: 'Todos' },
			...perfis.map((perfil) => ({ value: String(perfil.id), label: perfil.nome_perfil })),
		];
	}, [perfis]);

	const resultadoFiltrado = useMemo(() => {
		const termo = pesquisa.trim().toLowerCase();

		return dados.filter((item) => {
			const perfil = perfisPorId.get(String(item.id_perfil)) || 'Sem perfil';
			const passaFiltro = filtro === 'todos' || String(item.id_perfil) === filtro;
			const passaPesquisa = !termo || [item.nome, item.email, item.matricula, perfil, item.ativo ? 'ativo' : 'inativo']
				.filter(Boolean)
				.some((valor) => String(valor).toLowerCase().includes(termo));

			return passaFiltro && passaPesquisa;
		});
	}, [dados, filtro, perfisPorId, pesquisa]);

	const abrirModal = (item) => {
		setFormulario({
			...item,
			id_perfil: String(item.id_perfil),
			ativo: String(Boolean(item.ativo)),
		});
		setModalAberto(true);
	};

	const fecharModal = () => {
		setModalAberto(false);
		setFormulario(null);
	};

	const confirmarEdicao = async () => {
		if (!formulario) {
			return;
		}

		setSalvando(true);
		setErro('');

		try {
			const token = localStorage.getItem('asq_token');
			const atualizado = await updateUser(
				formulario.id,
				{
					nome: formulario.nome,
					email: formulario.email,
					matricula: formulario.matricula,
					id_perfil: Number(formulario.id_perfil),
					ativo: formulario.ativo === 'true',
				},
				token
			);

			setDados((atual) => atual.map((item) => (item.id === atualizado.id ? atualizado : item)));
			setLinhaAberta(atualizado.id);
			fecharModal();
		} catch (error) {
			setErro(error.message || 'Falha ao salvar alterações');
		} finally {
			setSalvando(false);
		}
	};

	const excluirRegistro = async () => {
		if (!formulario) {
			return;
		}

		setSalvando(true);
		setErro('');

		try {
			const token = localStorage.getItem('asq_token');
			await deleteUser(formulario.id, token);
			setDados((atual) => atual.filter((item) => item.id !== formulario.id));
			setLinhaAberta((atual) => (atual === formulario.id ? null : atual));
			fecharModal();
		} catch (error) {
			setErro(error.message || 'Falha ao excluir usuário');
		} finally {
			setSalvando(false);
		}
	};

	const estiloBotao = 'bg-color-blue text-white font-jaro tracking-widest rounded-md border-b-4 border-[#0c1840] hover:bg-color-blue-light active:border-b-0 active:translate-y-1 transition-all flex items-center justify-center';

	return (
		<div className="min-h-screen bg-[#FFF1E4] text-color-blue font-jaro">
			<header className="h-[74px] bg-color-orange shadow-[0_4px_12px_rgba(0,0,0,0.15)] flex items-center justify-between px-4 sm:px-6">
				<div className="flex items-center gap-3 text-white">
					<div className="w-12 h-12 rounded-full overflow-hidden border-2 border-white shadow-md bg-[#fff3e2] flex items-center justify-center">
						<span className="text-color-blue text-sm font-bold">Admin</span>
					</div>
					<div className="leading-none">
						<p className="text-sm tracking-widest font-bold">Admin</p>
						<p className="text-[11px] opacity-90 tracking-wide">Gestão acadêmica</p>
					</div>
				</div>

				<img src={logoSigla} alt="Logo ASQ" className="h-12 sm:h-14 w-auto object-contain drop-shadow-md" />
			</header>

			<main className="max-w-[920px] mx-auto px-4 sm:px-6 py-6 sm:py-8">
				<section className="p-0">
					{erro && (
						<div className="mb-4 rounded-[12px] bg-red-100 border border-red-300 px-4 py-3 text-red-700 text-sm">
							{erro}
						</div>
					)}

					{carregando && (
						<div className="rounded-[12px] bg-[#FFF8F0] px-4 py-6 text-center text-color-blue shadow-[0_10px_18px_rgba(0,0,0,0.14)] mb-4">
							Carregando usuários...
						</div>
					)}

					<div className="bg-[#FFF8F0] rounded-[18px] shadow-[0_10px_18px_rgba(0,0,0,0.14)] p-2 sm:p-3 mb-5">
						<div className="flex flex-col sm:flex-row gap-2 sm:items-center">
							<div className="flex-1 bg-white rounded-[16px] shadow-[0_8px_14px_rgba(0,0,0,0.12)] px-3 py-2 flex items-center gap-2">
								<span className="text-2xl text-color-orange-bright">⌕</span>
								<input
									value={pesquisa}
									onChange={(event) => setPesquisa(event.target.value)}
									type="text"
									placeholder="Buscar usuário, perfil, e-mail..."
									className="w-full outline-none bg-transparent text-lg text-color-blue placeholder:text-[#3853A4]"
								/>
							</div>

							<div className="min-w-[170px]">
								<SelectField
									label=""
									id="filtro-categoria"
									name="filtro-categoria"
									options={filtrosPerfil}
									required={false}
									value={filtro}
									placeholderLabel="Filtrar por perfil"
									onChange={(event) => setFiltro(event.target.value)}
								/>
							</div>
						</div>
					</div>

					<div className="rounded-[12px] overflow-hidden">
						<div className="grid grid-cols-[1.6fr_0.9fr_0.7fr] bg-[#ffd08b] px-4 py-2 text-[24px] leading-none">
							<span>Usuário</span>
							<span>Perfil</span>
							<span className="text-right">Ver mais</span>
						</div>

						<div className="divide-y divide-[#e4be83]">
							{resultadoFiltrado.map((item, index) => {
								const aberto = linhaAberta === item.id;
								const cargo = perfisPorId.get(String(item.id_perfil)) || 'Sem perfil';

								return (
									<div key={item.id} className={index % 2 === 0 ? 'bg-[#ffb747]' : 'bg-[#ffd089]'}>
										<button
											type="button"
											onClick={() => setLinhaAberta(aberto ? null : item.id)}
											className="w-full grid grid-cols-[1.6fr_0.9fr_0.7fr] items-center px-4 py-3 text-left text-[18px] hover:bg-[#ffbf5f]/70 transition-colors"
										>
											<span>{item.nome}</span>
											<span>{cargo}</span>
											<span className="justify-self-end text-xl">{aberto ? '▴' : '▾'}</span>
										</button>

										<div
											aria-hidden={!aberto}
											className={`relative overflow-hidden bg-[#fdf1dd] shadow-[inset_0_10px_18px_rgba(0,0,0,0.12)] text-[15px] sm:text-[16px] transition-[max-height,opacity,transform,padding] duration-300 ease-out ${aberto ? 'max-h-[240px] opacity-100 translate-y-0 px-4 py-3 pointer-events-auto' : 'max-h-0 opacity-0 -translate-y-1 px-4 py-0 pointer-events-none'}`}
										>
												<div className="grid gap-3 sm:grid-cols-[1.4fr_1fr] sm:items-start">
													<div className="space-y-1">
														<p className="text-color-blue font-bold">Matrícula: {item.matricula || '—'}</p>
														<p className="text-color-blue">E-mail: {item.email}</p>
														<p className="text-color-blue">Perfil: {cargo}</p>
														<p className="text-color-blue">Criado em: {formatarData(item.created_at)}</p>
													</div>
													<div className="sm:self-end sm:justify-self-end w-full">
														<p className="text-color-blue sm:text-right">Status: {item.ativo ? 'Ativo' : 'Inativo'}</p>
														<p className="text-color-blue sm:text-right">Atualizado em: {formatarData(item.updated_at)}</p>
													</div>
												</div>
												<button
													type="button"
													onClick={() => abrirModal(item)}
													className="absolute top-3 right-3 sm:top-4 sm:right-4 text-color-blue hover:text-color-blue-light transition-colors"
													aria-label={`Editar ${item.nome}`}
												>
													<Pencil aria-hidden="true" className="w-8 h-8" />
												</button>
											</div>
									</div>
								);
							})}
						</div>
					</div>
				</section>
			</main>

			{modalAberto && formulario && (
				<div className="fixed inset-0 z-50 bg-black/45 flex items-center justify-center p-4">
					<div className="relative w-full max-w-[560px] bg-color-yellow rounded-[15px] shadow-[0_18px_30px_rgba(0,0,0,0.3)] overflow-hidden">
						<div className="absolute top-0 left-0 w-24 h-24 bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.45),_transparent_65%)]" />
						<div className="absolute bottom-0 right-0 w-24 h-24 bg-[radial-gradient(circle_at_bottom_right,_rgba(17,33,64,0.12),_transparent_65%)]" />

						<div className="relative z-10 p-5 sm:p-6">
							<h2 className="text-color-blue text-3xl sm:text-[40px] font-normal mb-5">Editar cadastro</h2>

							<div className="grid gap-3">
								<div className="grid gap-3 sm:grid-cols-2">
									{camposEdicao.map((campo) => (
										<div key={campo.id} className="flex flex-col w-full">
											<label htmlFor={campo.id} className="text-color-blue font-bold text-base sm:text-lg mb-1">
												{campo.label}
											</label>
											<input
												id={campo.id}
												type={campo.type}
												value={formulario[campo.id] ?? ''}
												onChange={(event) => setFormulario((atual) => ({ ...atual, [campo.id]: event.target.value }))}
												className="w-full bg-[#D5800BD4] rounded-[10px] px-3 py-2 sm:py-3 text-gray-900 outline-none focus:ring-2 focus:ring-color-blue transition-shadow shadow-[inset_0_4px_8px_rgba(0,0,0,0.15)]"
											/>
										</div>
									))}
								</div>

								<div className="grid gap-3 sm:grid-cols-2">
									<div className="flex flex-col w-full">
										<label htmlFor="id_perfil" className="text-color-blue font-bold text-base sm:text-lg mb-1">Perfil</label>
										<SelectField
											label=""
											id="id_perfil"
											name="id_perfil"
											options={perfis.map((perfil) => ({ value: String(perfil.id), label: perfil.nome_perfil }))}
											required={false}
											value={formulario.id_perfil}
											placeholderLabel="Selecione o perfil"
											onChange={(event) => setFormulario((atual) => ({ ...atual, id_perfil: event.target.value }))}
										/>
									</div>

									<div className="flex flex-col w-full">
										<label htmlFor="ativo" className="text-color-blue font-bold text-base sm:text-lg mb-1">Status</label>
										<SelectField
											label=""
											id="ativo"
											name="ativo"
											options={statusOptions}
											required={false}
											value={formulario.ativo}
											placeholderLabel="Selecione o status"
											onChange={(event) => setFormulario((atual) => ({ ...atual, ativo: event.target.value }))}
										/>
									</div>
								</div>

								<div className="flex gap-4 sm:gap-6 mt-4 justify-center flex-wrap">
									<button type="button" onClick={fecharModal} className={`${estiloBotao} w-[130px] py-2 text-lg`} disabled={salvando}>
										Voltar
									</button>
									<button type="button" onClick={confirmarEdicao} className={`${estiloBotao} w-[130px] py-2 text-lg`} disabled={salvando}>
										{salvando ? 'Salvando...' : 'Confirmar'}
									</button>
									<button type="button" onClick={excluirRegistro} className="bg-color-red text-white font-jaro tracking-widest rounded-md border-b-4 border-[#7d1712] hover:opacity-90 active:border-b-0 active:translate-y-1 transition-all flex items-center justify-center w-[130px] py-2 text-lg" disabled={salvando}>
										{salvando ? 'Excluindo...' : 'Excluir'}
									</button>
								</div>
							</div>
						</div>
					</div>
				</div>
			)}

			{!carregando && resultadoFiltrado.length === 0 && (
				<div className="max-w-[920px] mx-auto px-4 sm:px-6 pb-8 text-center text-color-blue">
					Nenhum registro encontrado para a busca atual.
				</div>
			)}

			<div className="fixed bottom-4 left-4">
				<Link to="/" className="bg-white/80 rounded-full px-4 py-2 text-color-blue shadow-md text-sm sm:text-base">
					Voltar para o início
				</Link>
			</div>
		</div>
	);
}
