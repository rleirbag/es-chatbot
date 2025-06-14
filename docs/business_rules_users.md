# Regras de Negócio - Sistema de Gerenciamento de Usuários

## Visão Geral

O sistema de gerenciamento de usuários do ES Chatbot é responsável pelo controle de acesso, perfis de usuário e hierarquia de permissões. Implementa um modelo híbrido que combina autenticação via Google OAuth2 com controle de acesso baseado em roles (USER/ADMIN), servindo como base para todos os outros sistemas da aplicação.

## Regras de Negócio Principais

### 1. Modelo de Usuário Único e Identificação

**Regra:** Sistema mantém um usuário único por email do Google com identificação numérica derivada.

**Geração de ID:**
- **Fonte:** Últimos 9 dígitos do Google ID (sub)
- **Formato:** Inteiro de 9 dígitos únicos
- **Imutabilidade:** ID nunca muda após criação
- **Finalidade:** Facilita referenciamento e é mais legível que UUIDs

**Unicidade:**
- **Email:** Chave única no banco de dados
- **Constraint:** Email deve ser único na tabela users
- **Validação:** Sistema impede cadastro de emails duplicados
- **Case Sensitivity:** Emails tratados conforme padrão do Google

**Justificativa:**
- **Simplicidade:** Um usuário = um email do Google
- **Consistência:** Integração direta com sistema de autenticação
- **Rastreabilidade:** ID numérico facilita logs e debugging
- **Integridade:** Evita usuários duplicados

### 2. Sistema de Roles e Hierarquia de Permissões

**Regra:** Sistema implementa hierarquia de roles com permissões específicas.

**Roles Disponíveis:**
- **USER (padrão):** Acesso básico ao sistema
- **ADMIN:** Acesso completo incluindo estatísticas e gestão

**Permissões por Role:**

**USER:**
- Fazer upload de documentos pessoais
- Chat com LLM e RAG
- Gerenciar próprio histórico de chat 
- Visualizar próprios dados (/users/me)
- Criar dúvidas anônimas

**ADMIN:**
- Todas as permissões de USER
- Visualizar estatísticas de chat de todos os usuários
- Acessar dúvidas anônimas de todos os usuários
- Visualizar métricas e relatórios do sistema
- Acesso a endpoints administrativos

**Implementação de Segurança:**
- **Validação no endpoint:** Cada rota admin verifica role
- **Erro 403:** Usuários não-admin recebem Forbidden
- **Múltiplas validações:** Email válido + usuário existe + role adequada

**Justificativa:**
- **Segurança:** Separação clara de permissões
- **Administração:** Permite gestão do sistema
- **Escalabilidade:** Fácil adição de novos roles
- **Compliance:** Controle de acesso auditável

### 3. Estratégia "Upsert" Inteligente

**Regra:** Sistema decide automaticamente entre criar, atualizar ou manter usuário.

**Cenários de Comportamento:**

**1. Usuário Novo:**
- Email não existe no banco
- Sistema cria novo registro
- Role padrão: USER
- Timestamps automáticos

**2. Usuário Existente - Mesmo Token:**
- Email existe + refresh_token igual
- Sistema retorna usuário existente
- Sem modificações no banco
- Performance otimizada

**3. Usuário Existente - Token Diferente:**
- Email existe + refresh_token diferente
- Sistema atualiza dados do usuário
- Preserva ID original e role
- Atualiza: nome, avatar_url, refresh_token

**Campos Atualizáveis:**
- name (nome pode mudar no Google)
- avatar_url (foto de perfil pode mudar)
- refresh_token (novo token de acesso)

**Campos Preservados:**
- id (mantém referências)
- email (chave de identificação)
- role (preserva permissões)
- created_at (histórico de criação)

**Justificativa:**
- **Flexibilidade:** Adapta-se a mudanças no Google
- **Performance:** Evita atualizações desnecessárias
- **Integridade:** Preserva referências existentes
- **UX:** Usuário mantém dados mesmo mudando token

### 4. Relacionamentos e Cascade Operations

**Regra:** Usuário é proprietário de todos os seus dados com cascata controlada.

**Relacionamentos Definidos:**
- **documents:** Um para muitos (User → Document)
- **chat_histories:** Um para muitos (User → ChatHistory)
- **chat_statistics:** Um para muitos (User → ChatStatistics)

