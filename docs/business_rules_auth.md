# Regras de Negócio - Sistema de Autenticação

## Visão Geral

O sistema de autenticação do ES Chatbot implementa um fluxo OAuth2 com Google, focado na integração com Google Drive para permitir que usuários façam upload e gerenciem documentos. O sistema possui regras específicas para criação e atualização de usuários baseadas no comportamento do Google OAuth.

## Regras de Negócio Principais

### 1. Autenticação Obrigatória via Google

**Regra:** O sistema só aceita autenticação através do Google OAuth2.

**Justificativa:** 
- Necessidade de integração com Google Drive para armazenamento de documentos
- Simplificação do processo de login (sem necessidade de criar contas)
- Aproveitamento da infraestrutura de segurança do Google

**Implementação:**
- Não existe cadastro manual de usuários
- Todos os usuários devem ter uma conta Google válida
- O sistema solicita permissões específicas do Google Drive

### 2. Escopos Específicos do Google

**Regra:** O sistema solicita escopos específicos que são obrigatórios para funcionamento completo.

**Escopos Solicitados:**
- `openid`: Identificação básica do usuário
- `profile`: Nome e informações do perfil
- `email`: Acesso ao email (usado como identificador único)
- `https://www.googleapis.com/auth/drive.file`: **Crítico** - Acesso aos arquivos do Google Drive
- `https://www.googleapis.com/auth/userinfo.profile`: Informações detalhadas do perfil
- `https://www.googleapis.com/auth/userinfo.email`: Informações detalhadas do email

**Comportamento:**
- `access_type=offline`: Garante obtenção do refresh token
- `prompt=consent`: Força reaprovação para garantir refresh token sempre

### 3. Geração de ID Único do Sistema

**Regra:** O sistema gera um ID numérico interno baseado no Google ID.

**Lógica:**
- Pega o Google ID completo (string)
- Extrai os últimos 9 dígitos
- Converte para inteiro
- Usa como ID primário no banco de dados

**Justificativa:**
- Google IDs são muito longos para uso prático
- Garante IDs numéricos únicos
- Mantém rastreabilidade com Google ID original

### 4. Gestão Inteligente de Usuários Existentes

**Regra:** O sistema implementa lógica de "upsert" para usuários.

**Comportamento:**

**Caso 1 - Usuário Novo:**
- Cria novo registro no banco de dados
- Armazena todas as informações do Google

**Caso 2 - Usuário Existente com Mesmo Refresh Token:**
- Retorna usuário existente sem alterações
- Não faz update desnecessário

**Caso 3 - Usuário Existente com Refresh Token Diferente:**
- Atualiza TODOS os dados do usuário
- Atualiza refresh token (mais importante)
- Atualiza nome, avatar_url e outras informações
- **Não atualiza o ID** (mantém consistência)

**Justificativa da Regra:**
- Refresh tokens podem expirar ou ser revogados
- Usuários podem alterar informações no Google (nome, foto)
- Garante que o sistema sempre tenha credenciais válidas

### 5. Validação Obrigatória de Refresh Token

**Regra:** O sistema EXIGE que o Google retorne um refresh token.

**Comportamento:**
- Se não receber refresh token → Retorna erro 400
- Mensagem: "Não foi possível obter o refresh token"

**Justificativa:**
- Refresh token é essencial para operações com Google Drive
- Sem refresh token, usuário não consegue usar funcionalidades principais
- Força configuração correta do OAuth (consent screen)

### 6. Codificação Segura de Credenciais

**Regra:** As credenciais nunca são transmitidas em texto plano para o frontend.

**Processo:**
1. Monta objeto com todas as credenciais
2. Serializa para JSON
3. Codifica em Base64
4. Envia para frontend via query parameter

**Credenciais Incluídas:**
- `access_token`: Token de acesso atual
- `refresh_token`: Token para renovação
- `expires_in`: Tempo de expiração
- `token_type`: Tipo do token (Bearer)
- `id_token`: Token de identidade JWT
- `picture`: URL da foto do usuário

### 7. Renovação Automática de Tokens

**Regra:** O sistema fornece endpoint para renovação de access tokens.

**Comportamento:**
- Aceita refresh token
- Solicita novo access token ao Google
- Retorna novos tokens ou null em caso de erro

**Status:** Implementação parcial (TODO pendente para usuário logado)

### 8. Controle de Acesso por Autenticação

**Regra:** Todas as funcionalidades principais exigem usuário autenticado.

**Implementação:**
- Dependency `get_current_user` protege rotas
- Valida tokens de forma centralizada
- Rota `/auth/protected` serve para testar autenticação

## Fluxos de Negócio

### Fluxo Principal de Login

1. **Usuário acessa `/auth/login`**
   - Sistema redireciona para Google OAuth
   - Solicita todos os escopos necessários

2. **Usuário autoriza no Google**
   - Google redireciona para `/auth/callback`
   - Inclui código de autorização

3. **Sistema processa callback**
   - Troca código por tokens
   - Valida presença de refresh token
   - Obtém informações do usuário

4. **Gestão do usuário**
   - Verifica se usuário existe (por email)
   - Aplica lógica de upsert conforme regras

5. **Finalização**
   - Codifica credenciais
   - Redireciona para frontend com credenciais

### Fluxo de Erro - Sem Refresh Token

1. **Google não retorna refresh token**
   - Acontece quando usuário já autorizou antes
   - Ou quando configuração OAuth está incorreta

2. **Sistema detecta ausência**
   - Retorna HTTP 400
   - Não prossegue com criação/atualização

3. **Resolução**
   - `prompt=consent` força nova autorização
   - Usuário deve reautorizar aplicação

## Impactos nas Outras Funcionalidades

### Integração com Google Drive
- **Dependência Total:** Sem autenticação Google, usuário não pode upload documentos
- **Tokens Válidos:** Sistema precisa manter tokens atualizados para operações Drive

### Sistema de Chat
- **Identificação:** Email é usado para associar conversas ao usuário
- **Histórico:** Conversas são vinculadas ao ID do usuário

### Documentos
- **Propriedade:** Documentos são associados ao usuário que fez upload
- **Acesso:** Usuário só acessa seus próprios documentos

## Configurações Críticas

### Variáveis de Ambiente Obrigatórias
- `GOOGLE_CLIENT_ID`: ID da aplicação no Google Console
- `GOOGLE_SECRET_KEY`: Chave secreta da aplicação
- `GOOGLE_REDIRECT_URI`: URI autorizada para callback
- `FRONTEND_URL`: URL base do frontend para redirecionamento final

### Configurações do Google Console
- **Consent Screen:** Deve estar configurado corretamente
- **Scopes:** Todos os escopos devem estar aprovados
- **Redirect URIs:** Devem incluir a URI de callback exata
- **Domain Verification:** Para acesso ao Google Drive 