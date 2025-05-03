<h1>Neste Projeto Contém uma API para um software Web para a equipe furia </h1>
<h3>Objetivos da Api</h3>
<ul>
  <li>
    Fazer o Envio de informaçãoes entre Cliente e Funcionario e Funcionario para Cliente
  </li>
  <li>
    Tratar de forma segura os dados recebidos 
  </li>
  <li>
    Estar otimizada para muitas requisições Simultaneas
  </li>
  <li>
    Ter o controle de requisições para evitar ataques DDOS
  </li>
  <li>
    Fazer Conexão com o banco de dados de forma segura a fim de evitar Injeções SQL
  </li>
</ul>
<h3>Questões de Segurança da Informação</h3>
<p>
  Para esse Projeto foi feito uso de hash seguro de senhas e tokens JWT para ceder informações delicadas somente para pessoal autorizado e uso de limiter a fim de evitar exesso de requisições por IPs.
</p>
<h3>Ferramentas Utilizadas</h3>
<p>
  Abaixo segue as ferramentas utilizadas para Criar a Aplicação
</p>
<ul>
  <li>
    Sistema Operacional Windows 10
  </li>
  <li>
    Python versão 3.10.10
  </li>
  <li>
    Pip versão 25.0.1
  </li>
  <li>
    IDE PyCharm Community Edition 2024.1.1
  </li>
</ul>
<p>Agora segue abaixo Ferramentas para Criação do Código via NodeJS Npm</p>
  <li>
    Flask para criação de Server com suporte a requisições REST
  </li>
  <li>
    Webdriver-manager e Selenium para Scraping de dados simples
  </li>
  <li>
    Gemini GenerativeAI para criação de IA generativa utilizando API google AI
  </li>
  <li>
    JWT e bcrypt para criação de tokens Seguros e hash de valores
  </li>
  <li>
    JWT e bcrypt para criação de tokens Seguros e hash de valores
  </li>
  <li>
    Python dotenv utilizado para Criação de variaveis de Ambiente
</li>
<li>
    Mysql connector python para efetuar requisições para banco MySql
</li>
<h2>Como deve ser Feito para Efetuar a Integração do Código?</h2>
<p>
  Para efetuar a integração do Código foi o pip install de todos os itens presentes no arquivo requirements.txt com o código pip install -r requirements ele fará o dowload automaticamente, o mesmo está presente no repositório e por fim deve ser retirado os comentarios nas linhas 869,870,871 e 872 do arquivo app.py e então ser rodado o comando python app.py somente caso o terminal já esteja aberto na pasta com o arquivo presente, nele foi inserido um certificado de teste para https com a finalidade de fazer a criação de cookie seguro em cross-site é recomendado que o mesmo seja mantido.
</p>
<p>OBS:o seguinte item gunicorn foi utilizado para uso da aplicação corretamente no deploy publico e por isso em testes locais o mesmo é opcional, caso for feito o uso do mesmo o comando está presente em Procfile, mas o comentarios das linhas 869,870,871 e 872 devem ser mantidas nesse caso</p>
<h3>
  Passo a Passo:
</h3>
<p>
  Efetue o Download do Pycharm em sua Máquina, segue o link de Dowload: https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC, após download crie um novo projeto fazendo a criação do ambiente virtual e o python.
</p>
<p>
  Após isso ou baixe o repositório em zip e ao extrair a pasta cole seus conteudos na pasta com o ambiente virtual instalado e então faça os pip install pelo terminal da aplicação, ou então abra o git bash e rode o comando git clone https://github.com/GustavoFerreira143/ApiProjetoFuriaGG.git / dentro da pasta criada no pycharm assim todos os itens serão inseridos corretamente.
</p>
<p>
  Por fim Basta abrir o terminal na pasta criada e rodar o Python app.py para abrir o server do projeto.
</p>

