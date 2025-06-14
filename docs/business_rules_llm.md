# Regras de Negócio - Sistema de LLM (Large Language Models)

## Visão Geral

O sistema de LLM do ES Chatbot implementa uma arquitetura flexível baseada no padrão Strategy para integração com diferentes provedores de modelos de linguagem. O sistema suporta múltiplos provedores (Anthropic Claude e Ollama) e fornece geração de texto em tempo real via streaming.

## Regras de Negócio Principais

### 1. Arquitetura Strategy para Múltiplos Provedores

**Regra:** O sistema implementa o padrão Strategy para suportar diferentes provedores de LLM de forma intercambiável.

**Provedores Suportados:**
- **Anthropic Claude:** Modelo comercial hospedado na nuvem
- **Ollama:** Modelo open-source auto-hospedado

**Componentes da Arquitetura:**
- `LLMStrategy` (Interface): Define contrato comum para todos os provedores
- `LLMStrategyFactory`: Factory para instanciar estratégia correta
- `ClaudeStrategy`: Implementação para Anthropic Claude
- `OllamaStrategy`: Implementação para Ollama

**Justificativa:**
- **Flexibilidade:** Permite mudança de provedor sem alterar código cliente
- **Extensibilidade:** Facilita adição de novos provedores
- **Abstração:** Clientes não precisam conhecer detalhes de implementação
- **Testabilidade:** Estratégias podem ser testadas independentemente

### 2. Seleção Dinâmica de Provedor

**Regra:** O provedor de LLM é selecionado dinamicamente baseado na configuração.

**Comportamento:**
- Configuração via variável `LLM_PROVIDER`
- Valores aceitos: `'anthropic'` ou `'ollama'` (case-insensitive)
- Falha com `ValueError` se provedor não suportado
- Seleção acontece a cada requisição (permite mudança em runtime)

**Justificativa:**
- **Configurabilidade:** Permite alternar provedores sem recompilação
- **Ambientes:** Diferentes provedores para dev/staging/prod
- **Fallback:** Possibilidade de implementar fallback entre provedores
- **Experimentação:** Facilita A/B testing com diferentes modelos

### 3. Streaming Obrigatório em Tempo Real

**Regra:** Todas as respostas do LLM devem ser entregues via streaming.

**Implementação Técnica:**
- **Protocolo:** Server-Sent Events (SSE)
- **Content-Type:** `text/event-stream`
- **Headers especiais:**
  - `Cache-Control: no-cache`
  - `Connection: keep-alive`
- **Streaming nativo:** Ambos provedores suportam streaming

**Comportamento:**
- Resposta começa imediatamente após primeiro token
- Tokens são enviados conforme gerados pelo modelo
- Finalização marcada com `\n` adicional
- Conexão mantida até resposta completa

**Justificativa:**
- **Experiência do Usuário:** Resposta aparece gradualmente
- **Percepção de Performance:** Reduz tempo percebido de espera
- **Interatividade:** Usuário pode interromper se necessário
- **Eficiência:** Reduz latência inicial da resposta

### 4. Sistema de Prompts Configurável

**Regra:** O sistema utiliza um prompt de sistema configurável para todos os provedores.

**Configuração:**
- Variável: `LLM_SYSTEM_PROMPT`
- Aplicado a todos os provedores
- Enviado como primeira mensagem do contexto
- Não pode ser alterado pelo usuário durante conversa

**Comportamento:**
- **Claude:** Enviado como mensagem de `assistant`
- **Ollama:** Enviado como mensagem de `system`
- Contextualiza o comportamento do modelo
- Define personalidade e regras de resposta

**Justificativa:**
- **Consistência:** Comportamento uniforme entre provedores
- **Controle:** Administradores podem definir comportamento
- **Especialização:** Adapta modelo para domínio específico
- **Governança:** Estabelece regras de uso e restrições

### 5. Singleton Pattern para Serviço

**Regra:** O `LLMService` implementa o padrão Singleton para garantir instância única.

**Implementação:**
- Sobrescrita do método `__new__`
- Instância única armazenada em `_instance`
- Métodos estáticos para execução

**Justificativa:**
- **Eficiência:** Evita reinstanciação desnecessária
- **Consistência:** Garante mesma configuração em toda aplicação
- **Recursos:** Reduz overhead de criação de objetos
- **Estado:** Mantém estado comum se necessário

### 6. Configurações Específicas por Provedor

**Regra:** Cada provedor possui suas próprias configurações obrigatórias.

**Configurações Anthropic Claude:**
- `ANTHROPIC_API_KEY`: Chave de API obrigatória
- `ANTHROPIC_MODEL`: Modelo específico a usar
- `LLM_SYSTEM_PROMPT`: Prompt de sistema
- **Limite de tokens:** Fixo em 1000 tokens por resposta

**Configurações Ollama:**
- `OLLAMA_API_URL`: URL do servidor Ollama
- `OLLAMA_MODEL`: Modelo específico a usar
- `OLLAMA_TIMEOUT`: Timeout para requisições
- `LLM_SYSTEM_PROMPT`: Prompt de sistema

**Justificativa:**
- **Especialização:** Cada provedor tem suas peculiaridades
- **Flexibilidade:** Configurações otimizadas por provedor
- **Isolamento:** Falha em um provedor não afeta configuração do outro
- **Manutenibilidade:** Configurações claras e organizadas

### 7. Tratamento de Erros Específico

**Regra:** Cada provedor implementa seu próprio tratamento de erros.