**Comportamento Cascade:**
- **ON DELETE CASCADE:** Remoção do usuário remove todos os dados
- **Isolamento:** Dados nunca vazam entre usuários
- **Integridade Referencial:** FK constraints garantem consistência

**Implicações:**
- **Privacidade:** Dados completamente isolados por usuário
- **Limpeza:** Remoção completa deixa sistema limpo
- **Performance:** Consultas otimizadas por user_id
- **Compliance:** Conformidade com direito ao esquecimento

**Justificativa:**
- **LGPD/GDPR:** Controle total sobre dados pessoais
- **Manutenção:** Limpeza automática de dados órfãos
- **Segurança:** Impossibilidade de acesso cruzado
- **Simplicidade:** Modelo de dados claro

### 5. Gestão de Timestamps e Auditoria

**Regra:** Sistema mantém rastreabilidade completa de ciclo de vida do usuário.

**Timestamps Automáticos:**
- **created_at:** Momento exato da criação (UTC)
- **updated_at:** Última modificação (UTC)
- **Trigger automático:** updated_at atualizado a cada mudança

**Auditoria Via Logs:**
- **Criação:** Log de criação com dados completos
- **Atualização:** Log de campos modificados
- **Acesso:** Logs de autenticação
- **Ações admin:** Logs de operações privilegiadas

**Casos de Uso:**
- **Debugging:** Identificar quando problemas começaram
- **Analytics:** Análise temporal de uso
- **Compliance:** Histórico para auditoria
- **Suporte:** Investigação de problemas de usuário

**Justificativa:**
- **Transparência:** Rastreabilidade completa
- **Debugging:** Facilita resolução de problemas
- **Analytics:** Base para métricas de crescimento
- **Legal:** Compliance com regulamentações

### 6. Endpoint de Perfil Pessoal

**Regra:** Usuário pode consultar apenas seus próprios dados de perfil.

**Endpoint `/users/me`:**
- **Autenticação obrigatória:** Via JWT token
- **Dados retornados:** id, name, email, avatar_url, role
- **Exclusões:** refresh_token nunca é exposto
- **Validação:** Usuário deve existir no banco

**Dados Expostos:**
```json
{
  "id": 123456789,
  "name": "Nome do Usuário",
  "email": "usuario@gmail.com",
  "avatar_url": "https://...",
  "role": "USER"
}
```

**Segurança:**
- **Token validation:** JWT deve ser válido
- **User existence:** Email do token deve existir no banco
- **No cross-access:** Usuário só vê próprios dados
- **Sanitização:** Dados sensíveis nunca expostos

**Justificativa:**
- **Self-service:** Usuário gerencia próprio perfil
- **Segurança:** Acesso restrito a dados próprios
- **Frontend:** Dados necessários para UI
- **Privacidade:** Controle sobre exposição de dados

### 7. Integração com Sistema de Autenticação

**Regra:** Gerenciamento de usuários integra-se perfeitamente com autenticação OAuth2.

**Fluxo de Integração:**
1. **Login Google:** Usuário autentica via OAuth2
2. **Token validation:** Sistema valida token JWT
3. **User extraction:** Email extraído do token
4. **Database sync:** Usuário criado/atualizado via upsert
5. **Session establishment:** Sessão criada para o usuário

**Dados Sincronizados:**
- **Google Profile:** Nome e foto do Google
- **OAuth Tokens:** refresh_token para APIs
- **Email:** Identificador primário
- **Metadata:** Timestamps automáticos

**Fail-safes:**
- **Token inválido:** Erro 401 Unauthorized
- **Usuário não encontrado:** Erro 404 Not Found
- **Database error:** Erro 500 com logs detalhados
- **Google API down:** Graceful degradation

**Justificativa:**
- **Single Sign-On:** Uma autenticação para todos os serviços
- **Dados atualizados:** Sync automático com mudanças no Google
- **Robustez:** Sistema funciona mesmo com falhas parciais
- **UX:** Experiência fluida entre login e uso

### 8. Controle de Acesso Administrativo

**Regra:** Funcionalidades administrativas requerem validação rigorosa de permissões.

**Validação Admin:**
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

