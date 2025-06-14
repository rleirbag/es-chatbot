# Regras de Negócio - Sistema de Perguntas Anônimas

## Visão Geral

O sistema de perguntas anônimas do ES Chatbot permite que usuários submetam dúvidas de forma anônima, facilitando a participação sem constrangimento. Implementa coleta automática de dados durante conversas normais e oferece funcionalidades administrativas para análise e gestão das dúvidas coletadas.

## Regras de Negócio Principais

### 1. Coleta Automática de Dúvidas Durante Chat

**Regra:** Sistema identifica e registra automaticamente perguntas durante conversas normais de chat.

**Detecção Automática:**
- **Integração com Chat:** Toda mensagem de chat é analisada
- **Classificação AI:** Agente de IA determina se é uma pergunta
- **Extração de Tópico:** IA identifica o tema da pergunta
- **Registro Silencioso:** Usuário não percebe a coleta

**Critérios de Identificação:**
- **Estrutura de Pergunta:** Sentenças interrogativas
- **Conteúdo Semântico:** Contexto indica busca por informação
- **Classificação Inteligente:** AI Topic Agent categoriza automaticamente
- **Filtros de Qualidade:** Evita spam e perguntas irrelevantes

**Dados Coletados:**
- **Pergunta:** Texto completo da pergunta
- **Tópico:** Tema identificado pela IA
- **Timestamp:** Momento da pergunta (UTC-3, horário de Brasília)
- **Metadata:** Informações contextuais não identificadoras

**Justificativa:**
- **Usabilidade:** Zero friction para o usuário
- **Coleta Passiva:** Não interrompe fluxo de conversa
- **Análise de Demanda:** Identifica temas mais comuns
- **Melhoria Contínua:** Base para otimização do sistema

### 2. Anonimização Rigorosa de Dados

**Regra:** Sistema garante completa anonimização de perguntas coletadas.

**Estratégias de Anonimização:**
- **Sem Identificação:** Nenhum dado pessoal é armazenado
- **Sem Sessão:** Não há vínculo com usuário ou sessão
- **Sem Timestamp Exato:** Apenas data/hora aproximada
- **Sem Metadata Identificadora:** Exclusão de dados únicos

**Dados NÃO Coletados:**
- **User ID:** Jamais associado a usuário específico
- **Email:** Nenhuma informação pessoal
- **IP Address:** Sem rastreamento de origem
- **Session ID:** Sem vínculo com sessões específicas

**Proteções Implementadas:**
- **Hashing:** Conteúdo pode ser hasheado para deduplicação
- **Agregação:** Dados sempre apresentados de forma agregada
- **Temporal Fuzzing:** Timestamps aproximados para evitar correlação
- **Content Sanitization:** Remoção de possíveis identificadores

**Justificativa:**
- **Privacidade:** Conformidade total com LGPD/GDPR
- **Confiança:** Usuários podem perguntar sem receio
- **Ética:** Respeito aos direitos fundamentais
- **Legal:** Prevenção de problemas jurídicos

### 3. Submissão Manual de Dúvidas

**Regra:** Usuários podem submeter dúvidas manualmente de forma anônima.

**Endpoint `/anonymous-questions` (POST):**
- **Acesso Público:** Não requer autenticação
- **Campos Obrigatórios:** tema e pergunta
- **Validação Mínima:** Apenas estrutura básica
- **Resposta Confirmação:** Sucesso sem dados identificadores

**Schema de Entrada:**
```json
{
  "topic": "Programação",
  "question": "Como funciona recursão em Python?"
}
```

**Validações Aplicadas:**
- **Tema:** String não vazia, tamanho razoável
- **Pergunta:** String não vazia, tamanho máximo
- **Sanitização:** Limpeza de possíveis identificadores
- **Rate Limiting:** Prevenção de spam (se implementado)

**Casos de Uso:**
- **Dúvidas Específicas:** Usuário quer fazer pergunta pontual
- **Temas Sensíveis:** Perguntas que causam constrangimento
- **Sugestões:** Ideias para melhorias do sistema
- **Feedback:** Dúvidas sobre funcionalidades

**Justificativa:**
- **Acessibilidade:** Qualquer pessoa pode participar
- **Flexibilidade:** Não depende de estar em chat
- **Foco:** Usuário pode elaborar melhor a pergunta
- **Inclusão:** Participação sem barreiras

### 4. Controle de Acesso Administrativo

**Regra:** Apenas administradores podem visualizar e analisar dúvidas coletadas.

**Validação de Acesso:**
- **Autenticação Obrigatória:** JWT token válido
- **Role ADMIN:** Verificação rigorosa de permissões
- **Dupla Validação:** Usuário existe + role adequada
- **Audit Trail:** Logs de todos os acessos admin

