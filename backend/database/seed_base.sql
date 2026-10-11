-- Task 07 e Task 35: dados básicos de teste e PPC TADS 2019
-- Senhas: admin@teste.com -> admin123; demais contas -> 123456.
-- IDs explícitos deixam as referências previsíveis e evitam duplicação por PK ao reexecutar.

INSERT IGNORE INTO Perfil (id, nome_perfil) VALUES
(1, 'Aluno'), (2, 'Professor'), (3, 'Coordenador'), (4, 'Administrador');

INSERT IGNORE INTO Usuario (id, nome, email, senha_hash, matricula, id_perfil, ativo) VALUES
(1, 'Administrador Teste', 'admin@teste.com', '$2b$12$tSDZ7g4R8lkEGnVISw7cX.RKqOf4UVgDM.1/.GSki4.lPmdfOUCN6', NULL, 4, 1),
(2, 'Coordenador Teste', 'coordenador@teste.com', '$2b$12$OWaCBWpF9JFJV1YVM5610e39Xb1UWqHt12Kdy4TPzaQoYRqrvVYqa', 'SERV001', 3, 1),
(3, 'Professor Teste', 'professor@teste.com', '$2b$12$OWaCBWpF9JFJV1YVM5610e39Xb1UWqHt12Kdy4TPzaQoYRqrvVYqa', 'SERV002', 2, 1),
(4, 'Aluno Teste', 'aluno@teste.com', '$2b$12$OWaCBWpF9JFJV1YVM5610e39Xb1UWqHt12Kdy4TPzaQoYRqrvVYqa', '2023000001', 1, 1);

INSERT IGNORE INTO Curso (id, nome, sigla, instituicao, ativo) VALUES
(1, 'Tecnologia em Análise e Desenvolvimento de Sistemas', 'TADS', 'IFMS - Campus Três Lagoas', 1);

INSERT IGNORE INTO PPC (id, id_curso, nome, ano, descricao, total_pontos, ativo, id_criador) VALUES
(1, 1, 'PPC TADS 2019', 2019, 'Projeto Pedagógico do Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas - IFMS Três Lagoas', 275, 1, 2);

INSERT IGNORE INTO Categoria (id, id_ppc, nome, descricao, limite_total, limite_semestre) VALUES
(1, 1, 'Atividades de aperfeiçoamento e enriquecimento cultural e esportivo', NULL, 120, 80),
(2, 1, 'Atividades de divulgação científica e de iniciação à docência', NULL, 100, 60),
(3, 1, 'Atividades de vivência acadêmica e profissional complementar', NULL, 100, 60),
(4, 1, 'Atividades de pesquisa ou extensão e publicações', NULL, 100, 80);

INSERT IGNORE INTO Subcategoria (id, id_categoria, codigo, nome, descricao, documentacao_pedida, limite_semestre) VALUES
(1, 1, '1.1', 'Participação como agente em atividades culturais: filme, teatro, apresentações artísticas, feiras, exposições, festivais e competições esportivas, bandas, coral, olimpíadas em geral', NULL, 'Relatório ou comprovante de participação', 30),
(2, 1, '1.2', 'Visitas técnicas e culturais: patrimônios tombados, cidades históricas, monumentos, museus, memoriais, escola-modelo, creches, berçários, ONGs, APAE e entidades afins, hospitais, laboratórios, instituições de ensino e pesquisa, empresas públicas e privadas e outras de interesse do curso', NULL, 'Relatório ou comprovante de participação', 30),
(3, 1, '1.3', 'Realização de cursos de língua estrangeira, informática e outros de formação cultural, social ou específica do âmbito do curso', NULL, 'Certificado/Declaração', 40),
(4, 1, '1.4', 'Trabalho voluntário, atividades comunitárias, associações de bairros, brigadas de incêndio e associações escolares', NULL, 'Declaração', 40),
(5, 2, '2.1', 'Monitoria remunerada ou voluntária', NULL, 'Certificado/Declaração', 60),
(6, 2, '2.2', 'Membro atuante em atividades técnico-científicas, tais como apresentação de trabalhos científicos, ministrar palestras, orientações técnicas supervisionadas e participação em bancas de debate', NULL, 'Certificado/Declaração', 30),
(7, 2, '2.3', 'Participação em atividades pedagógicas de observação', NULL, 'Certificado/Declaração', 20),
(8, 3, '3.1', 'Organização de eventos acadêmicos e festivais', NULL, 'Certificado/Declaração', 30),
(9, 3, '3.2', 'Representação discente em conselhos e entidades estudantis, liderança de turma, órgãos de classe e conselhos representativos', NULL, 'Certificado/Declaração', 20),
(10, 3, '3.3', 'Participação como ouvinte em eventos acadêmicos, tais como bancas de TCC, dissertação, teses', NULL, 'Relatório/Declaração', 18),
(11, 3, '3.4', 'Participação como ouvinte em congressos, seminários, simpósios e demais eventos relacionados ao curso de graduação ou áreas afins', NULL, 'Certificado/Declaração', 40),
(12, 3, '3.5', 'Participação em visita técnica relacionada à área de atuação', NULL, 'Relatório da visita, com anuência do professor responsável', 20),
(13, 3, '3.6', 'Participação em projetos de incubação', NULL, 'Certificado/Declaração', 45),
(14, 4, '4.1', 'Participação em projetos e grupos de pesquisa', NULL, 'Certificado/Declaração', 45),
(15, 4, '4.2', 'Participação em projetos e grupos de extensão', NULL, 'Certificado/Declaração', 45),
(16, 4, '4.3', 'Publicação de artigo científico completo em revista ou periódico', NULL, 'Artigo publicado', 50),
(17, 4, '4.4', 'Publicação de resumos de artigo científico em revista ou periódico', NULL, 'Resumo publicado', 50),
(18, 4, '4.5', 'Publicação de matérias ou notas em jornais e meios eletrônicos', NULL, 'Publicação', 10);

