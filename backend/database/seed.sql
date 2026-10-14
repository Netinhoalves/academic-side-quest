-- Task 07: Inserção dos dados básicos para testes

INSERT IGNORE INTO Perfil (id, nome_perfil) VALUES
(1, 'Aluno'),
(2, 'Professor'),
(3, 'Coordenador'),
(4, 'Administrador');

INSERT IGNORE INTO Usuario (
    nome,
    email,
    senha_hash,
    matricula,
    id_perfil,
    ativo
) VALUES (
    'Administrador Teste',
    'admin@teste.com',
    'admin123',
    NULL,
    4,
    1
);
