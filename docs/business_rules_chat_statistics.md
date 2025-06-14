# Regras de Negócio - Sistema de Estatísticas de Chat

## Visão Geral

O sistema de estatísticas de chat do ES Chatbot coleta, processa e apresenta métricas detalhadas sobre o uso do sistema de conversação. Implementa coleta automática de dados anonimizados durante conversas, oferecendo insights valiosos para administradores sobre padrões de uso, performance e demandas dos usuários.

## Regras de Negócio Principais

### 1. Coleta Automática e Transparente

**Regra:** Sistema coleta automaticamente métricas de todas as interações de chat sem impactar a experiência do usuário.

**Integração Transparente:**
- **Coleta Silenciosa:** Usuário não percebe a coleta de dados
- **Performance Não Impactada:** Processamento assíncrono
- **Zero Friction:** Não interfere no fluxo de conversa
- **Continuidade:** Coleta funciona mesmo com falhas parciais

**Dados Coletados Automaticamente:**
- **Tamanho da Mensagem:** Contagem de caracteres
- **Tipo de Mensagem:** question, statement, command
- **Tópico Detectado:** Classificação automática via IA
- **Tempo de Resposta:** Duração do processamento em ms
- **Contexto RAG:** Se foi encontrado contexto relevante
- **Provedor LLM:** Qual modelo foi utilizado

**Momento da Coleta:**
- **Início:** Medição do tempo quando mensagem é recebida
- **Processamento:** Análise durante o processamento
- **Finalização:** Registro final quando resposta é enviada
- **Assíncrono:** Não bloqueia resposta ao usuário

**Justificativa:**
- **Melhoria Contínua:** Dados para otimização do sistema
- **Análise de Performance:** Identificação de gargalos
- **Insights de Uso:** Compreensão de padrões de usuário
- **Data-Driven:** Decisões baseadas em evidências

### 2. Anonimização e Proteção de Privacidade

**Regra:** Sistema implementa anonimização rigorosa para proteger privacidade dos usuários.

**Estratégias de Anonimização:**
- **Hash de Email:** SHA256 de 16 caracteres
- **Hash de Mensagem:** SHA256 de 16 caracteres  
- **User ID Opcional:** Referência pode ser null
- **Sem Conteúdo:** Apenas hash, nunca texto original

**Dados Anonimizados:**
```json
{
  "user_email_hash": "a1b2c3d4e5f6...",  // 16 chars
  "message_hash": "f6e5d4c3b2a1...",     // 16 chars
  "message_length": 150,
  "detected_topic": "Programação",
  "message_type": "question"
}
```

**Dados NUNCA Coletados:**
- **Conteúdo Real:** Texto das mensagens
- **Email Completo:** Apenas hash irrecuperável
- **Dados Pessoais:** Nome, telefone, endereço
- **Identificadores Únicos:** IPs, cookies, fingerprints

**Proteções Implementadas:**
- **Hashing Unidirecional:** SHA256 sem possibilidade de reversão
- **Truncamento:** Apenas primeiros 16 caracteres do hash
- **Separação:** Hashes não permitem correlação
- **Agregação:** Dados apresentados sempre agregados

**Justificativa:**
- **LGPD/GDPR:** Conformidade total com regulamentações
- **Confiança:** Usuários podem usar sem receio
- **Ética:** Coleta responsável de dados
- **Segurança:** Proteção contra vazamentos

### 3. Classificação Inteligente de Mensagens

**Regra:** Sistema classifica automaticamente mensagens usando IA para análise semântica.

**Tipos de Classificação:**

**Por Tipo de Mensagem:**
- **question:** Perguntas diretas ou indiretas
- **statement:** Afirmações ou comentários
- **command:** Comandos específicos (ex: /desafio)

**Por Tópico (AI Topic Agent):**
- **Programação:** Código, algoritmos, linguagens
- **Banco de Dados:** SQL, NoSQL, modelagem
- **Arquitetura:** Patterns, estruturas, design
- **Ferramentas:** IDEs, frameworks, libs
- **Conceitos:** Teoria, fundamentos
- **Outros:** Não classificado

