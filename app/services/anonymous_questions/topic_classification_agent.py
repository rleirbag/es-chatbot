import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class TopicDefinition:
    """Definição de um tópico de engenharia de software"""
    name: str
    description: str
    keywords: List[str]
    patterns: List[str]  # Regex patterns for more sophisticated matching
    priority: int  # Higher priority topics are checked first


class SoftwareEngineeringTopicAgent:
    """
    Agente especializado para classificação de tópicos de Engenharia de Software
    """
    
    def __init__(self):
        self.topics = self._initialize_software_engineering_topics()
        # Ordena por prioridade (maior prioridade primeiro)
        self.topics.sort(key=lambda x: x.priority, reverse=True)
        logger.info(f"Agente inicializado com {len(self.topics)} tópicos")
    
    def _initialize_software_engineering_topics(self) -> List[TopicDefinition]:
        """Define todos os tópicos de Engenharia de Software"""
        return [
            # Desenvolvimento de Software - Alta prioridade
            TopicDefinition(
                name="Programação e Desenvolvimento",
                description="Linguagens de programação, sintaxe, algoritmos básicos",
                keywords=[
                    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
                    "código", "programação", "sintaxe", "variável", "função", "método",
                    "loop", "condicional", "array", "lista", "dicionário", "objeto",
                    "classe", "herança", "polimorfismo", "encapsulamento"
                ],
                patterns=[
                    r"como\s+(programar|codificar|escrever\s+código)",
                    r"(erro|bug)\s+no\s+código",
                    r"linguagem\s+de\s+programação",
                    r"(função|método|classe)\s+\w+"
                ],
                priority=9
            ),
            
            # Arquitetura e Design - Alta prioridade
            TopicDefinition(
                name="Arquitetura e Design de Software",
                description="Padrões de design, arquitetura de sistemas, SOLID",
                keywords=[
                    "arquitetura", "design pattern", "padrão", "solid", "mvc", "mvp", "mvvm",
                    "microserviços", "monolito", "clean architecture", "hexagonal",
                    "singleton", "factory", "observer", "strategy", "decorator",
                    "repository", "dependency injection", "modularização"
                ],
                patterns=[
                    r"padrão\s+de\s+(design|projeto)",
                    r"arquitetura\s+de\s+software",
                    r"princípio\s+solid",
                    r"microserviços?\s+vs\s+monolito"
                ],
                priority=9
            ),
            
            # Banco de Dados - Alta prioridade
            TopicDefinition(
                name="Banco de Dados",
                description="SQL, NoSQL, modelagem, otimização",
                keywords=[
                    "banco", "database", "sql", "nosql", "postgresql", "mysql", "mongodb",
                    "redis", "query", "consulta", "tabela", "índice", "join",
                    "normalização", "chave primária", "foreign key", "relacionamento",
                    "orm", "sqlalchemy", "sequelize", "hibernate"
                ],
                patterns=[
                    r"banco\s+de\s+dados",
                    r"consulta\s+sql",
                    r"modelagem\s+de\s+dados",
                    r"otimização\s+de\s+query"
                ],
                priority=8
            ),
            
            # APIs e Web Services - Alta prioridade  
            TopicDefinition(
                name="APIs e Serviços Web",
                description="REST, GraphQL, APIs, integração de sistemas",
                keywords=[
                    "api", "rest", "restful", "graphql", "endpoint", "http", "https",
                    "get", "post", "put", "delete", "patch", "json", "xml",
                    "autenticação", "autorização", "token", "jwt", "oauth",
                    "webhook", "integração", "soap", "rpc"
                ],
                patterns=[
                    r"api\s+(rest|restful|graphql)",
                    r"endpoint\s+\w+",
                    r"autenticação\s+de\s+api",
                    r"integração\s+de\s+sistemas"
                ],
                priority=8
            ),
            
            # Frameworks e Tecnologias Web - Média prioridade
            TopicDefinition(
                name="Frameworks e Desenvolvimento Web",
                description="React, Angular, Vue, Django, Flask, Spring, etc.",
                keywords=[
                    "react", "angular", "vue", "nextjs", "django", "flask", "fastapi",
                    "spring", "express", "nodejs", "laravel", "symfony", "rails",
                    "frontend", "backend", "fullstack", "spa", "pwa",
                    "html", "css", "sass", "bootstrap", "tailwind"
                ],
                patterns=[
                    r"framework\s+(web|frontend|backend)",
                    r"desenvolvimento\s+web",
                    r"(react|angular|vue)\s+\w+"
                ],
                priority=7
            ),
            
            # DevOps e Infraestrutura - Média prioridade
            TopicDefinition(
                name="DevOps e Infraestrutura",
                description="Docker, CI/CD, Cloud, Kubernetes, automação",
                keywords=[
                    "docker", "kubernetes", "container", "devops", "ci/cd", "pipeline",
                    "jenkins", "github actions", "gitlab", "aws", "azure", "gcp",
                    "terraform", "ansible", "vagrant", "cloud", "deploy",
                    "infraestrutura", "monitoramento", "logging"
                ],
                patterns=[
                    r"containerização\s+com\s+docker",
                    r"pipeline\s+de\s+ci/cd",
                    r"infraestrutura\s+como\s+código",
                    r"deploy\s+em\s+(aws|azure|gcp)"
                ],
                priority=7
            ),
            
            # Testes - Média prioridade
            TopicDefinition(
                name="Testes de Software",
                description="Testes unitários, integração, TDD, qualidade",
                keywords=[
                    "teste", "testing", "tdd", "bdd", "unittest", "pytest", "jest",
                    "test", "mock", "cobertura", "coverage", "integração",
                    "unitário", "funcional", "aceitação", "qualidade",
                    "selenium", "cypress", "playwright"
                ],
                patterns=[
                    r"teste\s+(unitário|integração|funcional)",
                    r"tdd\s+e\s+bdd",
                    r"cobertura\s+de\s+testes",
                    r"automação\s+de\s+testes"
                ],
                priority=7
            ),
            
            # Controle de Versão - Média prioridade
            TopicDefinition(
                name="Controle de Versão",
                description="Git, GitHub, GitLab, branching, merge",
                keywords=[
                    "git", "github", "gitlab", "bitbucket", "commit", "push", "pull",
                    "branch", "merge", "rebase", "fork", "clone", "versionamento",
                    "controle", "versão", "repositório", "pull request", "merge request"
                ],
                patterns=[
                    r"controle\s+de\s+versão",
                    r"git\s+(commit|merge|branch|rebase)",
                    r"(github|gitlab)\s+workflow",
                    r"pull\s+request"
                ],
                priority=6
            ),
            
            # Segurança - Média prioridade
            TopicDefinition(
                name="Segurança de Software",
                description="Segurança, criptografia, vulnerabilidades, OWASP",
                keywords=[
                    "segurança", "security", "criptografia", "hash", "ssl", "tls",
                    "vulnerabilidade", "owasp", "sql injection", "xss", "csrf",
                    "autenticação", "autorização", "firewall", "penetration test",
                    "encryption", "decrypt"
                ],
                patterns=[
                    r"segurança\s+de\s+software",
                    r"vulnerabilidade\s+\w+",
                    r"criptografia\s+e\s+segurança",
                    r"(sql\s+injection|xss|csrf)"
                ],
                priority=6
            ),
            
            # Metodologias - Média prioridade
            TopicDefinition(
                name="Metodologias e Processos",
                description="Scrum, Kanban, Agile, metodologias de desenvolvimento",
                keywords=[
                    "scrum", "kanban", "agile", "metodologia", "processo", "sprint",
                    "backlog", "standup", "retrospectiva", "planning", "review",
                    "waterfall", "lean", "xp", "extreme programming", "devops"
                ],
                patterns=[
                    r"metodologia\s+(agile|scrum|kanban)",
                    r"processo\s+de\s+desenvolvimento",
                    r"(sprint|backlog|standup)\s+\w+"
                ],
                priority=5
            ),
            
            # Algoritmos e Estruturas de Dados - Baixa prioridade
            TopicDefinition(
                name="Algoritmos e Estruturas de Dados",
                description="Complexidade, ordenação, busca, estruturas",
                keywords=[
                    "algoritmo", "estrutura", "dados", "complexidade", "big o",
                    "ordenação", "busca", "árvore", "grafo", "lista ligada",
                    "pilha", "fila", "hash table", "recursão", "dynamic programming",
                    "sort", "search", "binary tree", "queue", "stack"
                ],
                patterns=[
                    r"algoritmo\s+de\s+(ordenação|busca)",
                    r"estrutura\s+de\s+dados",
                    r"complexidade\s+(temporal|espacial|big\s+o)",
                    r"(árvore|grafo|lista\s+ligada)"
                ],
                priority=4
            ),
            
            # Ferramentas de Desenvolvimento - Baixa prioridade
            TopicDefinition(
                name="Ferramentas de Desenvolvimento",
                description="IDEs, editores, ferramentas, produtividade",
                keywords=[
                    "ide", "editor", "vscode", "intellij", "eclipse", "pycharm",
                    "vim", "emacs", "sublime", "atom", "terminal", "shell",
                    "debug", "debugger", "linter", "formatter", "refactoring"
                ],
                patterns=[
                    r"(ide|editor)\s+de\s+código",
                    r"ferramentas\s+de\s+desenvolvimento",
                    r"debug\s+e\s+refactoring"
                ],
                priority=3
            ),
            
            # Conceitos Gerais - Baixa prioridade
            TopicDefinition(
                name="Conceitos Gerais",
                description="Conceitos gerais de computação e engenharia de software",
                keywords=[
                    "computação", "software", "engenharia", "sistema", "aplicação",
                    "programa", "development", "tecnologia", "informática"
                ],
                patterns=[
                    r"engenharia\s+de\s+software",
                    r"desenvolvimento\s+de\s+sistemas",
                    r"conceitos?\s+de\s+programação"
                ],
                priority=1
            )
        ]
    
    def classify_topic(self, message: str, context: str = "") -> str:
        """
        Classifica uma mensagem em um tópico de engenharia de software
        
        Args:
            message: A mensagem/pergunta do usuário
            context: Contexto adicional (opcional)
        
        Returns:
            str: Nome do tópico classificado
        """
        text = f"{message} {context}".lower()
        
        # Pontuação para cada tópico
        topic_scores = {}
        
        for topic in self.topics:
            score = 0
            
            # Verifica padrões regex (maior peso)
            for pattern in topic.patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 10
                    logger.debug(f"Pattern match '{pattern}' para tópico '{topic.name}'")
            
            # Verifica palavras-chave (peso normal)
            for keyword in topic.keywords:
                if keyword.lower() in text:
                    score += 1
                    logger.debug(f"Keyword match '{keyword}' para tópico '{topic.name}'")
            
            # Aplica prioridade do tópico como fator de desempate
            if score > 0:
                score += topic.priority * 0.1
                topic_scores[topic.name] = score
        
        if topic_scores:
            # Retorna o tópico com maior pontuação
            best_topic = max(topic_scores, key=topic_scores.get)
            logger.info(f"Tópico classificado: '{best_topic}' (score: {topic_scores[best_topic]})")
            return best_topic
        
        # Se não encontrou nenhum tópico específico
        logger.info("Nenhum tópico específico encontrado, usando 'Outros'")
        return "Outros"
    
    def get_topic_suggestions(self, partial_text: str, limit: int = 5) -> List[str]:
        """
        Retorna sugestões de tópicos baseado em texto parcial
        
        Args:
            partial_text: Texto parcial para busca
            limit: Número máximo de sugestões
        
        Returns:
            List[str]: Lista de nomes de tópicos sugeridos
        """
        text = partial_text.lower()
        suggestions = []
        
        for topic in self.topics:
            # Verifica se alguma palavra-chave contém o texto parcial
            for keyword in topic.keywords:
                if text in keyword.lower() and topic.name not in suggestions:
                    suggestions.append(topic.name)
                    break
        
        return suggestions[:limit]
    
    def get_all_topics(self) -> List[Dict[str, str]]:
        """
        Retorna todos os tópicos disponíveis com suas descrições
        
        Returns:
            List[Dict]: Lista de dicionários com name e description
        """
        return [
            {
                "name": topic.name,
                "description": topic.description,
                "keywords_count": len(topic.keywords),
                "patterns_count": len(topic.patterns)
            }
            for topic in self.topics
        ]
    
    def get_topic_details(self, topic_name: str) -> Optional[Dict]:
        """
        Retorna detalhes específicos de um tópico
        
        Args:
            topic_name: Nome do tópico
            
        Returns:
            Dict: Detalhes do tópico ou None se não encontrado
        """
        for topic in self.topics:
            if topic.name == topic_name:
                return {
                    "name": topic.name,
                    "description": topic.description,
                    "keywords": topic.keywords,
                    "patterns": topic.patterns,
                    "priority": topic.priority
                }
        return None 