# Regras de Negócio - Sistema de Chat Integrado

## Visão Geral

O sistema de chat do ES Chatbot é o núcleo da aplicação, integrando múltiplos sistemas para criar uma experiência conversacional completa. Combina RAG (Retrieval-Augmented Generation), múltiplos LLMs, persistência de histórico, detecção de dúvidas anônimas e análise estatística em um fluxo unificado de streaming em tempo real.

## Regras de Negócio Principais

### 1. Arquitetura de Integração Complexa

**Regra:** O chat integra 6 sistemas distintos em um fluxo único e coordenado.

**Sistemas Integrados:**
- **RAG Service:** Busca de contexto em documentos
- **LLM Service:** Geração de resposta com IA
- **Chat History:** Persistência de conversas
- **Anonymous Questions:** Detecção automática de dúvidas
- **Statistics Service:** Coleta de métricas em tempo real
- **User Management:** Controle de acesso e identificação

**Coordenação:**
- Processamento paralelo onde possível
- Falhas isoladas não comprometem fluxo principal
- Limpeza automática de recursos compartilhados
- Streaming unificado para experiência fluida

**Justificativa:**
- **Funcionalidade Rica:** Múltiplas funcionalidades em uma única interação
- **Eficiência:** Operações paralelas onde possível
- **Robustez:** Falhas isoladas não quebram o sistema
- **Observabilidade:** Métricas automáticas de todas as interações

### 2. Gestão Inteligente de Histórico de Conversas

**Regra:** O sistema gerencia automaticamente a persistência e continuidade de conversas.

**Comportamento de Histórico:**

**Caso 1 - Nova Conversa:**
- `chat_history_id` é `null` na requisição
- Sistema cria novo histórico automaticamente
- Estrutura: `{'messages': []}`
- Associa ao usuário autenticado

**Caso 2 - Continuação de Conversa:**
- `chat_history_id` é fornecido na requisição
- Sistema valida propriedade do histórico
- Carrega mensagens existentes para contexto
- Erro 403 se usuário não é proprietário

**Persistência:**
- Atualização em nova sessão DB para evitar concorrência
- Tanto pergunta quanto resposta são salvos
- Formato: `[{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]`

**Justificativa:**
- **Experiência Contínua:** Usuário mantém contexto entre sessões
- **Segurança:** Isolamento de conversas por usuário
- **Concorrência:** Evita conflitos em operações simultâneas
- **Rastreabilidade:** Histórico completo para auditoria

### 3. Sistema RAG Condicional com Comando Especial

**Regra:** A busca RAG é aplicada condicionalmente baseada no tipo de mensagem.

**Lógica de Decisão:**
- **Mensagens normais:** Passam por busca RAG automaticamente
- **Comando `/desafio`:** Bypassa RAG completamente
- **RAG encontra contexto:** Monta prompt enriquecido
- **RAG não encontra:** Usa prompt original

**Processamento RAG:**
1. **Busca semântica:** 4 documentos mais relevantes por padrão
2. **Extração de conteúdo:** Concatena textos encontrados
3. **Coleta de fontes:** Links únicos do Google Drive
4. **Limpeza:** Cache ChromaDB sempre limpo ao final

**Formatação de Prompt:**
```
Baseado no seguinte contexto, responda a pergunta.

Contexto:
{documentos_encontrados}

Pergunta: {pergunta_usuario}
```

**Justificativa:**
- **Relevância:** Respostas baseadas em documentos específicos
- **Transparência:** Fontes são sempre exibidas
- **Performance:** Busca apenas quando necessário
- **Flexibilidade:** Comandos especiais para casos específicos

### 4. Comando `/desafio` para Geração de Exercícios

**Regra:** O comando `/desafio` ativa modo especial de geração de exercícios.

**Comportamento:**
- **Formato:** `/desafio [tópico]` ou `/desafio` (sem tópico)
- **Com tópico:** `"Crie um desafio sobre o seguinte tópico: {tópico}"`
- **Sem tópico:** `"Crie um desafio com base no contexto da nossa conversa até agora."`
- **Sem RAG:** Não busca documentos para este tipo de interação
- **Sem fontes:** Não exibe seção de fontes consultadas

**Casos de Uso:**
- Professores criando exercícios
- Estudantes praticando conceitos
- Geração de atividades educacionais