**Endpoints Protegidos:**
- **GET `/anonymous-questions`:** Lista paginada de dúvidas
- **GET `/anonymous-questions/stats`:** Estatísticas por tema
- **GET `/anonymous-questions/topics`:** Temas mais comuns

**Funcionalidades Admin:**
- **Visualização:** Todas as dúvidas coletadas
- **Filtros:** Por tema, período, etc.
- **Paginação:** Navegação eficiente
- **Estatísticas:** Análise agregada
- **Exportação:** Dados para análise externa (se implementado)

**Justificativa:**
- **Segurança:** Dados sensíveis protegidos
- **Gestão:** Permite análise e melhoria
- **Compliance:** Acesso controlado e auditado
- **Eficiência:** Ferramentas adequadas para análise

### 5. Análise Estatística e Relatórios

**Regra:** Sistema oferece análises estatísticas agregadas para auxiliar na tomada de decisões.

**Métricas Disponíveis:**
- **Contagem por Tema:** Quantas perguntas por categoria
- **Tendências Temporais:** Evolução ao longo do tempo
- **Temas Mais Comuns:** Ranking de popularidade
- **Distribuição:** Padrões de uso

**Endpoint de Estatísticas:**
```json
{
  "topic": "Programação",
  "count": 45,
  "percentage": 32.1,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

**Análise de Temas:**
- **Classificação Automática:** IA categoriza perguntas
- **Agregação:** Contagem e porcentagens
- **Ordenação:** Por frequência ou alfabética
- **Filtros:** Por período, tema, etc.

**Casos de Uso Administrativos:**
- **Planejamento:** Identificar temas para criar conteúdo
- **Priorização:** Focar nos temas mais demandados
- **Métricas:** Acompanhar evolução das dúvidas
- **Insights:** Entender necessidades dos usuários

**Justificativa:**
- **Data-Driven:** Decisões baseadas em dados reais
- **Eficiência:** Foco onde há mais demanda
- **Melhoria Contínua:** Otimização baseada em feedback
- **ROI:** Melhor retorno sobre investimento

### 6. Integração com Sistema de IA

**Regra:** Sistema integra-se com agentes de IA para classificação automática inteligente.

**Topic Agent Integration:**
- **Classificação Automática:** IA identifica tema da pergunta
- **Múltiplas Categorias:** Suporte a diversos temas
- **Aprendizado:** Melhora com uso
- **Fallback:** Categoria "Outros" para casos incertos

**Categorias Suportadas:**
- **Programação:** Códigos, algoritmos, linguagens
- **Banco de Dados:** SQL, NoSQL, modelagem
- **Arquitetura:** Design patterns, estruturas
- **Ferramentas:** IDEs, frameworks, libraries
- **Conceitos:** Teoria, fundamentos
- **Outros:** Temas não categorizados

**Processamento Inteligente:**
- **Análise Semântica:** Entende contexto da pergunta
- **Extração de Entidades:** Identifica conceitos-chave
- **Classificação Confiável:** Score de confiança
- **Refinamento:** Melhoria contínua da classificação

**Justificativa:**
- **Automação:** Reduz trabalho manual
- **Precisão:** IA mais precisa que regras fixas
- **Escalabilidade:** Processa grandes volumes
- **Melhoria:** Aprende e evolui com uso

### 7. Tratamento de Spam e Qualidade

**Regra:** Sistema implementa medidas para garantir qualidade das dúvidas coletadas.

**Filtros de Qualidade:**
- **Tamanho Mínimo:** Perguntas muito curtas filtradas
- **Tamanho Máximo:** Limit de caracteres para evitar spam
- **Conteúdo Duplicado:** Deduplicação baseada em hash
- **Padrões Spam:** Detecção de conteúdo repetitivo

**Validações Aplicadas:**
- **Texto Válido:** Caracteres permitidos
- **Idioma:** Principalmente português
- **Estrutura:** Formato de pergunta reconhecível
- **Contexto:** Relevante para domínio do sistema

**Medidas Anti-Spam:**
- **Rate Limiting:** Limite de submissões por tempo
- **IP Throttling:** Controle por origem (se implementado)
- **Pattern Detection:** Identificação de padrões suspeitos
- **Human Review:** Revisão manual quando necessário

**Justificativa:**
- **Qualidade:** Dados úteis para análise
- **Eficiência:** Evita processamento desnecessário
- **Experiência:** Melhores insights para admins
- **Recursos:** Otimização de armazenamento

### 8. Conformidade e Privacidade

**Regra:** Sistema atende rigorosamente aos requisitos de privacidade e proteção de dados.

**Princípios LGPD/GDPR:**
- **Minimização:** Coleta apenas dados necessários
- **Finalidade:** Uso restrito aos propósitos declarados
- **Transparência:** Usuários informados sobre coleta
- **Anonimização:** Dados verdadeiramente anônimos

**Implementação Técnica:**
- **Sem PII:** Nenhuma informação pessoal identificável
- **Encryption:** Dados protegidos em trânsito e repouso
- **Access Control:** Acesso restrito a administradores
- **Audit Logs:** Rastreamento de todos os acessos

**Direitos dos Usuários:**
- **Opt-out:** Possibilidade de desativar coleta (se implementado)
- **Transparência:** Informação sobre como dados são usados
- **Anonimização:** Garantia de que dados não são rastreáveis
- **Finalidade:** Uso exclusivo para melhoria do sistema

**Justificativa:**
- **Legal:** Conformidade com regulamentações
- **Ética:** Respeito aos direitos fundamentais
- **Confiança:** Usuários podem usar sem receio
- **Reputação:** Demonstra compromisso com privacidade

## Fluxos de Negócio

### Fluxo de Coleta Automática

1. **Mensagem de Chat Recebida**
   - Usuário envia mensagem no chat
   - Sistema processa mensagem normalmente

2. **Análise Paralela**
   - Topic Agent analisa se é pergunta
   - Extrai tema da pergunta
   - Classifica tipo de conteúdo

3. **Decisão de Coleta**
   - Se for pergunta: procede com coleta
   - Se não for: ignora para este fim

4. **Anonimização e Armazenamento**
   - Remove identificadores
   - Armazena pergunta anonimizada
   - Registra tema e timestamp

### Fluxo de Submissão Manual

1. **Recebimento da Requisição**
   - POST `/anonymous-questions`
   - Dados: topic e question

2. **Validação de Entrada**
   - Verifica formato dos dados
   - Valida tamanho e conteúdo
   - Sanitiza entrada

3. **Processamento**
   - Análise adicional se necessário
   - Verificação de duplicatas
   - Aplicação de filtros

4. **Armazenamento Anônimo**
   - Persiste pergunta sem identificadores
   - Registra timestamp aproximado
   - Confirma recebimento

### Fluxo de Consulta Administrativa

1. **Autenticação e Autorização**
   - Valida token JWT
   - Verifica role ADMIN
   - Registra acesso em audit log

2. **Processamento da Consulta**
   - Aplica filtros solicitados
   - Implementa paginação
   - Ordena resultados

3. **Agregação de Dados**
   - Calcula estatísticas
   - Prepara métricas
   - Formata resposta

4. **Retorno Seguro**
   - Dados agregados apenas
   - Sem informações identificadoras
   - Resposta formatada

## Estruturas de Dados

### Modelo de Banco (AnonymousQuestion)
```sql
CREATE TABLE anonymous_questions (
    id INTEGER PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    -- Sem campos identificadores
);
```

### Schema de Entrada (AnonymousQuestionCreate)
```json
{
  "topic": "Programação",
  "question": "Como implementar algoritmo de ordenação eficiente?"
}
```

### Schema de Resposta (AnonymousQuestionResponse)
```json
{
  "id": 123,
  "topic": "Programação",
  "question": "Como implementar algoritmo de ordenação eficiente?",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Schema de Estatísticas (AnonymousQuestionStats)
```json
{
  "topic": "Programação",
  "count": 45,
  "percentage": 32.1,
  "last_question_date": "2024-01-15T10:30:00Z"
}
```

## Limitações e Considerações

### Limitações Atuais
- **Classificação Simples:** Apenas um tema por pergunta
- **Sem Detalhamento:** Não há sub-categorias
- **Processamento Básico:** Sem análise semântica avançada
- **Sem Feedback:** Não há confirmação da classificação

### Escalabilidade
- **Volume:** Suporta milhares de perguntas
- **Performance:** Consultas otimizadas para admin
- **Storage:** Dados compactos, sem redundância
- **Processing:** Análise assíncrona quando possível

### Privacidade
- **Anonimização:** Verdadeiramente anônimo
- **Sem Correlação:** Impossível rastrear usuários
- **Agregação:** Dados sempre agregados
- **Minimização:** Coleta apenas o necessário

### Monitoramento
- **Usage Metrics:** Quantas perguntas por período
- **Quality Metrics:** Taxa de spam detectado
- **Admin Activity:** Logs de acesso administrativo
- **Performance:** Tempo de processamento

### Extensibilidade
- **Novos Temas:** Fácil adição de categorias
- **Análise Avançada:** Suporte a ML mais sofisticado
- **Integração:** APIs para sistemas externos
- **Exportação:** Capacidade de exportar dados 