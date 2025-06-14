# Regras de Negócio - Sistema de Documentos

## Visão Geral

O sistema de documentos do ES Chatbot implementa uma arquitetura de três camadas para gerenciamento de documentos com funcionalidades avançadas de busca semântica. O sistema integra Google Drive (armazenamento), ChromaDB (busca vetorial) e banco de dados relacional (metadados) para criar um sistema completo de RAG (Retrieval-Augmented Generation).

## Regras de Negócio Principais

### 1. Arquitetura de Três Sistemas Independentes

**Regra:** Cada documento é processado e armazenado em três sistemas distintos que operam de forma independente.

**Sistemas:**
- **Google Drive:** Armazenamento físico dos arquivos
- **ChromaDB:** Embeddings vetoriais para busca semântica
- **Banco de Dados:** Metadados e controle de acesso

**Justificativa:**
- **Redundância:** Falha em um sistema não compromete totalmente a funcionalidade
- **Especialização:** Cada sistema otimizado para sua função específica
- **Escalabilidade:** Sistemas podem ser escalados independentemente
- **Flexibilidade:** Permite operações específicas em cada camada

### 2. Validação de Unicidade de Nomes

**Regra:** Não são permitidos arquivos com nomes duplicados no sistema.

**Comportamento:**
- Verificação realizada **antes** do upload para Google Drive
- Consulta no banco de dados pelo campo `name`
- Retorna erro 409 (Conflict) se já existir
- Bloqueia todo o processo de upload

**Justificativa:**
- Evita confusão na identificação de documentos
- Simplifica lógica de busca e referência
- Previne sobrescrita acidental de arquivos

### 3. Gestão Automática de Pastas no Google Drive

**Regra:** Todos os arquivos são organizados em uma pasta específica configurada no Google Drive.

**Comportamento:**
- Pasta definida por `GOOGLE_FOLDER_NAME` (configuração)
- Se a pasta não existir, é criada automaticamente
- Pasta recebe permissões de domínio automaticamente
- Todos os arquivos ficam dentro desta pasta única

**Configuração de Permissões:**
- Tipo: `domain` (todo o domínio da organização)
- Papel: `reader` (apenas leitura)
- Domínio: Configurado em `GOOGLE_DOMAIN`
- Descoberta: `allowFileDiscovery=true`

**Justificativa:**
- Organização centralizada de todos os documentos
- Controle de acesso unificado
- Facilita gestão e backup dos arquivos

### 4. Processamento RAG Obrigatório

**Regra:** Todo documento upload passa obrigatoriamente pelo processamento RAG.

**Processo de Processamento:**
1. **Criação de arquivo temporário** para processamento
2. **Parsing de PDF** usando PyPDFLoader
3. **Chunking** com RecursiveCharacterTextSplitter:
   - Tamanho do chunk: 1000 caracteres
   - Sobreposição: 200 caracteres
4. **Geração de embeddings** usando HuggingFace (all-MiniLM-L6-v2)
5. **Armazenamento no ChromaDB** com metadados completos

**Metadados Incluídos:**
- `source`: Nome original do arquivo
- `chunk_id`: Identificador do pedaço
- `page`: Número da página de origem
- `drive_link`: Link do Google Drive
- `g_file_id`: ID do arquivo no Google Drive

**Justificativa:**
- Permite busca semântica avançada
- Prepara documento para uso em chat com IA
- Indexação automática de conteúdo

### 5. Limpeza Automática de Recursos

**Regra:** O sistema implementa limpeza automática de recursos temporários e cache.

**Comportamento:**
- **Arquivos temporários:** Removidos automaticamente após processamento
- **Cache ChromaDB:** Limpo após cada upload
- **Limpeza garantida:** Executada mesmo em caso de erro (finally block)

**Justificativa:**
- Evita acúmulo de arquivos temporários
- Previne vazamentos de memória
- Garante consistência do cache

### 6. Associação Obrigatória com Usuário

**Regra:** Todo documento deve estar associado a um usuário válido.

**Comportamento:**
- Identificação do usuário via email (token de autenticação)
- Validação da existência do usuário no banco
- Documento associado ao `user_id`
- Falha na associação cancela todo o processo

**Justificativa:**
- Controle de propriedade de documentos
- Auditoria de uploads
- Base para controle de acesso futuro

### 7. Estratégia de Exclusão Independente

**Regra:** A exclusão de documentos opera de forma independente em cada sistema.

**Funcionamento da Exclusão Total:**
- **Google Drive:** Deleta todos os arquivos da pasta configurada
- **ChromaDB:** Remove todos os embeddings da collection
- **Banco de Dados:** Exclui todos os registros da tabela documents

