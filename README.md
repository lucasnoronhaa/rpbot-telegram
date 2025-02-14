# BotTelegram

BotTelegram é um bot de Telegram desenvolvido para fornecer informações financeiras, como cotações de moedas, cálculos de juros compostos e definições de termos financeiros.

## Pré-requisitos

- Python 3.13 ou superior
- Poetry

## Configuração

1. Clone o repositório:
    ```sh
    git clone https://github.com/seu-usuario/BotTelegram.git
    cd BotTelegram
    ```

2. Instale as dependências:
    ```sh
    poetry install
    ```

3. Crie um arquivo `config.json` na raiz do projeto com o seguinte conteúdo:
    ```json
    {
        "token": "SEU_TOKEN_DO_TELEGRAM"
    }
    ```

 Test##es

Para rodar os testes, execute o seguinte comando:
```sh
poetry run pytest

## Funcionalidades

- **/start**: Envia uma mensagem de boas-vindas e exibe o menu inicial.
- **/cotacao**: Consulta a cotação de moedas.
  - `/cotacao <moeda>`: Exibe a cotação da moeda fornecida em relação a BRL, USD e EUR.
  - `/cotacao <moeda_base> <moeda_alvo>`: Exibe a cotação da moeda base em relação à moeda alvo.
- **/juros_compostos**: Calcula o montante final de um investimento com juros compostos.
  - `/juros_compostos <principal> <taxa_juros> <tempo>`: Calcula o montante final.
- **/glossario**: Consulta um termo financeiro no glossário.
  - `/glossario <termo>`: Exibe a definição do termo financeiro fornecido.

## Instalação

1. Clone o repositório:
    ```sh
    git clone https://github.com/seu-usuario/BotTelegram.git
    cd BotTelegram
    ```

2. Instale as dependências:
    ```sh
    poetry install
    ```

3. Crie um arquivo `config.json` na raiz do projeto com o  conteúdoseguinte:
    ```json
    {
        "token": "SEU_TOKEN_DO_TELEGRAM"
    }
    ```

## Uso

Para iniciar o bot, execute o seguinte comando:
```sh
poetry run python BotTelegram/bot.py

## Contribuição
1. Faça um fork do projeto.
2. Crie uma branch para sua feature (git checkout -b feature/nova-feature).
3. Commit suas alterações (git commit -m 'Adiciona nova feature').
4. Faça o push para a branch (git push origin feature/nova-feature).
5. Abra um Pull Request.