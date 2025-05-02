CREATE DATABASE PesquisaFuria;
USE PesquisaFuria;

CREATE TABLE tokenuser(
    id_token INT PRIMARY KEY AUTO_INCREMENT,
    token CHAR(5) NOT NULL,
    email_ref VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fansfuria (
    id_fa INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    estado CHAR(2) NOT NULL,
    email VARCHAR(255) NOT NULL,
    redeSocial VARCHAR(50) NOT NULL,
    idade INT NOT NULL,
    userRede VARCHAR(150) NOT NULL,
    interesseEmComp BOOL DEFAULT FALSE,
    membroFavorito VARCHAR(150),
    interesseCatalogo BOOL DEFAULT FALSE,
    modeloInteresse VARCHAR(255),
    estiloSugestao TEXT,
    mensagem TEXT NOT NULL,
    receberPromo BOOL DEFAULT FALSE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vizualizado BOOL DEFAULT FALSE
);

CREATE TABLE jogosfavoritos(
    id_jogo INT PRIMARY KEY AUTO_INCREMENT,
    id_fa INT NOT NULL,
    nomeJogo VARCHAR(50),
    FOREIGN KEY (id_fa) REFERENCES fansFuria(id_fa) ON DELETE CASCADE
);

CREATE TABLE funcionariosfuria(
    id_func INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    desativado BOOL DEFAULT FALSE,
    permisaoUser CHAR(5) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE noticiasfuria(
    id_noticia INT AUTO_INCREMENT PRIMARY KEY,
    img_noticia VARCHAR(255),
    texto_noticia TEXT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/*
INSERT INTO FuncionariosFuria (nome, email, senha, desativado, permisaoUser)
VALUES
('Gustavo Oliveira', 'gustavo.oliveira@furia.gg', 'senha123', FALSE, 'admin'),
('Larissa Mendes', 'larissa.mendes@furia.gg', 'larissa321', FALSE, 'comum'),
('Carlos Souza', 'carlos.souza@furia.gg', 'carlos456', TRUE, 'comum'),
('Fernanda Lima', 'fernanda.lima@furia.gg', 'fernanda789', FALSE, 'admin'),
('João Pedro', 'joao.pedro@furia.gg', 'jp@321', TRUE, 'comum');


/*
INSERT INTO fansFuria (
    nome, estado, email, redeSocial, userRede, interesseEmComp,
    membroFavorito, interesseCatalogo, modeloInteresse, estiloSugestao, receberPromo
) VALUES (
    'Ana Souza', 'RJ', 'ana.souza@example.com', 'Twitter', 'anasouza_rj',
    TRUE, 'Player2', FALSE, 'ModeloY', 'Gosto de roupas esportivas.', TRUE
);

-- 2º fã
INSERT INTO fansFuria (
    nome, estado, email, redeSocial, userRede, interesseEmComp,
    membroFavorito, interesseCatalogo, modeloInteresse, estiloSugestao, receberPromo
) VALUES (
    'Carlos Lima', 'MG', 'carlos.lima@example.com', 'Facebook', 'carlim_lima',
    FALSE, 'Player3', TRUE, 'ModeloZ', 'Prefiro um estilo mais casual.', FALSE
);

-- 3º fã
INSERT INTO fansFuria (
    nome, estado, email, redeSocial, userRede, interesseEmComp,
    membroFavorito, interesseCatalogo, modeloInteresse, estiloSugestao, receberPromo
) VALUES (
    'Beatriz Martins', 'BA', 'beatriz.martins@example.com', 'Instagram', 'bia_martins',
    TRUE, 'Player4', TRUE, 'ModeloA', 'Moda urbana e alternativa.', TRUE
);

INSERT INTO fansFuria (nome, estado, email, redeSocial, userRede, interesseEmComp, membroFavorito, interesseCatalogo, modeloInteresse, estiloSugestao, receberPromo) VALUES
('Lucas Andrade', 'SP', 'lucas.andrade@example.com', 'Twitter', 'lucas_and', TRUE, 'Player1', TRUE, 'ModeloX', 'Prefiro estilo streetwear.', TRUE),
('Mariana Oliveira', 'RJ', 'mariana.oliveira@example.com', 'Instagram', 'mari_oli', FALSE, 'Player2', FALSE, 'ModeloY', 'Moda casual e moderna.', FALSE),
('Felipe Costa', 'MG', 'felipe.costa@example.com', 'TikTok', 'felipec', TRUE, 'Player3', TRUE, 'ModeloZ', 'Gosto de peças esportivas.', TRUE),
('Amanda Souza', 'RS', 'amanda.souza@example.com', 'Facebook', 'amandasz', FALSE, 'Player4', FALSE, 'ModeloA', 'Alternativo e despojado.', TRUE),
('Ricardo Lima', 'PR', 'ricardo.lima@example.com', 'Twitter', 'ricardolim4', TRUE, 'Player5', TRUE, 'ModeloB', 'Minimalista e clean.', FALSE),
('Juliana Martins', 'SC', 'juliana.martins@example.com', 'Instagram', 'julimartins', TRUE, 'Player6', TRUE, 'ModeloC', 'Looks criativos e coloridos.', TRUE);


INSERT INTO JogosFavoritos (id_fa, nomeJogo) VALUES
(5, 'CS2'),
(5, 'Valorant'),
(5, 'R6');

-- Jogos da Mariana Oliveira
INSERT INTO JogosFavoritos (id_fa, nomeJogo) VALUES
(6, 'LOL'),
(6, 'Fifa');

-- Jogos do Felipe Costa
INSERT INTO JogosFavoritos (id_fa, nomeJogo) VALUES
(7, 'Apex'),
(7, 'PUBG'),
(7, 'Rocket League');

-- Jogos da Amanda Souza
INSERT INTO JogosFavoritos (id_fa, nomeJogo) VALUES
(8, 'Free Fire'),
(8, 'PUBG Mobile');

-- Jogos do Ricardo Lima
INSERT INTO JogosFavoritos (id_fa, nomeJogo) VALUES
(9, 'Kings League'),
(9, 'CS2');

-- Jogos da Juliana Martins
INSERT INTO JogosFavoritos (id_fa, nomeJogo) VALUES
(10, 'Furia Redram'),
(10, 'LOL'),
(10, 'Valorant');

*/