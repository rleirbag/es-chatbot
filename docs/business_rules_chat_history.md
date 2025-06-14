# Regras de Negócio - Sistema de Histórico de Chat

## Visão Geral

O sistema de histórico de chat do ES Chatbot gerencia a persistência, recuperação e controle de acesso às conversas dos usuários. Implementa um modelo de dados JSON flexível para armazenar mensagens estruturadas, com controle rigoroso de propriedade e isolamento por usuário, permitindo continuidade de conversas entre sessões.

## Regras de Negócio Principais

### 1. Isolamento Total por Usuário

**Regra:** Cada usuário só pode acessar seus próprios históricos de chat.

**Implementação de Segurança:**
- **Identificação:** Usuário identificado pelo email do token JWT
- **Validação dupla:** Verificação de existência + propriedade do histórico
- **Erro 403:** Tentativa de acesso a histórico de outro usuário
- **Erro 404:** Usuário não encontrado ou histórico inexistente

**Comportamento:**
- Todas as operações (GET, POST, PUT, DELETE) verificam propriedade
- Busca automática filtra apenas históricos do usuário
- Impossibilidade de acesso cruzado entre usuários

**Justificativa:**
- **Privacidade:** Conversas são dados pessoais sensíveis
- **Compliance:** Conformidade com LGPD/GDPR
- **Confiança:** Usuários devem confiar no isolamento
- **Segurança:** Prevenção de vazamentos de dados

### 2. Estrutura JSON Flexível para Mensagens

**Regra:** Mensagens são armazenadas em formato JSON estruturado para máxima flexibilidade.

