CREATE TABLE IF NOT EXISTS Perfil (
    id INT PRIMARY KEY,
    nome_perfil VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS Usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    matricula VARCHAR(30) UNIQUE,
    id_perfil INT NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_usuario_perfil
        FOREIGN KEY (id_perfil)
        REFERENCES Perfil(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS PPC (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    versao VARCHAR(30) NOT NULL,
    total_pontos DECIMAL(10,2) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    id_professor INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ppc_professor
        FOREIGN KEY (id_professor)
        REFERENCES Usuario(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_ppc_total_pontos
        CHECK (total_pontos > 0),

    CONSTRAINT chk_ppc_datas
        CHECK (data_fim >= data_inicio)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS Categoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_ppc INT NOT NULL,
    nome VARCHAR(150) NOT NULL,
    limite_total DECIMAL(10,2) NOT NULL,
    limite_semestre DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_categoria_ppc
        FOREIGN KEY (id_ppc)
        REFERENCES PPC(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT uq_categoria_ppc_nome
        UNIQUE (id_ppc, nome),

    CONSTRAINT chk_categoria_limite_total
        CHECK (limite_total > 0),

    CONSTRAINT chk_categoria_limite_semestre
        CHECK (limite_semestre > 0),

    CONSTRAINT chk_categoria_limite_semestre_total
        CHECK (limite_semestre <= limite_total)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS Subcategoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    limite_semestre DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_subcategoria_categoria
        FOREIGN KEY (id_categoria)
        REFERENCES Categoria(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT uq_subcategoria_categoria_nome
        UNIQUE (id_categoria, nome),

    CONSTRAINT chk_subcategoria_limite_semestre
        CHECK (limite_semestre > 0)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS RegraPontuacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_subcategoria INT NOT NULL,
    titulo_exibicao VARCHAR(1000) NOT NULL,
    tipo VARCHAR(255) NOT NULL,
    multiplicador DECIMAL(10,2) NOT NULL,
    operacao ENUM('SOMA', 'MULTIPLICACAO') NOT NULL,
    tipo_documento VARCHAR(255) NOT NULL,

    CONSTRAINT fk_regra_subcategoria
        FOREIGN KEY (id_subcategoria)
        REFERENCES Subcategoria(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_regra_multiplicador
        CHECK (multiplicador > 0)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS PeriodoPPC (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_ppc INT NOT NULL,
    numero_semestre TINYINT UNSIGNED NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,

    CONSTRAINT fk_periodo_ppc
        FOREIGN KEY (id_ppc)
        REFERENCES PPC(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT uq_periodo_ppc_semestre
        UNIQUE (id_ppc, numero_semestre),

    CONSTRAINT chk_periodo_datas
        CHECK (data_fim >= data_inicio),

    CONSTRAINT chk_periodo_numero_semestre
        CHECK (numero_semestre > 0)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS Aluno (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_ppc INT NOT NULL,

    CONSTRAINT uq_aluno_usuario
        UNIQUE (id_usuario),

    CONSTRAINT fk_aluno_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES Usuario(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_aluno_ppc
        FOREIGN KEY (id_ppc)
        REFERENCES PPC(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS Solicitacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_aluno INT NOT NULL,
    id_periodo_ppc INT NOT NULL,
    data_atividade DATE NOT NULL,
    id_regra_pontuacao INT NOT NULL,
    quantidade DECIMAL(10,2),
    arquivo VARCHAR(500) NOT NULL,
    pontos_calculados DECIMAL(10,2) NOT NULL,
    pontos_aproveitados DECIMAL(10,2),
    status ENUM('PENDENTE', 'APROVADA', 'REJEITADA') NOT NULL DEFAULT 'PENDENTE',
    id_professor INT,
    observacao TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_solicitacao_aluno
        FOREIGN KEY (id_aluno)
        REFERENCES Aluno(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_solicitacao_periodo_ppc
        FOREIGN KEY (id_periodo_ppc)
        REFERENCES PeriodoPPC(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_solicitacao_regra
        FOREIGN KEY (id_regra_pontuacao)
        REFERENCES RegraPontuacao(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_solicitacao_professor
        FOREIGN KEY (id_professor)
        REFERENCES Usuario(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_solicitacao_quantidade
        CHECK (quantidade IS NULL OR quantidade > 0),

    CONSTRAINT chk_solicitacao_pontos_calculados
        CHECK (pontos_calculados >= 0),

    CONSTRAINT chk_solicitacao_pontos_aproveitados
        CHECK (pontos_aproveitados IS NULL OR pontos_aproveitados >= 0),

    CONSTRAINT chk_solicitacao_aproveitados_limite
        CHECK (
            pontos_aproveitados IS NULL
            OR pontos_aproveitados <= pontos_calculados
        )
) ENGINE=InnoDB;


INSERT IGNORE INTO Perfil (id, nome_perfil) VALUES
(1, 'Aluno'),
(2, 'Professor'),
(3, 'Coordenador'),
(4, 'Administrador');
