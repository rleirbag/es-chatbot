# ES Chatbot - Documentação de Regras de Negócio

## Visão Geral

Este diretório contém a documentação completa das regras de negócio do ES Chatbot, uma aplicação de conversação inteligente que integra múltiplos sistemas para oferecer respostas contextualizadas usando RAG (Retrieval-Augmented Generation) e LLMs.

## Sistemas Documentados

### 1. [Sistema de Autenticação](./business_rules_auth.md)
**Responsabilidade:** Controle de acesso e autenticação via Google OAuth2

**Regras Principais:**
- **Google OAuth2 Exclusivo:** Única forma de autenticação
- **Scopos Obrigatórios:** Drive access + profile information
- **ID Numérico Único:** Últimos 9 dígitos do Google ID
- **Upsert Inteligente:** Cria, atualiza ou mantém usuário conforme contexto
- **Refresh Token Obrigatório:** Necessário para operações com Google Drive
- **Credenciais Base64:** Encoding seguro para frontend

**Impacto:** Base de segurança para todos os outros sistemas.

---

### 2. [Sistema de Documentos](./business_rules_documents.md)
**Responsabilidade:** Gerenciamento de documentos com integração tripla

**Arquitetura:**
- **Google Drive:** Armazenamento físico dos arquivos
- **ChromaDB:** Embeddings para busca semântica
- **PostgreSQL:** Metadados e controle de acesso

**Regras Principais:**
- **Nome Único:** Validação de duplicatas antes do upload
- **Upload Complexo:** 7 etapas desde autenticação até limpeza
- **RAG Obrigatório:** Processamento automático para busca
- **Associação de Usuário:** Documentos sempre vinculados ao proprietário
- **Cleanup Automático:** Limpeza de recursos temporários
- **Três Sistemas Independentes:** Cada um mantém próprios dados

**Impacto:** Fornece contexto para respostas inteligentes do chat.

---

### 3. [Sistema LLM](./business_rules_llm.md)
**Responsabilidade:** Processamento de linguagem natural com múltiplos provedores

**Estratégia Pattern:**
- **Anthropic Claude:** Modelo comercial em nuvem
- **Ollama:** Modelos open-source auto-hospedados

**Regras Principais:**
- **Seleção Dinâmica:** Provider configurável via LLM_PROVIDER
- **Streaming Obrigatório:** Todas as respostas via Server-Sent Events
- **Sistema Prompts:** Configuração centralizada de comportamento
- **Singleton Service:** Instância única para consistência
- **Timeout Configurável:** Limites de tempo por provider
- **Token Limits:** Controle de uso (1000 tokens para Claude)

**Impacto:** Coração da inteligência conversacional do sistema.

---

### 4. [Sistema de Chat](./business_rules_chat.md) - **MAIS COMPLEXO**
**Responsabilidade:** Orquestração de conversas inteligentes

**Integração de 6 Subsistemas:**
- RAG Service (contexto de documentos)
- LLM Service (geração de respostas)
- Chat History (persistência)
- Anonymous Questions (coleta de dúvidas)
- Statistics Service (métricas)
- User Management (controle de acesso)

**Regras Principais:**
- **Histórico Inteligente:** Auto-criação vs. continuação com validação
- **RAG Condicional:** Mensagens normais vs. comando `/desafio`
- **Comando Especial:** `/desafio` para exercícios educacionais
- **Coleta Automática:** Dúvidas anônimas via IA
- **Estatísticas Transparentes:** Métricas sem impactar UX
- **Streaming Coordenado:** Resposta em tempo real com citações
- **Session Management:** Múltiplas sessões DB para concorrência

**Impacto:** Interface principal de interação com usuários.

---

### 5. [Sistema de Histórico de Chat](./business_rules_chat_history.md)
**Responsabilidade:** Persistência e gerenciamento de conversas

**Regras Principais:**
- **Isolamento Total:** Cada usuário acessa apenas seus históricos
- **JSON Flexível:** Estrutura adaptável para mensagens
- **Timestamps Automáticos:** created_at e updated_at gerenciados
- **CRUD Completo:** Operações completas com validação rigorosa
- **Integração Seamless:** Coordenação perfeita com sistema de chat
- **Clean Architecture:** Casos de uso específicos e testáveis
- **Transações Isoladas:** Controle de concorrência adequado

**Impacto:** Permite continuidade de conversas entre sessões.

---

### 6. [Sistema de Usuários](./business_rules_users.md)
**Responsabilidade:** Gerenciamento de perfis e permissões

**Modelo Híbrido:**
- **Autenticação:** Google OAuth2
- **Autorização:** Roles internos (USER/ADMIN)

**Regras Principais:**
- **ID Derivado:** Últimos 9 dígitos do Google ID
- **Roles Hierárquicos:** USER (padrão) e ADMIN (privilegiado)
- **Upsert Inteligente:** 3 cenários (novo, mesmo token, token diferente)
- **Cascade Operations:** Usuário é proprietário de todos os dados
- **Timestamps Auditáveis:** Rastreabilidade completa
- **Endpoint Self-Service:** `/users/me` para dados próprios
- **Controle Admin:** Validação rigorosa para operações privilegiadas

**Impacto:** Base de segurança e controle de acesso para todo o sistema.

---

### 7. [Sistema de Perguntas Anônimas](./business_rules_anonymous_questions.md)
**Responsabilidade:** Coleta e análise de dúvidas dos usuários