**Processo de Classificação:**
1. **Análise Semântica:** IA analisa contexto da mensagem
2. **Extração de Entidades:** Identifica conceitos-chave
3. **Classificação Multi-Critério:** Tipo + tópico
4. **Score de Confiança:** Avalia certeza da classificação

**Detecção de Perguntas:**
- **Estrutura Interrogativa:** Sentenças com "?", "como", "quando"
- **Contexto Semântico:** Busca por informação
- **Padrões Linguísticos:** Expressões típicas de dúvidas
- **Machine Learning:** Modelo treinado para português

**Justificativa:**
- **Precisão:** IA mais precisa que regras fixas
- **Escalabilidade:** Processa grandes volumes
- **Insights:** Compreensão semântica do uso
- **Automação:** Reduz trabalho manual

### 4. Métricas Temporais e Geolocalização

**Regra:** Sistema registra informações temporais precisas no fuso horário brasileiro.

**Timestamp Brasileiro (UTC-3):**
- **Horário de Brasília:** Todos os timestamps em UTC-3
- **Hora do Dia:** 0-23 (campo separado)
- **Dia da Semana:** 0-6 (0=domingo, campo separado)
- **Timezone Fixo:** Sempre UTC-3, independente do usuário

**Dados Temporais Coletados:**
```python
created_at = datetime.now(timezone(timedelta(hours=-3)))
hour_of_day = created_at.hour  # 0-23
day_of_week = created_at.weekday()  # 0-6
```

**Utilização dos Dados Temporais:**
- **Análise de Picos:** Horários de maior uso
- **Padrões Semanais:** Diferenças entre dias da semana
- **Planejamento:** Quando fazer manutenções
- **Recursos:** Dimensionamento de infraestrutura

**Justificativa:**
- **Localização:** Sistema brasileiro, fuso brasileiro
- **Análise:** Padrões temporais são cruciais
- **Operações:** Planejamento de manutenções
- **UX:** Entender quando usuários mais precisam

### 5. Métricas de Performance e Qualidade

**Regra:** Sistema monitora continuamente performance e qualidade das respostas.

**Métricas de Performance:**
- **Tempo de Resposta:** Milissegundos do início ao fim
- **RAG Context Found:** Se contexto relevante foi encontrado
- **LLM Provider:** Qual modelo foi utilizado
- **Success Rate:** Taxa de sucesso implícita

**Cálculo de Tempo de Resposta:**
```python
start_time = time.time()
# ... processamento da mensagem ...
response_time_ms = (time.time() - start_time) * 1000
```

**Métricas de Qualidade:**
- **Contexto RAG:** % de mensagens com contexto encontrado
- **Classificação Precisa:** Confiança na classificação de tópicos
- **Tipos de Pergunta:** Diversidade de questões
- **Engagement:** Comprimento médio das conversas

**Benchmarks e SLAs:**
- **Tempo Alvo:** < 5 segundos para resposta
- **RAG Hit Rate:** > 70% deve encontrar contexto
- **Uptime:** > 99% de disponibilidade
- **Error Rate:** < 1% de falhas

**Justificativa:**
- **Otimização:** Identificar gargalos de performance
- **Qualidade:** Monitorar efetividade do RAG
- **SLA:** Garantir qualidade de serviço
- **Alertas:** Detecção proativa de problemas

### 6. Controle de Acesso Administrativo

**Regra:** Apenas administradores podem acessar estatísticas detalhadas do sistema.

**Validação Rigorosa:**
```python
def _verify_admin_access(current_user: dict, db: Session):
    user_email = current_user.get('email')
    if not user_email:
        raise HTTPException(401, 'Credentials required')
    
    user = GetUserByEmailUseCase.execute(db, email=user_email)
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(403, 'Admin access required')
    return user
```

**Endpoints Administrativos:**
- **GET `/chat-statistics/overview`:** Visão geral do sistema
- **GET `/chat-statistics/topics`:** Análise por tópicos
- **GET `/chat-statistics/performance`:** Métricas de performance
- **GET `/chat-statistics/usage`:** Padrões de uso