<h1>Estrutura de Código</h1>
<p>O código está bem estruturado e espero que de simples compreenssão </p>
<p>Estarei inserindo aqui Detalhes sobre o Funcionamento do Projeto e em caso seja necessário algum Debug</p>
<p>OBS:a lógica da aplicação é dividida da seguinte forma app <- cria as rotas e trativas de dados após tratativas envia dados para funções presentes nas pastas do repositório sendo </p>
<pre>
    /ConsultasFuncionarios <- funções especificas somente disponibilizada a funcionarios
    /ConsultasBanco <- funções onde a pagina de clientes e funcionarios podem trabalhar em paralelo
    /scrapFunction <- seu nome é auto explicativo, coleta informações sobre a furia e retorna para uso na página.
</pre>
<pre>
|_furiaBanco.sql <- Criação do banco de Dados de Toda aplicação 
|
|_requirements.txt <- Conjunto de Pacotes utilizados e que é necessário ser feito Download
|   
|_ConsultasBanco
|        |_CadastraFa.py <- função cadastrar_ou_atualizar_usuario onde cadastra fa no banco.
|        |
|        |_ColetaNoticias.py <- função recebe_noticias busca as noticias do banco e retorna.
|        |    
|        |_ConfirmaUser.py <- função ConfirmaDadosUser recebe os dados token, id e email para fazer validação de dados com base no banco.
|        |    
|        |_GeraToken.py <- função enviar_token_email daz envio de token por email ao usuario, armazena no banco e retorna o id do token criado
|
|_ConsultasFuncionarios
|                |_BuscaUser.py <- função obter_todos_usuarios função pesquisa todos ou usuários filtrados de usuarios funcionarios com base em parametro e retorna os valores encontrados
|                |
|                |_CriaGraficoPersonalizado.py <- função gerar_dados_personalizados_grafico, recebe parametros e retorna dados em quantidade refente aos valores solicitados.
|                |
|                |_DashboardFuntions.py <- contém todas as funções pré definidas para coletar informações quantitativas de valores e ser inseridas no dashboard.
|                |
|                |_DeletaNoticia.py <- função deletaNoticia recebe os parametros da noticia especifica e então apaga do banco de dados a informação com base no id e depois apaga a img salva na pasta imgs. 
|                |  
|                |_EditaUser.py <- função atualizar_funcionario recebe informações pelos parametros e então busca pelo id e atualiza todos os dados do funcionario em especifico
|                |
|                |_EnviaNoticias.py <- função AdicionaNoticia recebe informações pelos parametros e então modifica o nome da imagem para formato Year Mouth Day Hour: Minute: Second para inserir uma imagem de texto unico evitando sobrescrição e então salva esses dados no banco
|                |
|                |_EnvioEmailPrmocional.py <- funções enviaEmailUsers e enviaEmailUsers a função enviaEmailUsers pega os parametros digitados pelo usuário retorna os emails dos usuários referentes e então no forEach dos dados chama enviaEmailUsers e então envia os anuncios especificos aos usuários
|                |
|                |_InserUser.py <- função inserir_funcionario_furia cria novo funcionario para acesso ao sistema e converte a senha em hash seguro
|                |
|                |_LoginUser.py <- função autenticar_usuario recebe dados de usuário e então valida as informaçãoes com base nas salvas no sistema.
|                |
|                |_RetornaInfosPesquisa.py <- função retornaUsers retorna dados dos fãns que fizeram as pesquisas do site furia para visualização dos dados de forma personalizada.
|                |    
|                |_ mudaVizualizado.py <- função altera_visualizado altera o status visualizado para true do usuário fazendo com que seus dados sejam setados com já visto.
|
|_scrapsFunction <- pasta de funções para scrap de dados furia.
|         
|_ app.py <- todo Servidor de Apis onde os dados são recebidos.
    |
    |_linhas 1 até 46 <- importação de funções e frameworks necessários para a aplicação
    |
    |_linhas 52 até 65 <- abertura do a dotenv para carregamento de váriaveis de ambiente e Configurações do modelo de IA
    |
    |_linhas 68 até 76 <- criação do app Flask para inicio do server com configurações de CORS e Limiters para segurança do server e inserção, criação de variavel para tornar a pasta imgs uma pasta online
    |
    |_linhas 84 até 101 <- funções limpar_mensagem para tirar caracteres considerados maliciosos e validar_input responsavel por validações de texto a fim de evitar erros cometidos pelo usuario
    |
    |_linhas 105 até 133 <- criação das funções token_required e admin_required, essas funções são as primeiras verificações para páginas protegidas onde para usuários comuns é rodado somente token_required que busca um token JWT valido recebido pelo cliente e para páginas sensiveis é rodado token_required e admin_required que verifica se dentro do token contém o valor que é inserido em sua criação adicionando o tipo de usuario.
    |
    |_linhas 136 até 138 <- inserção da pasta imgs para ser possivel fazer a visualização de arquivos
    |
    |_linhas 143 até 155 <- criação da rota <strong> /coletaNoticias </strong> que é responsavel por chamar a função recebe_noticias() que deve retornar se as noticias atualizadas pelos funcionarios em tempo real.
    |
    |_linhas 161 até 179 <- criação da rota <strong> /estaAoVivo </strong> que é responsavel por chamar a função coletaAoVivo que retorna se a furia está ao vivo ou não no kings league e retorna as informações ao cliente
    |
    |_linhas 185 até 408 <- criação da rota <strong> /conversas </strong> que recebe a mensagem do usuario para a IA, utiliza a função limpar_mensagem presente na linha 84 e então cria o prompt de configuração da IA com as informações que a mesma deve saber sobre a furia e datalhes
    |                       a partir da linha 283 é gerado a resposta para o usuário com base nos conhecimentos da IA e por pré configuração caso seja detectado perguntas especificas a mesma retornas valores pré definidos para disparar os if e elifs especificos   
    |                       todos os ifs exeto os referente ao Kings League utilizam a função obter_dados_player com sua respectiva URL para retornar os dados solicitados com precisão e então por final retorna a resposta personalizada ao usuário
    |
    |_linhas 416 até 481 <- criação de rota <strong> /feedback </strong> essa rota é responsavel pelo recebimento do feedback do usuário completo junto com token de confirmação e dados para dar proceguimento ao salvamento no banco de dados, de inicio ela faz o envio do token, id 
    |                        e email para a função ConfirmaDadosUser que verifica se as informações batem exatamente com a salvas no banco e então da proceguimento depois efetua a verificação de todas as variaveis recebidas formatando da forma esperada para evitar erros e faldes
    |                        caso não seja encontrado nenhuma irregularidade faz uma verificação com IA dos dados para verificação se não há uso de discursos de ódio fraudes e linguagem de baixo calão nos envios e então a mesma retorna valores pré defindos para OK para dados validos e ENCONTRADO para dados irregulares
    |                        se tudo OK faz chama a função cadastrar_ou_atualizar que cadastra novos usuário ou atualiza caso já existentes com base em data recebido
    |    
    |_linhas 487 até 505 <- é criado a rota /enviaToken essa rota é responsavel pelo envio do token de usuário com base no email recebido e então retorna o id da linha em que o token do email especifico foi armazenado a função de envio e retorno do id é enviar_token_email(email)
    |
    |_linhas 513 até 543 <- Criação de rota <strong> /func/conferelogin/login </strong> essa função é especifica para tela de funcionarios, ela recebe dados de email e senha trata os dados e envia para a função autenticar_usuario(email, senha) que por sua vez faz a conferencia de usuário e em caso sucesso retorna o token de usuario, tipo de permissão e se foi sucesso ou não e então o código faz a verificações e retorna o token personalizado por meio de um cookie seguro
    |
    |_linhas 549 até 565 <- Criação de rota <strong> /func/conferelogin/VerificaLogado </strong> que recebe o token de usuário e retorna se o mesmo está logado ou não e se o token é valido
    |
    |_linhas 571 até 582 <- Criação de rota <strong> /func/conferelogin/logout essa função zera a validade atual do token jwt do usuário fazendo o mesmo se tornar inválido e então o mesmo é desvinculado
    |
    |_linhas 586 até 621 <- Criação de rota <strong>/func/insereuserfurioso/user</strong> nesta rota já é iniciado a verificação de token jwt tratadas a partir da linha 105 onde ele verifica se o token existe e se é admin caso seja pega as informações recebidas
    |                        pelo usuário valida utilizando a função de validar_input encontradas a partir da linha 84 e então se tudo ok envia para a função inserir_funcionario_furia que faz a inserção dos dados no banco de dados
    |
    |_linhas 627 até 646 <- Criação de rota <strong>/func/editaUserDados/user</strong> nesta função onde só é autorizado acesso admin ele recebe filtros opcionais e valores referentes ao carregamento de página dinâmica e então chama a função obter_todos_usuarios
    |                       que faz a busca e retorna todos os funcionarios cadastrados no banco de funcionarios e então os retorna ao usuário.     
    |
    |_linhas 652 até 671 <- Criação de rota <strong>/func/editaUserDados/enviar</strong> nesta função onde só é autorizado acesso admin ele recebe alteração de dados de usuário e então envia para atualizar_usuario função onde é atualizados todos os dados com base no id recebido
    |
    |_linhas 676 até 701 <- Criação de rota <strong>/func/enviaEmailusers/aut</strong> essa função onde só é autorizado acesso com token valido, recebe trata dados recebidos para envio de emails para os cliente e então envia os dados para enviaEmailUsers que envia email para todos os clientes que aceitaram a promoção com base no especificado pelo usuário
    |
    |_linhas 706 até 743 <- Criação de rota <strong>/enviafunc/usuario/noticia</strong> essa função onde só é autorizado acesso com token valido, recebe imagem e texto para inserção de nova noticia, é validado o tipo de extenção e se válido envia para a função AdicionaNoticia que salva a imagem em imgs e envia o nome para o banco para futura formatação.
    |
    |_linhas 749 até 766 <- Criação de rota <strong>/notic/func/encia/delet</strong> essa função onde só é autorizado acesso com token valido, recebe informações de noticia para deletar a mesma do banco, após validar as informações chama a função deletaNoticia
    |                       e então o mesmo é deletado da pasta imgs e do banco de dados
    |
    |_linhas 772 até 795 <- Criação de rota <strong>/verif/pesquisa/user/rec</strong> essa função onde só é autorizado acesso com token valido, recebe filtros opcionais enviado pelo usuario e informações de pagina para carregamento dinamico da página de vizualização de FeedBack de Usuários, onde essas informações é enviada para a função retornaUsers e então retorna os valores ao usuário.
    |
    |_linhas 799 até 819 <- Criação de rota <strong> /atualiz/user/fa/view</strong> essa função onde só é autorizado acesso com token valido, recebe o id do fan para atualizar como visualizado a sua respectiva carterinha de dados, a função de atualização é a altera_vizualizado(id).
    |
    |_linhas 824 até 840 <- Criação de rota <strong>/rec/dash/views/user</strong> essa função onde só é autorizado acesso com token valido, dispara diversas funções que retornam dados personalizados para inserção em gráficos de rendimento.
    |
    |_linhas 844 até 867 <- Criação de rota <strong>/rec/gera/views/grafic</strong> essa função onde só é autorizado usuarios com token admin faz o retorno de pesquisas personalizadas para criação de tabela dinâmica instantanea a função que recebe os dados para inserir na tabela é a gerar_dados_personalizados_grafico
    |
    |_linhas 870 até 873 <-função main disparada caso queira iniciar o servidor local sem gunicorn. 
</pre>
<h1 align="center">Por Fim Aproveite</h1>

