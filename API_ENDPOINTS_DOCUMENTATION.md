# Documentação da API - Endpoints

## Visão Geral
Esta documentação descreve os endpoints disponíveis para **Dúvidas Anônimas** e **Estatísticas do Chat**.

## 🔐 Autenticação

- **Endpoints Públicos**: Não requerem autenticação
- **Endpoints Admin**: Requerem token JWT no header `Authorization: Bearer {token}` + role ADMIN

---

# 📝 Anonymous Questions Endpoints

## 1. Criar Dúvida Anônima
**`POST /anonymous-questions`**

**Autenticação**: ❌ Público

**Request Body**:
```json
{
  "topic": "string",
  "question": "string"
}
```

**Response (200)**:
```json
{
  "id": 123,
  "topic": "React",
  "question": "Como usar hooks no React?",
  "created_at": "2024-01-15T10:30:00Z",
  "classified_topic": "Frontend Development"
}
```

**Códigos de Status**:
- `200`: Dúvida criada com sucesso
- `500`: Erro interno do servidor

---

## 2. Listar Dúvidas Anônimas
**`GET /anonymous-questions`**

**Autenticação**: 🔒 Admin

**Query Parameters**:
- `topic` (string, opcional): Filtrar por tema específico
- `page` (integer, opcional, padrão: 1): Número da página (≥1)
- `per_page` (integer, opcional, padrão: 20): Itens por página (1-100)

**Response (200)**:
```json
{
  "questions": [
    {
      "id": 123,
      "topic": "React",
      "question": "Como usar hooks no React?",
      "created_at": "2024-01-15T10:30:00Z",
      "classified_topic": "Frontend Development"
    },
    {
      "id": 124,
      "topic": "Node.js",
      "question": "Como configurar middleware no Express?",
      "created_at": "2024-01-15T09:15:00Z",
      "classified_topic": "Backend Development"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20
}
```

**Códigos de Status**:
- `200`: Lista retornada com sucesso
- `401`: Token inválido ou ausente
- `403`: Usuário não é administrador
- `500`: Erro interno do servidor

---

## 3. Estatísticas das Dúvidas
**`GET /anonymous-questions/stats`**

**Autenticação**: 🔒 Admin

**Response (200)**:
```json
[
  {
    "topic": "React",
    "total_questions": 45,
    "percentage": 30.0,
    "last_question_date": "2024-01-15T10:30:00Z"
  },
  {
    "topic": "Node.js",
    "total_questions": 32,
    "percentage": 21.3,
    "last_question_date": "2024-01-14T15:20:00Z"
  },
  {
    "topic": "Python",
    "total_questions": 28,
    "percentage": 18.7,
    "last_question_date": "2024-01-13T12:45:00Z"
  }
]
```

**Códigos de Status**:
- `200`: Estatísticas retornadas com sucesso
- `401`: Token inválido ou ausente
- `403`: Usuário não é administrador
- `500`: Erro interno do servidor

---

## 4. Temas Mais Comuns
**`GET /anonymous-questions/topics`**

**Autenticação**: 🔒 Admin

**Query Parameters**:
- `limit` (integer, opcional, padrão: 10): Número máximo de temas (1-50)

**Response (200)**:
```json
[
  "React",
  "Node.js",
  "Python",
  "JavaScript",
  "Database Design",
  "API Development",
  "DevOps",
  "Testing",
  "Git",
  "CSS"
]
```

**Códigos de Status**:
- `200`: Lista de temas retornada com sucesso
- `401`: Token inválido ou ausente
- `403`: Usuário não é administrador
- `500`: Erro interno do servidor

---

## 5. Tópicos Disponíveis
**`GET /anonymous-questions/available-topics`**

**Autenticação**: ❌ Público

**Response (200)**:
```json
[
  {
    "name": "Frontend Development",
    "description": "React, Vue, Angular, HTML, CSS, JavaScript",
    "keywords": ["react", "vue", "angular", "html", "css", "javascript"]
  },
  {
    "name": "Backend Development",
    "description": "Node.js, Python, Java, APIs, Microservices",
    "keywords": ["nodejs", "python", "java", "api", "microservices"]
  },
  {
    "name": "Database",
    "description": "SQL, NoSQL, PostgreSQL, MongoDB, Redis",
    "keywords": ["sql", "nosql", "postgresql", "mongodb", "redis"]
  },
  {
    "name": "DevOps",
    "description": "Docker, Kubernetes, CI/CD, Cloud Computing",
    "keywords": ["docker", "kubernetes", "cicd", "aws", "cloud"]
  }
]
```