**Funcionalidades Admin:**
- **Dashboards:** Visualizações gráficas
- **Filtros Avançados:** Por período, tópico, tipo
- **Exportação:** Dados para análise externa
- **Alertas:** Notificações de anomalias

**Segurança Implementada:**
- **Autenticação Dupla:** Token + role verification
- **Audit Trail:** Log de todos os acessos admin
- **Rate Limiting:** Proteção contra abuso
- **Data Masking:** Dados sensíveis sempre mascarados

**Justificativa:**
- **Confidencialidade:** Dados operacionais são sensíveis
- **Compliance:** Acesso controlado e auditado
- **Gestão:** Ferramentas para tomada de decisão
- **Segurança:** Proteção multicamada

### 7. Análises Estatísticas Avançadas

**Regra:** Sistema oferece análises estatísticas sofisticadas para insights estratégicos.

**Análises Disponíveis:**

**Por Tópicos:**
- **Ranking:** Temas mais populares
- **Tendências:** Evolução ao longo do tempo
- **Sazonalidade:** Padrões cíclicos
- **Correlações:** Relacionamentos entre temas

**Por Tempo:**
- **Picos de Uso:** Horários de maior atividade
- **Padrões Semanais:** Segunda vs. domingo
- **Crescimento:** Taxa de crescimento de uso
- **Previsões:** Estimativas de demanda futura

**Por Performance:**
- **Latência:** Distribuição de tempos de resposta
- **Efetividade RAG:** Taxa de contexto encontrado
- **Provider Comparison:** Performance entre LLMs
- **Error Analysis:** Análise de falhas

**Visualizações Oferecidas:**
- **Time Series:** Gráficos temporais
- **Histogramas:** Distribuições
- **Heat Maps:** Padrões bidimensionais
- **Comparativos:** Before/after, A/B tests

**Justificativa:**
- **Strategic Insights:** Compreensão profunda do negócio
- **Optimization:** Identificação de oportunidades
- **Planning:** Base para decisões futuras
- **ROI:** Demonstração de valor do sistema

### 8. Integração com Sistemas de Monitoramento

**Regra:** Estatísticas integram-se com ferramentas de monitoramento e alertas.

**Métricas para Alertas:**
- **Response Time:** Alertas se > threshold
- **Error Rate:** Alertas se > 1%
- **RAG Miss Rate:** Alertas se < 70% hit rate
- **Usage Spikes:** Alertas para picos anômalos

**Integrações Possíveis:**
- **Prometheus:** Exposição de métricas
- **Grafana:** Dashboards avançados
- **Slack/Teams:** Notificações automáticas
- **Email:** Relatórios periódicos

**Health Checks:**
- **System Health:** Status geral do sistema
- **Component Health:** Status de cada componente
- **Data Quality:** Validação de dados coletados
- **Performance Trends:** Degradação ao longo do tempo

**Justificativa:**
- **Proatividade:** Detecção precoce de problemas
- **Operacional:** Facilitação da gestão
- **Disponibilidade:** Maximização do uptime
- **Qualidade:** Manutenção de padrões

## Fluxos de Negócio

### Fluxo de Coleta de Estatísticas

1. **Início da Mensagem**
   - Sistema recebe mensagem de chat
   - Inicia medição de tempo
   - Extrai user_id e email

2. **Processamento da Mensagem**
   - Análise semântica via Topic Agent
   - Classificação de tipo de mensagem
   - Processamento RAG e LLM
   - Geração de hashes anonimizados

3. **Cálculo de Métricas**
   - Calcula tempo de resposta
   - Determina se RAG encontrou contexto
   - Identifica provider LLM utilizado
   - Calcula informações temporais

4. **Persistência Anônima**
   - Cria registro em chat_statistics
   - Todos os dados anonimizados
   - Commit assíncrono para não impactar performance

### Fluxo de Consulta Administrativa

1. **Autenticação e Autorização**
   - Validação de token JWT
   - Verificação de role ADMIN
   - Log de acesso administrativo