**Justificativa:**
- **Funcionalidade Específica:** Necessidade educacional comum
- **Contexto Diferente:** Criação vs. resposta baseada em documentos
- **Eficiência:** Economiza processamento RAG desnecessário

### 5. Detecção Automática de Dúvidas Anônimas

**Regra:** O sistema detecta e salva automaticamente dúvidas para análise posterior.

**Processo de Detecção:**
1. **Análise de indicadores:** Palavras-chave que sugerem dúvidas
2. **Classificação de tópico:** IA especializada categoriza o tema
3. **Salvamento silencioso:** Não afeta fluxo principal do chat
4. **Falha graceful:** Erros não comprometem resposta ao usuário

**Indicadores de Dúvida:**
- Termina com `?`
- Palavras-chave: "como", "o que", "por que", "dúvida", "não entendo"
- Padrões: "pode explicar", "me ajuda", "preciso de ajuda"

**Tópicos Classificados:**
- Frontend Development, Backend Development
- Database Management, DevOps
- Software Architecture, Testing
- Machine Learning, Mobile Development

**Justificativa:**
- **Inteligência de Negócio:** Identifica tendências de dúvidas
- **Melhoria Contínua:** Base para criação de novos conteúdos
- **Análise Educacional:** Entender dificuldades dos usuários
- **Anonimização:** Preserva privacidade dos usuários

### 6. Coleta de Estatísticas em Tempo Real

**Regra:** Cada interação gera automaticamente métricas detalhadas.

**Métricas Coletadas:**
- **Temporal:** Tempo de resposta em millisegundos
- **Conteúdo:** Tamanho da mensagem, tipo, tópico
- **RAG:** Se contexto foi encontrado nos documentos
- **LLM:** Qual provedor foi utilizado
- **Usuário:** Hash do email para privacidade
- **Temporal:** Hora do dia e dia da semana (fuso BR)

**Classificações Automáticas:**
- **Tipo de mensagem:** question, statement, command
- **É pergunta:** Detectado por IA
- **Tópico:** Classificado por agente especializado

**Privacidade:**
- **Hashing:** Email e mensagem são hasheados
- **Anonimização:** Dados pessoais não são armazenados
- **Agregação:** Análises são sempre agregadas

**Justificativa:**
- **Monitoramento:** Performance do sistema em tempo real
- **Analytics:** Padrões de uso e comportamento
- **Otimização:** Base para melhorias de performance
- **Compliance:** Coleta anonimizada preserva privacidade

### 7. Streaming com Fontes Integradas

**Regra:** Respostas são transmitidas em tempo real com fontes ao final.

**Fluxo de Streaming:**
1. **Stream LLM:** Tokens do modelo transmitidos imediatamente
2. **Acumulação:** Resposta completa mantida em memória
3. **Fontes dinâmicas:** Seção de fontes adicionada character-by-character
4. **Persistência:** Resposta completa (com fontes) salva no histórico

**Formato de Fontes:**
```markdown
**Fontes consultadas:**
- [Nome do documento](link_google_drive)
- [Outro documento](link_google_drive)
```

**Comportamento:**
- **Com RAG:** Sempre mostra fontes se documentos foram encontrados
- **Comando `/desafio`:** Nunca mostra fontes
- **Links únicos:** Deduplicação automática de documentos repetidos

**Justificativa:**
- **Transparência:** Usuário sabe origem das informações
- **Credibilidade:** Links para documentos oficiais
- **Experiência:** Resposta imediata + fontes contextuais
- **Rastreabilidade:** Permite verificação das informações

### 8. Gestão de Sessões e Concorrência

**Regra:** Sistema gerencia múltiplas sessões de banco para evitar conflitos.

**Estratégia de Sessões:**
- **Sessão principal:** Para leitura de dados iniciais
- **Nova sessão:** Para persistência ao final do stream
- **Isolamento:** Evita locks durante streaming longo
- **Cleanup:** Sessões sempre fechadas adequadamente

**Prevenção de Concorrência:**
- **Histórico:** Atualização em transação separada
- **Estatísticas:** Falhas não afetam chat principal
- **Dúvidas anônimas:** Processamento isolado