**Códigos de Status**:
- `200`: Lista de tópicos retornada com sucesso
- `500`: Erro interno do servidor

---

## 6. Sugestões de Tópicos
**`GET /anonymous-questions/topic-suggestions`**

**Autenticação**: ❌ Público

**Query Parameters**:
- `text` (string, obrigatório): Texto parcial para buscar sugestões
- `limit` (integer, opcional, padrão: 5): Número máximo de sugestões (1-20)

**Exemplo**: `GET /anonymous-questions/topic-suggestions?text=react&limit=3`

**Response (200)**:
```json
[
  "React Hooks",
  "React Components",
  "React State Management"
]
```

**Códigos de Status**:
- `200`: Sugestões retornadas com sucesso
- `400`: Parâmetro 'text' é obrigatório
- `500`: Erro interno do servidor

---

## 7. Detalhes do Tópico
**`GET /anonymous-questions/topic-details/{topic_name}`**

**Autenticação**: ❌ Público

**Path Parameters**:
- `topic_name` (string): Nome do tópico

**Exemplo**: `GET /anonymous-questions/topic-details/React`

**Response (200)**:
```json
{
  "name": "React",
  "description": "Biblioteca JavaScript para construção de interfaces de usuário",
  "keywords": ["react", "hooks", "components", "jsx", "props", "state"],
  "patterns": ["como usar", "tutorial", "exemplo", "implementar"],
  "total_questions": 45
}
```

**Response (404)**:
```json
{
  "detail": "Tópico 'InvalidTopic' não encontrado"
}
```

**Códigos de Status**:
- `200`: Detalhes retornados com sucesso
- `404`: Tópico não encontrado
- `500`: Erro interno do servidor

---

# 📊 Chat Statistics Endpoints

## 1. Estatísticas Completas do Chat
**`GET /stats`**

**Autenticação**: 🔒 Admin

**Query Parameters**:
- `days` (integer, opcional, padrão: 30): Últimos X dias (1-365)

**Exemplo**: `GET /stats?days=7`

**Response (200)**:
```json
{
  "period": "Últimos 7 dias",
  "timezone": "Horário de Brasília (UTC-3)",
  "totals": {
    "messages": 1250,
    "questions": 890,
    "users": 45,
    "avg_response_time_ms": 1234.56
  },
  "peak_usage": {
    "hour": {
      "hour": 14,
      "period": "Tarde",
      "messages": 125
    },
    "day": {
      "day": "Segunda-feira",
      "messages": 180
    }
  },
  "top_topics": [
    {
      "topic": "React",
      "messages": 234
    },
    {
      "topic": "Node.js",
      "messages": 187
    },
    {
      "topic": "Python",
      "messages": 156
    },
    {
      "topic": "JavaScript",
      "messages": 143
    },
    {
      "topic": "Database",
      "messages": 98
    }
  ]
}
```

**Códigos de Status**:
- `200`: Estatísticas retornadas com sucesso
- `401`: Token inválido ou ausente
- `403`: Usuário não é administrador
- `400`: Parâmetro 'days' inválido (deve ser entre 1-365)
- `500`: Erro interno do servidor

---

## 2. Estatísticas Públicas
**`GET /stats/public`**

**Autenticação**: ❌ Público

**Response (200)**:
```json
{
  "total_messages": 1250,
  "total_questions": 890,
  "most_discussed_topics": [
    "React",
    "Node.js",
    "Python"
  ]
}
```

**Códigos de Status**:
- `200`: Estatísticas públicas retornadas com sucesso
- `500`: Erro interno do servidor

---

# 📋 Estruturas de Dados

## Estrutura de Erro Padrão
```json
{
  "detail": "Descrição do erro"
}
```

## Tipos de Autenticação
- **Header de Autenticação**: `Authorization: Bearer {jwt_token}`
- **Roles**: `ADMIN` (para endpoints administrativos)

## Formatos de Data
- Todas as datas são retornadas no formato ISO 8601: `YYYY-MM-DDTHH:mm:ssZ`
- Timezone padrão: UTC-3 (Horário de Brasília) 