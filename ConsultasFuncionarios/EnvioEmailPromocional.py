import mysql.connector
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from email.utils import parseaddr

# Carregar variáveis de ambiente
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def conectar_banco():
    return mysql.connector.connect(
        host=DB_HOST,
        port=int(DB_PORT) if DB_PORT else 3306,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
def enviaEmailUsers(assunto, mensagem1, linkimg, mensagem2, destino):
    try:
        conn = conectar_banco()
        cursor = conn.cursor()

        if destino == 'todos':
            query = """
                SELECT email FROM fansfuria
                WHERE receberPromo = TRUE
            """
        elif destino == 'catalogo':
            query = """
                SELECT email FROM fansfuria
                WHERE receberPromo = TRUE AND interesseCatalogo = TRUE
            """
        elif destino == 'games':
            query = """
                SELECT email FROM fansfuria
                WHERE receberPromo = TRUE AND interesseEmComp = TRUE
            """
        else:
            raise ValueError("Destino inválido")

        cursor.execute(query)
        emails = [row[0] for row in cursor.fetchall()]

        for email in emails:
            if email and '@' in parseaddr(email)[1]:
                enviar_email_custom(
                    email_usuario=email,
                    assunto=assunto,
                    mensagem1=mensagem1 if mensagem1 else None,
                    img=linkimg if linkimg else None,
                    mensagem2=mensagem2 if mensagem2 else None
                )
            else:
                print(f"E-mail inválido ignorado: {email}")

        cursor.close()
        conn.close()

    except Exception as e:
        raise Exception(f"Erro ao enviar e-mails: {str(e)}")


def enviar_email_custom(email_usuario, assunto, mensagem1=None, img=None, mensagem2=None):
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_REMETENTE')
    msg['To'] = email_usuario
    msg['Subject'] = assunto

    # Corpo do email
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
                text-align: center;
            }}
            .header {{
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
            footer{{
                width:100%;
                margin-top: 30px;
            }}
              .footerdiv {{
                    display:flex;
                    width:30%;
                    margin:auto;
                }}
            .footerdiv p {{
                margin: 0;
            }}
            hr{{
                width:50%;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>{assunto}</h2>
            </div>
            <div class="content">
    """

    if mensagem1:
        corpo_html += f"<p>{mensagem1}</p>"

    if img:
        corpo_html += f'<img src="{img}" alt="Imagem da promoção" style="max-width:50%; height:auto; border-radius:8px; margin: 20px 0;">'

    if mensagem2:
        corpo_html += f"<p>{mensagem2}</p>"

    corpo_html += """
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
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(os.getenv('EMAIL_REMETENTE'), os.getenv('EMAIL_SENHA'))
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            return True
    except Exception as e:
        return False