**Justificativa:**
- **Robustez:** Streaming longo não bloqueia operações
- **Performance:** Operações paralelas onde seguro
- **Consistência:** Transações isoladas para cada funcionalidade

## Fluxos de Negócio Complexos

### Fluxo Principal de Chat (Mensagem Normal)

1. **Autenticação e Validação**
   - Valida token do usuário
   - Verifica existência no banco de dados
   - Inicia cronômetro para métricas

2. **Gestão de Histórico**
   - Se `chat_history_id` fornecido: carrega e valida propriedade
   - Se não fornecido: cria novo histórico automaticamente
   - Monta contexto de mensagens anteriores

3. **Detecção de Dúvida Anônima** (Paralelo)
   - Analisa mensagem para indicadores de dúvida
   - Classifica tópico com IA especializada
   - Salva silenciosamente (falhas não afetam chat)

4. **Processamento RAG**
   - Busca semântica no ChromaDB
   - Extrai conteúdo relevante dos documentos
   - Coleta links únicos das fontes
   - Limpa cache para garantir dados atuais

5. **Preparação do Prompt**
   - Monta prompt enriquecido com contexto RAG
   - Adiciona histórico de conversação
   - Formata para o LLM selecionado

6. **Geração e Streaming**
   - Executa LLM via Strategy Pattern
   - Transmite tokens em tempo real
   - Adiciona seção de fontes ao final
   - Acumula resposta completa

7. **Persistência Final** (Nova Sessão)
   - Salva pergunta e resposta no histórico
   - Registra estatísticas da interação
   - Confirma transações e fecha conexões

### Fluxo Especial - Comando `/desafio`

1. **Detecção de Comando**
   - Identifica padrão `/desafio [tópico]`
   - Extrai tópico opcional após comando

2. **Bypass RAG**
   - Pula completamente busca de documentos
   - Não coleta fontes ou links

3. **Prompt Especializado**
   - Com tópico: "Crie um desafio sobre: {tópico}"
   - Sem tópico: "Crie um desafio com base no contexto da conversa"

4. **Geração Limpa**
   - Streaming normal do LLM
   - Sem seção de fontes ao final
   - Foco na criatividade educacional

### Fluxo de Recuperação de Erro

1. **Isolamento de Falhas**
   - Dúvidas anônimas: falha silenciosa
   - Estatísticas: falha registrada mas não bloqueia
   - RAG: fallback para prompt original

2. **Cleanup Garantido**
   - Cache ChromaDB sempre limpo
   - Sessões de banco sempre fechadas
   - Recursos liberados mesmo com erro

3. **Experiência do Usuário**
   - Chat continua funcionando
   - Usuário recebe resposta mesmo com falhas parciais
   - Logs detalhados para debugging

## Integrações Críticas

### ChromaDB (RAG)
- **Busca:** Embeddings semânticos
- **Metadados:** Links e informações dos documentos
- **Cache:** Limpeza obrigatória pós-uso

### LLM Service
- **Strategy:** Seleção dinâmica de provedor
- **Streaming:** SSE para tempo real
- **Context:** Histórico + RAG + System Prompt

### Base de Dados
- **Chat History:** JSON estruturado de mensagens
- **Statistics:** Métricas detalhadas anonimizadas
- **Anonymous Questions:** Dúvidas categorizadas
- **Users:** Identificação e controle de acesso

## Configurações e Limitações

### Performance
- **RAG Search:** Limitado a 4 documentos mais relevantes
- **Histórico:** Sem limite de mensagens por conversa
- **Streaming:** Sem timeout configurado
- **Concorrência:** Sem limite de usuários simultâneos

### Segurança
- **Autenticação:** Obrigatória para todas as operações
- **Isolamento:** Históricos isolados por usuário
- **Anonimização:** Dados sensíveis hasheados
- **Validação:** Propriedade de histórico sempre verificada

### Monitoramento
- **Métricas automáticas:** Todas as interações
- **Logs estruturados:** Para debugging e auditoria
- **Detecção de padrões:** Dúvidas e tópicos frequentes
- **Performance tracking:** Tempos de resposta detalhados

### Extensibilidade
- **Novos comandos:** Padrão estabelecido com `/desafio`
- **Novos LLMs:** Via Strategy Pattern
- **Novas métricas:** Schema extensível
- **Novos tópicos:** IA classificadora treinável 