**Comportamento Claude:**
- Erros de API propagados como exceções
- Falhas de autenticação bloqueiam operação
- Rate limiting retornado como erro HTTP

**Comportamento Ollama:**
- Erros de conexão retornados como texto no stream
- Formato: `"Erro ao conectar com Ollama: {erro}"`
- Não interrompe stream, mas informa erro

**Justificativa:**
- **Robustez:** Diferentes provedores têm diferentes modos de falha
- **Experiência:** Usuário recebe feedback apropriado
- **Debugging:** Erros específicos facilitam diagnóstico
- **Graceful Degradation:** Sistema continua funcionando quando possível

### 8. Autenticação Obrigatória

**Regra:** Todos os endpoints de LLM requerem usuário autenticado.

**Implementação:**
- Security dependency `get_current_user`
- Validação de token em todas as requisições
- Informações do usuário disponíveis para auditoria

**Justificativa:**
- **Controle de Acesso:** Evita uso não autorizado
- **Auditoria:** Rastreabilidade de uso do sistema
- **Rate Limiting:** Base para implementar limites por usuário
- **Custos:** Controle de custos por usuário/departamento

## Fluxos de Negócio

### Fluxo Principal de Geração de Texto

1. **Validação de Autenticação**
   - Sistema valida token do usuário
   - Extrai informações para auditoria

2. **Seleção de Estratégia**
   - Factory consulta `LLM_PROVIDER`
   - Instancia estratégia apropriada
   - Falha se provedor não suportado

3. **Preparação do Contexto**
   - Adiciona system prompt configurado
   - Monta contexto com prompt do usuário
   - Aplica configurações específicas do provedor

4. **Streaming da Resposta**
   - Inicia conexão com provedor
   - Configura headers SSE
   - Transmite tokens conforme recebidos
   - Finaliza com quebra de linha adicional

5. **Tratamento de Erros**
   - Captura exceções durante geração
   - Retorna erro HTTP 500 com detalhes
   - Mantém log para debugging

### Fluxo de Configuração (Anthropic)

1. **Inicialização da Estratégia**
   - Carrega API key das configurações
   - Define modelo a ser usado
   - Configura system prompt

2. **Execução da Requisição**
   - Cria cliente Anthropic assíncrono
   - Monta mensagens com system prompt
   - Configura stream=True e max_tokens=1000

3. **Processamento do Stream**
   - Filtra chunks por tipo 'content_block_delta'
   - Extrai texto do campo 'delta.text'
   - Yield de cada chunk para o cliente

### Fluxo de Configuração (Ollama)

1. **Inicialização da Estratégia**
   - Carrega URL do servidor Ollama
   - Define modelo local a usar
   - Configura timeout para requisições

2. **Execução da Requisição**
   - Cria cliente Ollama assíncrono
   - Monta mensagens com system prompt
   - Configura stream=True

3. **Processamento do Stream**
   - Extrai conteúdo de 'message.content'
   - Fallback para 'content' se necessário
   - Tratamento de erros como parte do stream

## Integrações e Dependências

### Anthropic Claude
- **Biblioteca:** `anthropic` (AsyncAnthropic)
- **Modelo:** Configurável via `ANTHROPIC_MODEL`
- **Autenticação:** API Key obrigatória
- **Rate Limiting:** Controlado pelo provedor

### Ollama
- **Biblioteca:** `ollama` (AsyncClient)
- **Modelo:** Local, configurável via `OLLAMA_MODEL`
- **Conexão:** HTTP/HTTPS para servidor local
- **Timeout:** Configurável para evitar travamentos

### FastAPI
- **Streaming:** StreamingResponse para SSE
- **Segurança:** Security dependency para autenticação
- **Exceções:** HTTPException para erros padronizados

## Configurações Críticas

### Variáveis de Ambiente Obrigatórias
- `LLM_PROVIDER`: Provedor ativo ('anthropic' ou 'ollama')
- `LLM_SYSTEM_PROMPT`: Prompt de sistema comum

### Configurações Anthropic
- `ANTHROPIC_API_KEY`: Chave de API (obrigatória)
- `ANTHROPIC_MODEL`: Modelo específico (ex: 'claude-3-sonnet')

### Configurações Ollama
- `OLLAMA_API_URL`: URL do servidor (ex: 'http://localhost:11434')
- `OLLAMA_MODEL`: Modelo local (ex: 'llama2')
- `OLLAMA_TIMEOUT`: Timeout em segundos

## Limitações e Considerações

### Limitações Atuais
- **Tokens:** Claude limitado a 1000 tokens por resposta
- **Modelos:** Suporte apenas para chat/conversação
- **Contexto:** Sem persistência de contexto entre requisições
- **Rate Limiting:** Sem implementação de rate limiting próprio

### Escalabilidade
- **Concurrent Requests:** Limitado pela capacidade do provedor
- **Ollama:** Dependente de recursos do servidor local
- **Claude:** Dependente de limites da API Anthropic

### Segurança
- **API Keys:** Armazenadas em variáveis de ambiente
- **Logs:** Cuidado com vazamento de prompts em logs
- **Validation:** Sem validação de conteúdo de entrada/saída

### Custos
- **Claude:** Cobrança por token (entrada + saída)
- **Ollama:** Custos de infraestrutura local
- **Monitoramento:** Sem tracking de uso por usuário

## Extensibilidade

### Adição de Novos Provedores
1. Criar nova classe herdando de `LLMStrategy`
2. Implementar método `execute()` com streaming
3. Adicionar ao `LLMStrategyFactory`
4. Definir configurações específicas