**Dual Collection:**
- **Automática:** Durante conversas de chat
- **Manual:** Submissão direta pelos usuários

**Regras Principais:**
- **Anonimização Rigorosa:** Sem dados pessoais identificáveis
- **Coleta Transparente:** Usuário não percebe a coleta automática
- **Submissão Pública:** Endpoint aberto para dúvidas manuais
- **Acesso Admin:** Apenas administradores visualizam dados
- **IA Integration:** Topic Agent para classificação automática
- **Análise Estatística:** Métricas para tomada de decisão
- **Conformidade Total:** LGPD/GDPR compliant

**Impacto:** Insights para melhoria contínua do sistema.

---

### 8. [Sistema de Estatísticas de Chat](./business_rules_chat_statistics.md)
**Responsabilidade:** Métricas e análise de performance

**Coleta Transparente:**
- **Performance:** Tempos de resposta, hit rates
- **Comportamento:** Tipos de pergunta, tópicos
- **Temporais:** Padrões de uso por horário/dia

**Regras Principais:**
- **Coleta Automática:** Todas as interações são medidas
- **Anonimização SHA256:** Hashes irreversíveis
- **Timestamp Brasileiro:** UTC-3 (horário de Brasília)
- **Classificação IA:** Topic Agent + tipo de mensagem
- **Métricas Performance:** SLAs e benchmarks definidos
- **Acesso Restrito:** Apenas admins visualizam estatísticas
- **Análises Avançadas:** Insights estratégicos para gestão
- **Alertas Proativos:** Monitoramento com thresholds

**Impacto:** Base para otimização e gestão data-driven.

## Arquitetura Geral

### Padrões Transversais

**Segurança:**
- Autenticação via Google OAuth2 obrigatória
- Autorização baseada em roles (USER/ADMIN)
- Isolamento rigoroso de dados por usuário
- Anonimização completa para métricas/análises

**Performance:**
- Streaming obrigatório para respostas LLM
- Processamento assíncrono quando possível
- Sessões de banco isoladas para concorrência
- Cache e limpeza automática de recursos

**Arquitetura:**
- Clean Architecture com casos de uso
- Padrão Strategy para múltiplos providers
- Singleton services para consistência
- Transaction management com decoradores

**Observabilidade:**
- Logs estruturados em todos os sistemas
- Métricas automáticas de performance
- Audit trail para operações admin
- Health checks e alertas proativos

### Integrações Complexas

**Chat ↔ Todos os Sistemas:**
O sistema de chat é o orquestrador principal, integrando:
- Autenticação (controle de acesso)
- Usuários (identificação e permissões)
- Documentos (contexto RAG)
- LLM (geração de respostas)
- Histórico (persistência)
- Perguntas Anônimas (coleta de insights)
- Estatísticas (métricas de uso)

**Fluxo Típico de Conversa:**
1. **Autenticação** → Valida usuário
2. **Histórico** → Carrega/cria conversa
3. **RAG** → Busca contexto em documentos
4. **LLM** → Gera resposta inteligente
5. **Streaming** → Envia resposta em tempo real
6. **Persistência** → Salva conversa
7. **Analytics** → Coleta métricas anônimas
8. **Dúvidas** → Detecta e armazena perguntas

## Decisões Arquiteturais Importantes

### 1. **Google-First Strategy**
- **Decisão:** Usar apenas Google OAuth2 + Google Drive
- **Justificativa:** Simplicidade, integração nativa, menos complexidade
- **Impacto:** Dependência forte do ecossistema Google

### 2. **Anonimização Rigorosa**
- **Decisão:** Hash SHA256 para todas as métricas
- **Justificativa:** LGPD/GDPR compliance, confiança do usuário
- **Impacto:** Impossibilidade de rastreamento individual

### 3. **Multi-LLM Strategy**
- **Decisão:** Suporte a múltiplos providers (Claude + Ollama)
- **Justificativa:** Flexibilidade, custo, vendor independence
- **Impacto:** Complexidade adicional, mas maior resiliência

### 4. **Triple Document Storage**
- **Decisão:** Google Drive + ChromaDB + PostgreSQL
- **Justificativa:** Cada sistema tem propósito específico
- **Impacto:** Complexidade operacional, mas funcionalidade completa

### 5. **Real-Time First**
- **Decisão:** Streaming obrigatório para todas as respostas
- **Justificativa:** UX superior, percepção de velocidade
- **Impacto:** Complexidade técnica adicional

## Próximos Passos

### Melhorias Sugeridas
1. **Rate Limiting:** Implementar em endpoints públicos
2. **Caching:** Redis para dados frequentes
3. **ML Avançado:** Modelos preditivos para estatísticas
4. **Multi-Tenancy:** Suporte a múltiplas organizações
5. **API Versioning:** Versionamento para evolução

### Monitoramento
1. **Prometheus + Grafana:** Métricas avançadas
2. **Elasticsearch:** Logs centralizados
3. **Health Checks:** Endpoints de saúde
4. **Alerting:** Notificações proativas

### Escalabilidade
1. **Database Sharding:** Particionamento por usuário
2. **Microservices:** Separação de responsabilidades
3. **Load Balancing:** Distribuição de carga
4. **CDN:** Cache de assets estáticos

---

**Última Atualização:** Janeiro 2024  
**Versão:** 1.0  
**Cobertura:** 8 sistemas principais documentados 