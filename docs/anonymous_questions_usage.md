# Sistema de Dúvidas Anônimas

## Visão Geral

O sistema de dúvidas anônimas permite que os alunos façam perguntas de forma anônima, facilitando a coleta de feedback e identificação de temas que geram mais dúvidas.

## Funcionalidades

### 1. Detecção Automática via Chat
- Quando um usuário faz uma pergunta no chat, o sistema automaticamente detecta se é uma dúvida
- A dúvida é salva anonimamente com um tema extraído automaticamente
- Não interfere no funcionamento normal do chat

### 2. Submissão Manual de Dúvidas
- Endpoint público para enviar dúvidas diretamente
- Permite especificar tema e pergunta

### 3. Dashboard para Administradores
- Visualização de todas as dúvidas (apenas admins)
- Estatísticas por tema
- Temas mais comuns

## Endpoints da API

### POST `/anonymous-questions`
Cria uma nova dúvida anônima.

**Body:**
```json
{
  "topic": "python",
  "question": "Como funciona o list comprehension em Python?"
}
```

**Response:**
```json
{
  "id": 1,
  "topic": "python",
  "question": "Como funciona o list comprehension em Python?",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### GET `/anonymous-questions` (Admin apenas)
Lista dúvidas com paginação e filtros.

**Query Parameters:**
- `topic` (opcional): Filtrar por tema
- `page` (default: 1): Número da página
- `per_page` (default: 20): Itens por página

**Response:**
```json
{
  "questions": [...],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

### GET `/anonymous-questions/stats` (Admin apenas)
Retorna estatísticas completas das dúvidas por tema, incluindo **todos os tópicos possíveis** (mesmo os que ainda não têm dúvidas).

**Response:**
```json
[
  {
    "topic": "Programação e Desenvolvimento",
    "question_count": 25,
    "latest_question_date": "2024-01-15T10:30:00Z"
  },
  {
    "topic": "APIs e Serviços Web", 
    "question_count": 12,
    "latest_question_date": "2024-01-14T15:20:00Z"
  },
  {
    "topic": "Segurança de Software",
    "question_count": 0,
    "latest_question_date": null
  }
]
```

### GET `/anonymous-questions/topics` (Admin apenas)
Retorna temas mais comuns das dúvidas já coletadas.

**Query Parameters:**
- `limit` (default: 10): Número máximo de temas

**Response:**
```json
["Programação e Desenvolvimento", "APIs e Serviços Web", "Banco de Dados"]
```

### GET `/anonymous-questions/available-topics` (Público)
Retorna todos os tópicos disponíveis para classificação.

**Response:**
```json
[
  {
    "name": "Programação e Desenvolvimento",
    "description": "Linguagens de programação, sintaxe, algoritmos básicos",
    "keywords_count": 24,
    "patterns_count": 4
  }
]
```

### GET `/anonymous-questions/topic-suggestions` (Público)
Retorna sugestões de tópicos baseado em texto parcial.

**Query Parameters:**
- `text`: Texto para buscar sugestões
- `limit` (default: 5): Número máximo de sugestões

**Response:**
```json
["Programação e Desenvolvimento", "APIs e Serviços Web"]
```

### GET `/anonymous-questions/topic-details/{topic_name}` (Público)
Retorna detalhes específicos de um tópico.

**Response:**
```json
{
  "name": "Programação e Desenvolvimento",
  "description": "Linguagens de programação, sintaxe, algoritmos básicos",
  "keywords": ["python", "java", "javascript", "..."],
  "patterns": ["como\\s+(programar|codificar)", "..."],
  "priority": 9
}
```

## Agente Inteligente de Classificação de Tópicos

O sistema utiliza um **Agente Especializado em Engenharia de Software** para classificação inteligente de tópicos.

### 🤖 Funcionalidades do Agente:

#### 1. **Detecção Automática de Dúvidas**
- Mensagens que terminam com "?"
- Indicadores expandidos: "como", "o que", "por que", "dúvida", "não entendo", "explique", "esclareça", "tenho dificuldade", etc.
- Padrões regex avançados para identificação contextual

#### 2. **Classificação de Tópicos Consistente**
O agente classifica dúvidas em **13 tópicos específicos de Engenharia de Software**:

1. **🔧 Programação e Desenvolvimento**
   - Linguagens, sintaxe, algoritmos básicos
   - *Keywords*: python, java, javascript, código, função, classe, etc.

2. **🏗️ Arquitetura e Design de Software** 
   - Padrões de design, SOLID, Clean Architecture
   - *Keywords*: arquitetura, mvc, solid, microserviços, singleton, etc.

3. **🗄️ Banco de Dados**
   - SQL, NoSQL, modelagem, otimização
   - *Keywords*: sql, postgresql, mongodb, query, join, etc.

4. **🌐 APIs e Serviços Web**
   - REST, GraphQL, integração de sistemas
   - *Keywords*: api, rest, jwt, endpoint, integração, etc.

5. **⚛️ Frameworks e Desenvolvimento Web**
   - React, Angular, Django, Flask, etc.
   - *Keywords*: react, angular, django, frontend, spa, etc.

6. **🚀 DevOps e Infraestrutura**
   - Docker, CI/CD, Cloud, Kubernetes
   - *Keywords*: docker, kubernetes, aws, pipeline, deploy, etc.

7. **🧪 Testes de Software**
   - Testes unitários, TDD, qualidade
   - *Keywords*: teste, tdd, unittest, coverage, mock, etc.

8. **📝 Controle de Versão**
   - Git, GitHub, branching, merge
   - *Keywords*: git, github, commit, merge, branch, etc.

9. **🔒 Segurança de Software**
   - Vulnerabilidades, criptografia, OWASP
   - *Keywords*: segurança, ssl, owasp, sql injection, etc.

10. **📋 Metodologias e Processos**
    - Scrum, Kanban, Agile
    - *Keywords*: scrum, agile, sprint, backlog, etc.

11. **🧮 Algoritmos e Estruturas de Dados**
    - Complexidade, ordenação, estruturas
    - *Keywords*: algoritmo, big o, árvore, grafo, etc.

12. **🛠️ Ferramentas de Desenvolvimento**
    - IDEs, editores, produtividade
    - *Keywords*: vscode, ide, debug, linter, etc.

13. **💡 Conceitos Gerais**
    - Conceitos gerais de computação
    - *Keywords*: engenharia, software, sistema, etc.

#### 3. **Sistema de Pontuação Inteligente**
- **Padrões Regex** (peso 10x): Identificação contextual avançada
- **Palavras-chave** (peso 1x): Correspondência exata de termos
- **Prioridade de Tópicos**: Desempate por relevância
- **Fallback**: Categoria "Outros" para casos não identificados

## Exemplos de Uso

### Dúvidas que serão detectadas automaticamente:
- "Como faço para instalar o Python?"
- "O que é machine learning?"
- "Por que meu código não funciona?"
- "Não entendo como usar o Docker"
- "Pode explicar o que é uma API REST?"

### Dúvidas que NÃO serão detectadas:
- "Obrigado pela explicação" (afirmação)
- "Entendi perfeitamente" (afirmação)
- "Vou testar agora" (ação)

## Privacidade

- **Completamente anônimo**: Não armazenamos identificação do usuário
- **Dados mínimos**: Apenas tema, pergunta e timestamp
- **Acesso restrito**: Apenas administradores podem visualizar as dúvidas coletadas

## Benefícios

1. **Para Alunos:**
   - Podem fazer perguntas sem constrangimento
   - Não precisam se identificar
   - Processo transparente

2. **Para Professores/Administradores:**
   - Identificam temas que geram mais dúvidas
   - Podem adaptar conteúdo baseado nas necessidades
   - Monitoram tendências de perguntas

3. **Para o Sistema:**
   - Melhora a qualidade do ensino
   - Fornece dados para análise
   - Não interfere na experiência do usuário 