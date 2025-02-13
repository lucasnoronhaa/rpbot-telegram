import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from datetime import datetime
from bs4 import BeautifulSoup

TOKEN = "7532075980:AAGkvoFDHBVK6Md_r1SAOCBGAHIJUGs9q9w"

def obter_resumo_ativo(ticker):
    # Consulta o ativo na Investing.com
    url = f"https://br.investing.com/equities/{ticker.lower()}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None  # Caso a consulta falhe
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Pega as informações de nome, valor, variação, etc.
    try:
        nome = soup.find('h1', class_='instrumentHeader__name').text.strip()
        valor = soup.find('span', class_='instrument-price_last__price').text.strip()
        variacao = soup.find('span', class_='instrument-price_change').text.strip()
        descricao = soup.find('div', class_='instrument-overview').text.strip()

        resumo = {
            "nome": nome,
            "valor": valor,
            "variacao": variacao,
            "descricao": descricao,
        }

        return resumo
    except AttributeError:
        return None  # Retorna None se algum dado não for encontrado

def obter_historico_ativo(ticker):
    # Consulta histórico de preços (últimos 5 dias) na Investing.com
    url = f"https://br.investing.com/equities/{ticker.lower()}-historical-data"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None  # Caso a consulta falhe
    
    soup = BeautifulSoup(response.text, 'html.parser')
    tabela = soup.find('table', class_='genTbl closedTbl historicalTbl')

    if not tabela:
        return "Histórico não disponível."

    historico = ""
    linhas = tabela.find_all('tr')

    for linha in linhas[1:6]:  # Pegando os primeiros 5 dias
        colunas = linha.find_all('td')
        if len(colunas) > 1:
            data = colunas[0].text.strip()
            fechamento = colunas[4].text.strip()
            historico += f"{data} - Fechamento: R$ {fechamento}\n"
    
    return historico

# Função de comando para consultar a ação
async def acao(update: Update, context: CallbackContext):
    if context.args:
        ticker = context.args[0].upper()  # Obtém o ticker da ação (ex: PETR4)
        resumo = obter_resumo_ativo(ticker)
        if resumo is None:
            await update.message.reply_text("Ativo não encontrado. Verifique o ticker e tente novamente.")

# Função para consultar a cotação de moedas
def get_exchange_rate(base_currency: str, target_currency: str) -> str:
    """Retorna a cotação de uma moeda em realação a outra"""
    api_key = "95701c5ca25d843c793ad216"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if target_currency in data["conversion_rates"]:
            rate = data["conversion_rates"][target_currency]
            return f"A cotação de {base_currency} para {target_currency} é {rate:.2f}"
        else:
            return f"Não foi possível encontrar a contação para {target_currency}"
    else:
        return "Não consegui acessar os dados de cotação no momento."


# Comando /cotacao
async def cotacao(update: Update, context: CallbackContext):
    """Comando /cotacao para consultar a cotação de moedas"""
    if len(context.args) == 1:  # Se o usuário digitar apenas 1 moeda
        base_currency = context.args[0].upper()
        target_currencies = ["USD", "EUR", "BRL"]   # Moedas padrão
        resultados = []

        for target_currency in target_currencies:
            if target_currency != base_currency: # Evitar converter para a própria moeda
                rate = get_exchange_rate(base_currency, target_currency)
                resultados.append(rate)
        
        await update.message.reply_text("\n".join(resultados))
    
    elif len(context.args) == 2:  # Se o usuário digitar 2 moedas
        base_currency = context.args[0].upper()
        target_currency = context.args[1].upper()
        rate = get_exchange_rate(base_currency.upper(), target_currency.upper())
        await update.message.reply_text(rate)
    
    else:  # Se o usuário digitar mais de 2 moedas
        await update.message.reply_text(
            "Por favor, forneça uma ou duas moedas no formato:\n."
            "`/cotacao <moeda>` (exibe BRL, USD e EUR)\n"
            "`/cotacao <moeda_base> <moeda_alvo>` (exemplo: `/cotacao USD BRL`)",
            parse_mode = "Markdown"
            )

async def start(update: Update, context: CallbackContext):
    """Mensagem de boas-vindas com botões interativos"""
    keyboard = [
        [InlineKeyboardButton("Ajuda", callback_data="ajuda")],
        [InlineKeyboardButton("Ver Horário Atual", callback_data="horario")],
        [InlineKeyboardButton("Cotação", callback_data="cotacao")],
        [InlineKeyboardButton("Ações", callback_data="acao")],
        [InlineKeyboardButton("Sair", callback_data="sair")],
        
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Olá! Eu sou seu bot do Telegram. Como posso te ajudar?",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: CallbackContext):
    """Responde quando o usuário clica nos botões"""
    query = update.callback_query
    await query.answer()  # Confirma o clique do usuário

    if query.data == "ajuda":
        comandos = (
            "Aqui estão alguns comandos que você pode usar:\n\n"
            "➤ /start - Reiniciar o bot\n"
            "➤ /horario - Mostrar o horário atual\n"
            "➤ /cotacao <moeda_base> <moeda_alvo>` - Consultar a cotação de moedas\n"
            "➤ /acao <ticker> - Consultar informações sobre uma ação\n"
        )
        await query.message.reply_text(comandos)

    elif query.data == "horario":
        agora = datetime.now().strftime("%H:%M:%S")
        await query.message.reply_text(f"Horário atual: {agora}")
    
    elif query.data == "cotacao":
        await query.message.reply_text(
            "Para consultar a cotação, envie:\n"
            "`/cotacao <moeda_base> <moeda_alvo>`\n"
            "Exemplo: `/cotacao USD BRL`",
            parse_mode = "Markdown"
            )
    
    elif query.data == "acao":
        await query.message.reply_text(
            "Para consultar uma ação, envie:\n"
            "`/acao <ticker>`\n"
            "Exemplo: `/acao PETR4`",
            parse_mode = "Markdown"
            )
        

    # Exibir o menu inicial após qualquer ação
    await mostrar_menu_inicial(query.message)

# Função para exibir o menu inicial com os botões
async def mostrar_menu_inicial(message):
    """Exibe o menu inicial com os botões novamente"""
    keyboard = [
        [InlineKeyboardButton("Ajuda", callback_data="ajuda")],
        [InlineKeyboardButton("Ver Horário Atual", callback_data="horario")],
        [InlineKeyboardButton("Cotação", callback_data="cotacao")],
        [InlineKeyboardButton("Ações", callback_data="acao")],
        [InlineKeyboardButton("Sair", callback_data="sair")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "Escolha uma opção:",
        reply_markup=reply_markup
    )

#  Função para lidar com mensagens não comandos
async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text(update.message.text)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cotacao", cotacao))
app.add_handler(CommandHandler("acao", acao))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

if __name__ == "__main__":
    print("Bot está rodando...")
    app.run_polling()