**Endpoints Admin-Only:**
- **Estatísticas:** `/chat-statistics/*`
- **Dúvidas anônimas:** `/anonymous-questions` (GET)
- **Relatórios:** `/anonymous-questions/stats`
- **Temas:** `/anonymous-questions/topics`

**Proteções Implementadas:**
- **Double validation:** Token válido + role ADMIN
- **Error consistency:** Erros padronizados (401/403)
- **Audit trail:** Logs de tentativas de acesso
- **No enumeration:** Mesma resposta para user inexistente/não-admin

**Justificativa:**
- **Segurança:** Dados administrativos protegidos
- **Audit:** Rastreabilidade de acesso admin
- **Compliance:** Separação de responsabilidades
- **Defense in depth:** Múltiplas camadas de validação

## Fluxos de Negócio

### Fluxo de Criação/Atualização de Usuário

1. **Recebimento de Dados do OAuth**
   - Sistema recebe dados do Google após autenticação
   - Extrai: sub (ID), name, email, picture

2. **Geração de ID Numérico**
   - Últimos 9 dígitos do sub do Google
   - Conversão para inteiro

3. **Verificação de Existência**
   - Busca por email no banco
   - Decide estratégia: criar/atualizar/manter

4. **Aplicação da Estratégia Upsert**
   - **Novo:** Criação com role USER padrão
   - **Existente + token igual:** Retorna existente
   - **Existente + token diferente:** Atualiza dados

5. **Persistência e Resposta**
   - Commit da transação
   - Logs da operação
   - Retorno do usuário

### Fluxo de Consulta de Perfil

1. **Validação de Autenticação**
   - Token JWT deve ser válido
   - Email extraído do token

2. **Busca no Banco**
   - Query por email exato
   - Validação de existência

3. **Preparação de Resposta**
   - Exclusão de dados sensíveis
   - Formatação conforme schema

4. **Retorno Seguro**
   - Apenas dados públicos do próprio usuário

### Fluxo de Validação Admin

1. **Extração de Credenciais**
   - Token JWT validado
   - Email extraído

2. **Verificação de Usuário**
   - Busca por email
   - Confirmação de existência

3. **Validação de Role**
   - Verificação role == ADMIN
   - Erro 403 se não for admin

4. **Autorização de Acesso**
   - Access granted para operações admin

## Estruturas de Dados

### Modelo de Banco (User)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    avatar_url VARCHAR NOT NULL,
    role user_role DEFAULT 'USER' NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP NULL,
    refresh_token VARCHAR NOT NULL
);

CREATE TYPE user_role AS ENUM ('USER', 'ADMIN');
```

### Schema de Criação (UserCreate)
```json
{
  "id": 123456789,
  "name": "Nome do Usuário",
  "email": "usuario@gmail.com",
  "refresh_token": "1//...",
  "avatar_url": "https://lh3.googleusercontent.com/..."
}
```

### Schema de Resposta (UserResponse)
```json
{
  "id": 123456789,
  "name": "Nome do Usuário", 
  "email": "usuario@gmail.com",
  "avatar_url": "https://lh3.googleusercontent.com/...",
  "role": "USER"
}
```

## Limitações e Considerações

### Limitações Atuais
- **Roles limitados:** Apenas USER e ADMIN
- **Email único:** Um email = um usuário máximo
- **Google dependency:** Totalmente dependente do Google OAuth2
- **ID collision:** Teórica possibilidade de colisão de IDs

### Escalabilidade
- **Volume:** Suporta milhares de usuários concurrent
- **Queries:** Otimizadas por email (índice único)
- **Relacionamentos:** Eficientes via foreign keys
- **Growth:** Estrutura suporta adição de novos roles

### Segurança
- **Authentication:** Delegada ao Google OAuth2
- **Authorization:** Controlada por roles no sistema
- **Data isolation:** Rigorosa separação por usuário
- **Audit trail:** Logs completos de operações

### Monitoramento
- **Login tracking:** Logs de autenticação
- **Admin actions:** Auditoria de operações privilegiadas
- **Error tracking:** Logs estruturados de falhas
- **Performance:** Métricas de consultas frequentes

### Extensibilidade
- **New roles:** Enum facilita adição de roles
- **New fields:** Schema pode ser expandido
- **New permissions:** Sistema suporta granularidade
- **Integration:** Arquitetura suporta novos provedores OAuth 