import mysql.connector
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def enviar_token_email(email_usuario):
    try:  # Conexão com o banco de dados
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=int(DB_PORT) if DB_PORT else 3306,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()


        # Gerar um token de 5 caracteres aleatórios
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

        # Verificar se o email já existe na tabela tokenuser
        select_query = "SELECT id_token FROM tokenuser WHERE email_ref = %s"
        cursor.execute(select_query, (email_usuario,))
        result = cursor.fetchone()

        if result:
            # Se o email já existe, atualize o token
            update_query = "UPDATE tokenuser SET token = %s WHERE email_ref = %s"
            cursor.execute(update_query, (token, email_usuario))
            conn.commit()

        else:
            # Se o email não existe, insira um novo token e o email na tabela
            insert_query = "INSERT INTO tokenuser (token, email_ref) VALUES (%s, %s)"
            cursor.execute(insert_query, (token, email_usuario))
            conn.commit()

        # Obter o ID do token (caso tenha sido inserido ou atualizado)
        select_query = "SELECT id_token FROM tokenuser WHERE email_ref = %s"
        cursor.execute(select_query, (email_usuario,))
        token_id = cursor.fetchone()[0]  # Pegando o ID do token


        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_REMETENTE')
        msg['To'] = email_usuario
        msg['Subject'] = f"Token para Autenticação Furia"

 
        corpo_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    width:100%;
                }}
                .container {{
                    width:50%;
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
                    margin: auto;
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #ddd;
                }}
                .content {{
                    margin-top: 20px;
                }}
                .content p {{
                    margin: 10px 0;
                    line-height: 1.5;
                }}
                .field-title {{
                    font-weight: bold;
                }}
                .token {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #007BFF;
                    margin-top: 20px;
                }}
                footer{{
                width:100%;
                }}
                .footerdiv {{
                    display:flex;
                    width:30%;
                    margin:auto;
                }}
                hr{{
                    width:50%;
                }}
                .footerdiv img {{
                    margin-right: 10px;  /* Espaço entre a imagem e o texto */
                }}
                .footerdiv p {{
                    text-align: center;
                    margin: 0;  /* Remove margens do parágrafo */
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Olá muito obrigado por enviar sua opinião e idéias</h2>
                </div>
                <div class="content">
                    <p><span class="field-title">Mensagem:</span> Para finalizar o Envio basta utilizar o token Abaixo</p>
                    <p><span class="field-title">Token de Verificação:</span> <span class="token">{token}</span></p>
                </div>
            </div>
        
            <footer>
                <p style="text-align: center;margin-bottom:20px">Nunca Compartilhe suas Informações privadas para maior segurança</p>
                <div class="footerdiv">
                    <img src="https://upload.wikimedia.org/wikipedia/pt/thumb/f/f9/Furia_Esports_logo.png/250px-Furia_Esports_logo.png" width="80px" />
                    <p>© 2024 Furia Gustavo Dev. All Rights Reserved.</p>
                </div>
                <hr/>
            </footer>
        
        </body>
        </html>
        """

        msg.attach(MIMEText(corpo_html, 'html'))    

        try:
            # Enviar o e-mail utilizando o servidor SMTP
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(os.getenv('EMAIL_REMETENTE'), os.getenv('EMAIL_SENHA'))
                server.sendmail(msg['From'], msg['To'], msg.as_string())

        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")

        return token_id  # Retorna o ID do token inserido no banco

    except mysql.connector.Error as err:
        print(f"Erro de banco de dados: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