**Características:**
- **Independência total:** Cada sistema processado separadamente
- **Relatório detalhado:** Retorna contadores e erros por sistema
- **Resistência a falhas:** Continua mesmo se um sistema falhar
- **Limpeza de órfãos:** Remove dados inconsistentes entre sistemas

**Justificativa:**
- Resolve problemas de sincronização entre sistemas
- Permite limpeza completa mesmo com dados corrompidos
- Fornece transparência sobre o que foi removido

### 8. Tipos de Arquivo Suportados

**Regra:** Atualmente o sistema só processa arquivos PDF.

**Limitação Técnica:**
- PyPDFLoader usado para parsing
- Outros formatos não são processados para RAG
- Upload pode aceitar outros tipos, mas não serão indexados

**Justificativa:**
- Foco em documentos estruturados
- Garantia de qualidade do processamento
- Simplificação da lógica de parsing

## Fluxos de Negócio

### Fluxo Principal de Upload

1. **Validação de Autenticação**
   - Usuário deve estar autenticado
   - Sistema obtém email do usuário

2. **Validação de Unicidade**
   - Verifica se arquivo com mesmo nome já existe
   - Bloqueia upload se houver duplicata

3. **Preparação para Upload**
   - Lê conteúdo do arquivo
   - Autentica com Google Drive
   - Prepara metadados do arquivo

4. **Upload para Google Drive**
   - Cria/localiza pasta configurada
   - Faz upload do arquivo
   - Configura permissões de domínio
   - Obtém link de compartilhamento

5. **Processamento RAG**
   - Cria arquivo temporário
   - Processa PDF em chunks
   - Gera embeddings
   - Armazena no ChromaDB

6. **Registro no Banco de Dados**
   - Associa arquivo ao usuário
   - Armazena metadados completos
   - Confirma transação

7. **Limpeza**
   - Remove arquivos temporários
   - Limpa cache do ChromaDB

### Fluxo de Exclusão Total (Delete All)

1. **Exclusão no Google Drive**
   - Localiza pasta configurada
   - Lista todos os arquivos da pasta
   - Deleta cada arquivo individualmente
   - Registra sucessos e falhas

2. **Exclusão no ChromaDB**
   - Obtém contagem atual de documentos
   - Executa deleção completa da collection
   - Registra quantidade removida

3. **Exclusão no Banco de Dados**
   - Conta registros existentes
   - Executa DELETE em massa
   - Confirma transação

4. **Geração de Relatório**
   - Monta relatório detalhado por sistema
   - Calcula totais e estatísticas
   - Indica sucesso geral da operação

### Fluxo de Busca de Documentos

1. **Listagem Paginada**
   - Suporte a paginação configurável
   - Ordenação por data de criação (decrescente)
   - Inclui informações do usuário proprietário

2. **Busca no ChromaDB**
   - Listar documentos indexados
   - Obter informações da collection
   - Deletar por ID específico do Google Drive

## Integrações Críticas

### Google Drive API
- **Autenticação:** Service Account com credenciais OAuth2
- **Operações:** Upload, permissões, listagem, exclusão
- **Configurações:** Pasta específica, domínio autorizado

### ChromaDB (Chroma Vector Database)
- **Conexão:** HTTP client com SSL
- **Modelo de Embeddings:** HuggingFace all-MiniLM-L6-v2
- **Collection:** Nome configurável via settings
- **Operações:** Add, query, delete, list

### Banco de Dados Relacional
- **Tabela:** `documents`
- **Relacionamento:** Chave estrangeira para `users`
- **Campos:** nome, links, IDs externos, timestamps

## Configurações Críticas

### Variáveis de Ambiente
- `GOOGLE_FOLDER_NAME`: Nome da pasta no Google Drive
- `GOOGLE_DOMAIN`: Domínio autorizado para acesso
- `CHROMA_HOST`: Servidor do ChromaDB
- `CHROMA_COLLECTION`: Nome da collection

### Configurações do ChromaDB
- **Chunking:** 1000 caracteres com overlap de 200
- **Modelo:** all-MiniLM-L6-v2 (multilingual)
- **Conexão:** HTTPS na porta 443

## Limitações e Considerações

### Limitações Atuais
- **Apenas PDFs:** Outros formatos não são processados
- **Sincronização:** Sem sincronização automática entre sistemas
- **Backup:** Sem backup automático integrado

### Escalabilidade
- **Volume:** Dependente dos limites da API do Google Drive
- **Performance:** Processamento RAG pode ser lento para arquivos grandes
- **Concorrência:** Sem controle de concorrência para uploads simultâneos

### Segurança
- **Acesso:** Baseado em domínio Google (não individual)
- **Auditoria:** Logs detalhados de todas as operações
- **Validação:** Validação de tipos de arquivo limitada 