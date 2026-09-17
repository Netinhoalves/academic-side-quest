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
    '$2b$12$LTn2lXjw4j3.IZBvaVVzg.SBn50ce9FwVpn9FGp5vS54td0LehPGa',
    NULL,
    4,
    1
);
