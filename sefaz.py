import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# URL do site
url = "https://www.nfe.fazenda.gov.br/portal/disponibilidade.aspx"

# Faz a requisição HTTP
response = requests.get(url)

# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    # Obtém o conteúdo HTML da página
    html_content = response.text

    # Cria o objeto BeautifulSoup para analisar o HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Encontra todas as linhas ímpares ou pares com o conteúdo "bola_vermelho_P.png"
    linhas_vermelhas = soup.find_all("tr", {"class": ["linhaImparCentralizada", "linhaParCentralizada"]})
    linhas_com_problema = []

    for linha in linhas_vermelhas:
        if linha.find("img", {"src": "imagens/bola_vermelho_P.png"}):
            estado = linha.find("td").text
            linhas_com_problema.append(estado)

    # Verifica se existem linhas com problema
    if linhas_com_problema:
        mensagem = "<h2>Os seguintes estados estão com problemas:</h2> <h3>{}</h3>".format(", ".join(linhas_com_problema))
        
        # Faz a requisição HTTP para a segunda URL
        response2 = requests.get("https://www.nfe.fazenda.gov.br/portal/principal.aspx")

        # Verifica se a requisição foi bem-sucedida
        if response2.status_code == 200:
            # Obtém o conteúdo HTML da página
            html_content2 = response2.text

            # Cria o objeto BeautifulSoup para analisar o HTML
            soup2 = BeautifulSoup(html_content2, "html.parser")

            # Encontra a tabela com o ID "ctl00_ContentPlaceHolder1_gdvCtgAtiva"
            tabela_ativa = soup2.find("table", {"id": "ctl00_ContentPlaceHolder1_gdvCtgAtiva"})

            # Verifica se a tabela ativa foi encontrada
            if tabela_ativa:
                # Extrai o texto da tag <caption> dentro da tabela ativa
                caption_text_ativa = tabela_ativa.caption.get_text(strip=True)

                # Extrai o texto das tags <td> dentro da tabela ativa
                td_texts_ativa = [td.get_text(strip=True) for td in tabela_ativa.find_all("td")]

                # Adiciona as informações da tabela ativa à mensagem
                mensagem += "<h3><strong>Situação da contingência:</strong></h3>"
                mensagem += "<strong>{}</strong><br>".format(caption_text_ativa)
                for td_text_ativa in td_texts_ativa:
                    mensagem += "{}<br>".format(td_text_ativa)
            else:
                print("Tabela ativa não encontrada.")

            # Encontra a tabela com o ID "ctl00_ContentPlaceHolder1_gdvCtgAgendada"
            tabela_agendada = soup2.find("table", {"id": "ctl00_ContentPlaceHolder1_gdvCtgAgendada"})

            # Verifica se a tabela agendada foi encontrada
            if tabela_agendada:
                # Extrai o texto da tag <caption> dentro da tabela agendada
                caption_text_agendada = tabela_agendada.caption.get_text(strip=True)

                # Extrai o texto das tags <td> dentro da tabela agendada
                td_texts_agendada = [td.get_text(strip=True) for td in tabela_agendada.find_all("td")]

                # Adiciona as informações da tabela agendada à mensagem
                mensagem += "<h3><strong>Situação do agendamento da contingência:</strong></h3>"
                mensagem += "<strong>{}</strong><br>".format(caption_text_agendada)
                for td_text_agendada in td_texts_agendada:
                    mensagem += "{}<br>".format(td_text_agendada)
                    mensagem += "<br>===== E-mail automático para verificação do SEFAZ ====="
            else:
                print("Tabela agendada não encontrada.")

    else:
        mensagem = "<h2>Todos os estados estão funcionando normalmente</h2>"

    # Configurações do e-mail
    email_de = "EMAIL AQUI"  #  e-mail remetente
    email_para = ["EMAIL AQUI","EMAIL AQUI"]  # e-mail do destinatário
    senha_smtp = "SENHA DO EMAIL"  # senha do seu e-mail remetente

    # Cria o objeto MIMEMultipart
    msg = MIMEMultipart()
    msg["Subject"] = "Disponibilidade da SEFAZ"
    msg["From"] = email_de
    msg["To"] = ", ".join(email_para)

    # Adiciona o corpo do e-mail como HTML
    corpo_email = MIMEText(mensagem, "html")
    msg.attach(corpo_email)

    # Envia o e-mail usando o servidor SMTP com SSL
    servidor_smtp = "SERVIDOR DE ENVIO"
    porta_smtp = 465

    with smtplib.SMTP_SSL(servidor_smtp, porta_smtp) as servidor:
        servidor.login(email_de, senha_smtp)
        servidor.sendmail(email_de, email_para, msg.as_string())

    print("E-mail enviado com sucesso!")
else:
    print("Erro ao acessar a URL:", response.status_code)
