<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# AtomCode Daily

**Consulta o plano atual do AtomCode e tenta receber um CodingPlan gratuito na ordem Max → Pro → Lite quando não há um plano válido.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/AtomCode-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> A documentação completa em chinês está em [../README.md](../README.md).

## ✨ Recursos principais

- Lê `status-v2` e não repete a coleta quando já existe um plano válido.
- Tenta `Max → Pro → Lite` em sequência e para no primeiro resultado confirmado.
- Dá prioridade a um `expires_at` interpretável em vez de `remaining_days`, permitindo renovar planos expirados.
- Trata `duplicate: true` como plano já existente para evitar downgrade.
- Renova access tokens e salva o refresh token rotacionado quando há um caminho de estado gravável.
- Suporta várias contas, proxy e notificações PushPlus, Bark, WeCom e DingTalk.

## 🚀 Configuração mínima

Execute na raiz do repositório:

```bash
python -m pip install -r requirements.txt
python atomcode_auth.py --file path/to/auth.toml
```

Conta única:

```text
ATOMCODE_TOKEN=ACCESS_TOKEN
ATOMCODE_REFRESH_TOKEN=REFRESH_TOKEN
```

Várias contas:

```text
ATOMCODE_TOKENS=
Principal|ACCESS_TOKEN|REFRESH_TOKEN|1799999999000
Secundária|ACCESS_TOKEN|REFRESH_TOKEN
```

Consulta sem coleta:

```bash
python atomcode_daily.py --query
```

Execução normal:

```bash
python atomcode_daily.py
python atomcode_daily.py --only 1
python atomcode_daily.py --no-notify
```

## 🐧 Qinglong

```bash
pip3 install requests
```

Defina `ATOMCODE_TOKENS` nas variáveis do painel e crie uma tarefa:

```text
20 8 * * * python3 atomcode_daily.py
```

Os tokens rotacionados são gravados em `atomcode_state.json`. Use um diretório gravável e persistente; `ATOMCODE_STATE_FILE` permite alterar o caminho.

## ☁️ GitHub Actions

O workflow fica em [../.github/workflows/daily.yml](../.github/workflows/daily.yml). Por padrão, apenas a execução manual está ativa; o bloco de agendamento está comentado.

| Secret | Obrigatório | Uso |
| :--- | :---: | :--- |
| `ATOMCODE_TOKENS` | Um dos dois | Tokens de várias contas |
| `ATOMCODE_TOKEN` | Um dos dois | Access token de uma conta |
| `ATOMCODE_REFRESH_TOKEN` | Opcional | Refresh token de uma conta |
| `ATOMCODE_PROXY` | Opcional | Proxy |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | Opcional | Notificações |

Para ativar o agendamento, remova os comentários e lembre-se de que o cron do GitHub usa UTC. O Actions não preserva o arquivo de estado local; atualize o Secret se o refresh token for rotacionado.

## 🔧 Variáveis principais

| Variável | Descrição |
| :--- | :--- |
| `ATOMCODE_TOKENS` | Várias contas: `nome\|access\|refresh\|expires_at\|created_at\|expires_in` |
| `ATOMCODE_TOKEN` | Access token de uma conta |
| `ATOMCODE_REFRESH_TOKEN` | Refresh token de uma conta |
| `ATOMCODE_EXPIRES_AT` | Timestamp ou data/hora interpretável |
| `ATOMCODE_AUTH_FILE` | Caminho do arquivo JSON de autenticação |
| `ATOMCODE_STATE_FILE` | Caminho do arquivo de estado |
| `ATOMCODE_PROXY` | Proxy HTTP(S) / SOCKS |
| `ATOMCODE_NO_NOTIFY` | `1` desativa notificações |

## 📊 Critério de sucesso

Um plano válido, `success: true` ou `duplicate: true` confirmam sucesso nesta execução. Falta de token, conta inexistente ou recusa nos três planos resulta em falha. Um HTTP 200 isolado não confirma o recebimento.

## 🔒 Privacidade

- O projeto não coleta nem envia dados da conta.
- Os logs não exibem tokens completos.
- Não envie `atomcode_state.json`, `.env`, access tokens ou refresh tokens ao Git.
- Guarde credenciais apenas em variáveis locais, GitHub Secrets ou variáveis do Qinglong.

## 🔗 Links

- [Releases](https://github.com/L0NE-6/AtomCode-Daily/releases)
- [Issues](https://github.com/L0NE-6/AtomCode-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