INSERT IGNORE INTO RegraPontuacao (id, id_subcategoria, titulo_exibicao, tipo, multiplicador, operacao, tipo_documento) VALUES
(1, 1, '5 pontos por atividade', 'atividade', 5, 'SOMA', 'Relatório ou comprovante de participação'),
(2, 2, '5 pontos por visita', 'visita', 5, 'SOMA', 'Relatório ou comprovante de participação'),
(3, 3, '1 ponto por hora', 'hora', 1, 'MULTIPLICACAO', 'Certificado/Declaração'),
(4, 4, '10 pontos por participação comprovada', 'participação', 10, 'SOMA', 'Declaração'),
(5, 5, '15 pontos por participação', 'participação', 15, 'SOMA', 'Certificado/Declaração'),
(6, 6, '10 pontos por participação', 'participação', 10, 'SOMA', 'Certificado/Declaração'),
(7, 6, '15 pontos por participação, caso o trabalho seja da área específica do curso', 'participação na área', 15, 'SOMA', 'Certificado/Declaração'),
(8, 7, '5 pontos por participação', 'participação', 5, 'SOMA', 'Certificado/Declaração'),
(9, 8, '1 ponto por hora', 'hora', 1, 'MULTIPLICACAO', 'Certificado/Declaração'),
(10, 8, '10 pontos por evento, caso o documento não apresente a carga horária', 'evento', 10, 'SOMA', 'Certificado/Declaração'),
(11, 9, '5 pontos por participação', 'participação', 5, 'SOMA', 'Certificado/Declaração'),
(12, 10, '3 pontos por participação', 'participação', 3, 'SOMA', 'Relatório/Declaração'),
(13, 11, '1 ponto por hora', 'hora', 1, 'MULTIPLICACAO', 'Certificado/Declaração'),
(14, 11, '10 pontos por evento, caso o documento não apresente a carga horária', 'evento', 10, 'SOMA', 'Certificado/Declaração'),
(15, 12, '1 ponto por hora', 'hora', 1, 'MULTIPLICACAO', 'Relatório da visita, com anuência do professor responsável'),
(16, 12, '8 pontos por evento, caso o documento não apresente a carga horária', 'evento', 8, 'SOMA', 'Relatório da visita, com anuência do professor responsável'),
(17, 13, '7,5 pontos por mês', 'mês', 7.5, 'MULTIPLICACAO', 'Certificado/Declaração'),
(18, 14, '7,5 pontos por mês', 'mês', 7.5, 'MULTIPLICACAO', 'Certificado/Declaração'),
(19, 15, '7,5 pontos por mês', 'mês', 7.5, 'MULTIPLICACAO', 'Certificado/Declaração'),
(20, 16, '25 pontos por publicação', 'publicação', 25, 'SOMA', 'Artigo publicado'),
(21, 16, '30 pontos por publicação em revista ou periódico da área', 'publicação na área', 30, 'SOMA', 'Artigo publicado'),
(22, 17, '15 pontos por publicação', 'publicação', 15, 'SOMA', 'Resumo publicado'),
(23, 17, '20 pontos por publicação em revista ou periódico da área', 'publicação na área', 20, 'SOMA', 'Resumo publicado'),
(24, 18, '5 pontos por publicação', 'publicação', 5, 'SOMA', 'Publicação');

INSERT IGNORE INTO Aluno (id, id_usuario, id_ppc, data_ingresso, status) VALUES
(1, 4, 1, '2023-02-01', 'ATIVO');