**Estrutura Padrão:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Pergunta do usuário"
    },
    {
      "role": "assistant", 
      "content": "Resposta do assistente com **fontes consultadas:**..."
    }
  ]
}
```

**Campos Obrigatórios:**
- `role`: "user" ou "assistant"
- `content`: Texto completo da mensagem

**Flexibilidade:**
- **Extensibilidade:** Novos campos podem ser adicionados
- **Metadata:** Suporte a informações adicionais por mensagem
- **Versionamento:** Estrutura pode evoluir sem quebrar dados existentes
- **Compatibilidade:** Formato compatível com APIs de LLM

**Justificativa:**
- **Flexibilidade:** JSON permite estruturas complexas
- **Performance:** Consultas eficientes para sequências de mensagens
- **Integração:** Formato nativo para LLMs
- **Evolução:** Estrutura adaptável a novos requisitos

### 3. Gestão Automática de Timestamps

**Regra:** Sistema mantém timestamps automáticos de criação e atualização.

**Comportamento:**
- **created_at:** Definido automaticamente na criação
- **updated_at:** Atualizado automaticamente a cada modificação
- **Timezone:** UTC padrão do banco de dados
- **Imutabilidade:** created_at nunca muda após criação

**Casos de Uso:**
- **Ordenação:** Históricos mais recentes primeiro
- **Auditoria:** Rastreamento de quando conversas aconteceram
- **Limpeza:** Base para políticas de retenção de dados
- **Analytics:** Análise temporal de uso

**Justificativa:**
- **Rastreabilidade:** Histórico completo de modificações
- **Auditoria:** Compliance e debugging
- **UX:** Ordenação cronológica para usuários
- **Manutenção:** Base para limpeza automática

### 4. Operações CRUD Completas com Validação

**Regra:** Sistema oferece operações CRUD completas com validação rigorosa.

**Create (POST):**
- Requer autenticação obrigatória
- user_id automaticamente associado ao usuário autenticado
- Estrutura JSON validada no schema
- Resposta 201 com objeto criado

**Read (GET):**
- **Lista completa:** GET `/chat-history/` - todos os históricos do usuário
- **Item específico:** GET `/chat-history/{id}` - histórico específico com validação de propriedade
- Filtro automático por user_id

**Update (PUT):**
- Validação de propriedade obrigatória
- Substituição completa do campo chat_messages
- updated_at automaticamente atualizado
- Preservação de metadados (id, user_id, created_at)

**Delete (DELETE):**
- Validação de propriedade obrigatória
- Remoção física do registro
- Resposta 204 (No Content) em caso de sucesso
- Operação irreversível

**Justificativa:**
- **Completude:** API REST completa
- **Consistência:** Padrões uniformes em todas as operações
- **Segurança:** Validação em todas as operações
- **Flexibilidade:** Suporte a todos os casos de uso

### 5. Integração com Sistema de Chat Principal

**Regra:** O histórico integra-se perfeitamente com o sistema de chat em tempo real.

**Fluxo de Integração:**
1. **Chat verifica histórico:** Busca por chat_history_id fornecido
2. **Validação de propriedade:** Confirma que usuário é proprietário
3. **Carregamento de contexto:** Mensagens anteriores alimentam o LLM
4. **Atualização automática:** Nova mensagem adicionada ao histórico existente

**Criação Automática:**
- Se chat_history_id é null → Sistema cria novo histórico automaticamente
- Estrutura inicial: `{"messages": []}`
- Associação imediata ao usuário autenticado

**Persistência Coordenada:**
- Chat salva tanto pergunta quanto resposta
- Formato mantido consistente entre sistemas
- Transações isoladas para evitar conflitos

**Justificativa:**
- **Experiência Contínua:** Conversas persistem entre sessões
- **Contexto:** LLM mantém memória de conversas anteriores
- **Automação:** Usuário não precisa gerenciar históricos manualmente
- **Consistência:** Dados sincronizados entre sistemas

### 6. Arquitetura de Casos de Uso (Clean Architecture)

**Regra:** Sistema implementa Clean Architecture com casos de uso específicos.

**Casos de Uso Implementados:**
- **CreateChatHistoryUseCase:** Criação com validação completa
- **GetChatHistoryUseCase:** Busca individual e listagem com filtros
- **UpdateChatHistoryUseCase:** Atualização com validação de propriedade
- **DeleteChatHistoryUseCase:** Remoção com validação de propriedade

**Vantagens da Arquitetura:**
- **Separação de Responsabilidades:** Lógica de negócio isolada
- **Testabilidade:** Casos de uso testáveis independentemente
- **Reutilização:** Casos de uso compartilhados entre routers
- **Manutenibilidade:** Mudanças isoladas em cada caso de uso

**Padrão de Implementação:**
- Todos retornam tupla `(resultado, erro)`
- Decorador `@commit` para transações automáticas
- Logs estruturados para debugging
- Tratamento consistente de exceções

**Justificativa:**
- **Qualidade:** Código mais testável e manutenível
- **Padronização:** Estrutura consistente em todo o sistema
- **Flexibilidade:** Facilita mudanças e extensões
- **Robustez:** Tratamento de erro padronizado

### 7. Controle de Concorrência e Transações

**Regra:** Sistema gerencia adequadamente concorrência e transações.

**Estratégia de Transações:**
- **Decorador @commit:** Commit automático em casos de uso
- **Rollback automático:** Em caso de exceções
- **Isolamento:** Cada operação em transação separada
- **Sessões isoladas:** Evita conflitos entre operações

**Concorrência:**
- **Chat integrado:** Usa nova sessão para evitar locks longos
- **Operações independentes:** Casos de uso isolados
- **Estado consistente:** Transações ACID garantem consistência

**Tratamento de Erros:**
- **Graceful failure:** Erros não comprometem outras operações
- **Logs detalhados:** Para debugging e auditoria
- **Códigos consistentes:** HTTP status codes padronizados

**Justificativa:**
- **Robustez:** Sistema mantém consistência sob carga
- **Performance:** Evita locks desnecessários
- **Confiabilidade:** Dados sempre em estado válido
- **Debugging:** Facilita identificação de problemas

### 8. Relacionamentos de Banco de Dados

**Regra:** Históricos mantêm relacionamentos apropriados com outras entidades.

**Relacionamento com User:**
- **Chave estrangeira:** user_id obrigatória
- **Cascade delete:** Históricos removidos se usuário for removido
- **Back reference:** User.chat_histories para acesso bidirecional

**Relacionamento com Estatísticas:**
- **Referência indireta:** Estatísticas referenciam user_id
- **Anonimização:** Dados de histórico não vazam para estatísticas
- **Análise cruzada:** Possível correlação para analytics

**Indexação:**
- **Primary key:** id para acesso direto
- **Foreign key:** user_id para filtragem eficiente
- **Ordenação:** created_at para ordem cronológica

**Justificativa:**
- **Integridade:** Relacionamentos garantem consistência
- **Performance:** Índices otimizam consultas frequentes
- **Manutenção:** Cascade operations simplificam limpeza
- **Analytics:** Relacionamentos suportam análises futuras

## Fluxos de Negócio

### Fluxo de Criação de Histórico

1. **Autenticação**
   - Sistema valida token JWT
   - Extrai email do usuário

2. **Validação de Usuário**
   - Busca usuário no banco pelo email
   - Erro 404 se usuário não existe

3. **Preparação do Histórico**
   - Associa user_id automaticamente
   - Valida estrutura JSON das mensagens
   - Define timestamps automáticos

4. **Persistência**
   - Executa caso de uso de criação
   - Commit automático da transação
   - Retorna histórico criado (201)

### Fluxo de Busca de Históricos

1. **Listagem Completa (GET /chat-history/)**
   - Autenticação do usuário
   - Filtragem automática por user_id
   - Retorna lista ordenada por created_at

2. **Busca Específica (GET /chat-history/{id})**
   - Autenticação do usuário
   - Validação de existência do histórico
   - Verificação de propriedade
   - Erro 403 se não for proprietário

### Fluxo de Atualização

1. **Validação Inicial**
   - Autenticação obrigatória
   - Verificação de existência
   - Confirmação de propriedade

2. **Atualização**
   - Substituição de chat_messages
   - Preservação de metadados
   - updated_at automaticamente atualizado

3. **Persistência**
   - Commit da transação
   - Retorna objeto atualizado

### Fluxo de Exclusão

1. **Validação Rigorosa**
   - Autenticação obrigatória
   - Verificação de existência
   - Confirmação de propriedade

2. **Remoção**
   - Delete físico do registro
   - Commit da transação
   - Resposta 204 (No Content)

### Fluxo de Integração com Chat

1. **Recebimento de Requisição de Chat**
   - chat_history_id fornecido ou null

2. **Decisão de Fluxo**
   - Se ID fornecido: busca e valida histórico existente
   - Se null: cria novo histórico automaticamente

3. **Carregamento de Contexto**
   - Extrai mensagens do JSON
   - Formata para alimentar LLM
   - Mantém sequência cronológica

4. **Atualização Pós-Chat**
   - Adiciona pergunta e resposta ao histórico
   - Salva em nova sessão para evitar conflitos
   - Preserva formato estruturado

## Estruturas de Dados

### Modelo de Banco (ChatHistory)
```sql
CREATE TABLE chat_histories (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    chat_messages JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Schema de Entrada (ChatHistoryCreate)
```json
{
  "chat_messages": {
    "messages": [
      {"role": "user", "content": "string"},
      {"role": "assistant", "content": "string"}
    ]
  },
  "user_id": null  // Preenchido automaticamente
}
```

### Schema de Atualização (ChatHistoryUpdate)
```json
{
  "chat_messages": {
    "messages": [
      // Array completo de mensagens atualizado
    ]
  }
}
```

## Limitações e Considerações

### Limitações Atuais
- **Tamanho JSON:** Sem limite explícito para chat_messages
- **Versionamento:** Sem controle de versão de estrutura
- **Busca:** Sem busca por conteúdo dentro das mensagens
- **Backup:** Sem backup incremental de mudanças

### Escalabilidade
- **Volume:** Dependente de limites do banco PostgreSQL
- **Consultas:** Otimizadas por índices em user_id
- **JSON:** Performance pode degradar com mensagens muito longas
- **Concorrência:** Sem limite de operações simultâneas

### Segurança
- **Isolamento:** Rigorosamente implementado por usuário
- **Auditoria:** Logs de todas as operações
- **Criptografia:** Dados em repouso conforme configuração do banco
- **Validação:** Schemas garantem estrutura correta

### Monitoramento
- **Logs estruturados:** Para todas as operações
- **Métricas:** Via casos de uso e decoradores
- **Erros:** Tratamento e logging consistente
- **Performance:** Timestamps para análise temporal

### Extensibilidade
- **Schema flexível:** JSON permite evolução
- **Novos campos:** Adicionáveis sem breaking changes
- **Casos de uso:** Estrutura permite novos casos facilmente
- **Integrações:** Arquitetura suporta novas integrações 