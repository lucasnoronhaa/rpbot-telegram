import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from datetime import datetime
from bs4 import BeautifulSoup
import investpy
#import json

# Token do bot configurado para quando subir ao GitHub
with open("config.json", "r") as config_file:
    config = json.load(config_file)
    TOKEN = config["token"]

# Glossário financeiro (dicionário de termos)
glossario_dict = {
    "juros compostos": "Juros compostos são os juros calculados sobre o valor inicial de um investimento, acrescidos dos juros que se acumularam ao longo do tempo.",
    "taxa de juros": "A taxa de juros é o valor que será cobrado sobre um empréstimo ou pago por um investimento, normalmente expresso em porcentagem.",
    "liquidez": "Liquidez é a facilidade com que um ativo pode ser convertido em dinheiro sem grandes perdas.",
    "renda fixa": "Renda fixa é um tipo de investimento onde as condições de rentabilidade são pré-estabelecidas, ou seja, você sabe o que esperar de retorno no momento da aplicação.",
    "ações": "Ações representam uma fração do capital social de uma empresa, tornando o investidor um sócio da mesma."
}

# Função para consultar a cotação de moedas
def get_exchange_rate(base_currency: str, target_currency: str) -> str:
    """Retorna a cotação de uma moeda em relação a outra"""
    api_key = "95701c5ca25d843c793ad216"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if target_currency in data["conversion_rates"]:
            rate = data["conversion_rates"][target_currency]
            return f"A cotação de {base_currency} para {target_currency} é {rate:.2f}"
        else:
            return f"Não foi possível encontrar a cotação para {target_currency}"
    else:
        return "Não consegui acessar os dados de cotação no momento."

# Função para calcular juros compostos
def calcular_juros_compostos(principal, taxa_juros, tempo):
    """Calcula o montante final de um investimento com juros compostos"""
    montante = principal * (1 + taxa_juros)**tempo
    return montante


# Função para consultar o glossário financeiro
async def glossario(update: Update, context: CallbackContext):
    """Comando para consultar um termo financeiro no glossário"""
    if context.args:
        # Junta todos os argumentos para formar o termo completo
        termo = " ".join(context.args).lower()
        definicao = glossario_dict.get(termo, "Termo não encontrado no glossário.")
        await update.message.reply_text(f"{termo.capitalize()}: {definicao}")
    else:
        await update.message.reply_text(
            "Por favor, forneça o termo financeiro no formato:\n"
            "`/glossario <termo>`\n"
            "Exemplo: `/glossario juros compostos`"
        )


# Comando /start
async def start(update: Update, context: CallbackContext):
    """Envia uma mensagem de boas-vindas quando o comando /start é usado"""
    await update.message.reply_text(
        "Olá! Eu sou o seu bot de finanças. Use os botões abaixo para navegar pelas opções."
    )
    await mostrar_menu_inicial(update.message)

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
            parse_mode="Markdown"
        )

# Função para lidar com os botões de interação
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
            "➤ /glossario <termo> - Consultar um termo financeiro\n"
            "➤ /juros_compostos - Calcular juros compostos"
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
            parse_mode="Markdown"
        )
    
    elif query.data == "juros_compostos":
        await query.message.reply_text(
            "Para calcular os juros compostos, envie os seguintes dados:\n"
            "`/juros_compostos <principal> <taxa_juros> <tempo>`\n"
            "Exemplo: `/juros_compostos 1000 0.05 12` (investimento de R$1000 a 5% ao mês durante 12 meses)",
            parse_mode="Markdown"
        )
        
    elif query.data == "glossario":
        await query.message.reply_text(
            "Para consultar um termo financeiro, envie:\n"
            "`/glossario <termo>`\n"
            "Exemplo: `/glossario juros compostos`"
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
        [InlineKeyboardButton("Cálculos Financeiros", callback_data="juros_compostos")],
        [InlineKeyboardButton("Glossário Financeiro", callback_data="glossario")],
        [InlineKeyboardButton("Sair", callback_data="sair")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "Escolha uma opção:",
        reply_markup=reply_markup
    )

# Função para o comando de juros compostos
async def juros_compostos(update: Update, context: CallbackContext):
    """Comando para calcular juros compostos"""
    if len(context.args) == 3:
        try:
            principal = float(context.args[0])  # Valor do investimento
            taxa_juros = float(context.args[1])  # Taxa de juros mensal
            tempo = int(context.args[2])  # Tempo em meses

            montante = calcular_juros_compostos(principal, taxa_juros, tempo)
            await update.message.reply_text(
                f"O montante final após {tempo} meses será: R${montante:.2f}"
            )
        except ValueError:
            await update.message.reply_text("Por favor, forneça valores válidos para os cálculos.")
    else:
        await update.message.reply_text(
            "Por favor, forneça os parâmetros no formato:\n"
            "`/juros_compostos <principal> <taxa_juros> <tempo>`\n"
            "Exemplo: `/juros_compostos 1000 0.05 12`"
        )

# Função para lidar com mensagens não comandos
async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text(update.message.text)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cotacao", cotacao))
app.add_handler(CommandHandler("juros_compostos", juros_compostos))
app.add_handler(CommandHandler("glossario", glossario))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

if __name__ == "__main__":
    print("Bot está rodando...")
    app.run_polling()