2. **Processamento da Consulta**
   - Aplicação de filtros (tempo, tópico, etc.)
   - Agregação de dados conforme solicitado
   - Cálculos estatísticos necessários

3. **Preparação da Resposta**
   - Formatação dos dados
   - Aplicação de mascaramento adicional
   - Estruturação conforme schema

4. **Retorno de Insights**
   - Dados sempre agregados
   - Sem possibilidade de identificação
   - Métricas úteis para gestão

### Fluxo de Geração de Alertas

1. **Monitoramento Contínuo**
   - Sistema monitora métricas em tempo real
   - Compara com thresholds definidos
   - Identifica anomalias ou degradações

2. **Avaliação de Severidade**
   - Classifica tipo e urgência do alerta
   - Determina stakeholders a notificar
   - Prepara contexto relevante

3. **Disparo de Notificações**
   - Envia alertas via canais configurados
   - Inclui dados contextuais
   - Sugere ações recomendadas

4. **Tracking de Resolução**
   - Monitora se problema foi resolvido
   - Atualiza status do alerta
   - Gera relatórios de incidentes

## Estruturas de Dados

### Modelo de Banco (ChatStatistics)
```sql
CREATE TABLE chat_statistics (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NULL,
    user_email_hash VARCHAR(16) NULL,
    message_length INTEGER NOT NULL,
    message_hash VARCHAR(16) NULL,
    detected_topic VARCHAR(255) NULL,
    is_question BOOLEAN DEFAULT FALSE,
    message_type VARCHAR(50) NOT NULL,
    response_time_ms FLOAT NULL,
    rag_context_found BOOLEAN DEFAULT FALSE,
    llm_provider VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    hour_of_day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL
);
```

### Schema de Criação (ChatStatisticsCreate)
```json
{
  "user_id": 123456789,
  "user_email_hash": "a1b2c3d4e5f6g7h8",
  "message_length": 150,
  "message_hash": "f6e5d4c3b2a1h8g7",
  "detected_topic": "Programação",
  "is_question": true,
  "message_type": "question",
  "response_time_ms": 2500.5,
  "rag_context_found": true,
  "llm_provider": "claude",
  "hour_of_day": 14,
  "day_of_week": 2
}
```

### Schema de Resposta Agregada
```json
{
  "period": "2024-01-15",
  "total_messages": 1250,
  "questions_percentage": 65.2,
  "avg_response_time_ms": 2100.3,
  "rag_hit_rate": 78.5,
  "top_topics": [
    {"topic": "Programação", "count": 450, "percentage": 36.0},
    {"topic": "Banco de Dados", "count": 300, "percentage": 24.0}
  ],
  "hourly_distribution": {
    "14": 120,
    "15": 135,
    "16": 98
  }
}
```

## Limitações e Considerações

### Limitações Atuais
- **Timezone Fixo:** Apenas UTC-3 (horário de Brasília)
- **Classificação Única:** Um tópico por mensagem
- **Hashing Simples:** SHA256 básico sem salt
- **Sem ML Avançado:** Análises estatísticas básicas

### Escalabilidade
- **Volume:** Suporte a milhões de registros
- **Performance:** Queries otimizadas com índices
- **Storage:** Dados compactos, apenas essencial
- **Partitioning:** Possibilidade de particionamento por data

### Privacidade e Segurança
- **Anonimização:** Verdadeiramente irreversível
- **Agregação:** Sempre apresentação agregada
- **Access Control:** Rigoroso controle admin
- **Audit Trail:** Logs completos de acesso

### Monitoramento e Alertas
- **Real-time:** Métricas em tempo real
- **Thresholds:** Limites configuráveis
- **Notification:** Múltiplos canais de alerta
- **Recovery:** Tracking de resolução

### Extensibilidade
- **Novas Métricas:** Facilidade para adicionar campos
- **Integrações:** APIs para sistemas externos
- **ML Avançado:** Suporte a análises preditivas
- **Visualizações:** Dashboards customizáveis 