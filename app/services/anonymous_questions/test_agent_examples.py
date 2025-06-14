"""
Exemplos de como o Agente de Classificação de Tópicos funciona
Este arquivo demonstra a capacidade do agente de classificar diferentes tipos de perguntas
"""

from app.services.anonymous_questions.topic_classification_agent import SoftwareEngineeringTopicAgent


def test_agent_classification():
    """Testa o agente com exemplos reais de perguntas"""
    
    agent = SoftwareEngineeringTopicAgent()
    
    # Exemplos de perguntas e seus tópicos esperados
    test_cases = [
        # Programação e Desenvolvimento
        ("Como faço um loop em Python?", "Programação e Desenvolvimento"),
        ("O que é uma função em JavaScript?", "Programação e Desenvolvimento"),
        ("Erro no meu código Python", "Programação e Desenvolvimento"),
        ("Como declarar uma variável em Java?", "Programação e Desenvolvimento"),
        
        # Arquitetura e Design
        ("O que é o padrão MVC?", "Arquitetura e Design de Software"),
        ("Como aplicar SOLID principles?", "Arquitetura e Design de Software"),
        ("Diferença entre microserviços e monolito", "Arquitetura e Design de Software"),
        ("Padrão Singleton como implementar?", "Arquitetura e Design de Software"),
        
        # Banco de Dados
        ("Como fazer um JOIN no SQL?", "Banco de Dados"),
        ("O que é normalização de banco?", "Banco de Dados"),
        ("Diferença entre MySQL e PostgreSQL", "Banco de Dados"),
        ("Como otimizar uma query lenta?", "Banco de Dados"),
        
        # APIs e Serviços Web
        ("Como criar uma API REST?", "APIs e Serviços Web"),
        ("O que é autenticação JWT?", "APIs e Serviços Web"),
        ("Diferença entre GET e POST", "APIs e Serviços Web"),
        ("Como integrar sistemas via API?", "APIs e Serviços Web"),
        
        # Frameworks Web
        ("Como usar React Hooks?", "Frameworks e Desenvolvimento Web"),
        ("Configurar um projeto Django", "Frameworks e Desenvolvimento Web"),
        ("Diferença entre Angular e Vue", "Frameworks e Desenvolvimento Web"),
        ("FastAPI vs Flask qual usar?", "Frameworks e Desenvolvimento Web"),
        
        # DevOps
        ("Como usar Docker containers?", "DevOps e Infraestrutura"),
        ("O que é CI/CD pipeline?", "DevOps e Infraestrutura"),
        ("Deploy na AWS como fazer?", "DevOps e Infraestrutura"),
        ("Kubernetes para iniciantes", "DevOps e Infraestrutura"),
        
        # Testes
        ("Como escrever testes unitários?", "Testes de Software"),
        ("O que é TDD?", "Testes de Software"),
        ("Cobertura de testes como medir?", "Testes de Software"),
        ("Automação de testes com Selenium", "Testes de Software"),
        
        # Controle de Versão
        ("Como fazer merge no Git?", "Controle de Versão"),
        ("O que é pull request?", "Controle de Versão"),
        ("Git rebase vs merge", "Controle de Versão"),
        ("Resolver conflitos no GitHub", "Controle de Versão"),
        
        # Segurança
        ("Como evitar SQL injection?", "Segurança de Software"),
        ("O que é criptografia SSL?", "Segurança de Software"),
        ("Vulnerabilidades OWASP top 10", "Segurança de Software"),
        ("Autenticação vs autorização", "Segurança de Software"),
        
        # Metodologias
        ("O que é metodologia Scrum?", "Metodologias e Processos"),
        ("Como fazer sprint planning?", "Metodologias e Processos"),
        ("Diferença entre Agile e Waterfall", "Metodologias e Processos"),
        ("O que é backlog do produto?", "Metodologias e Processos"),
        
        # Algoritmos
        ("Complexidade Big O notation", "Algoritmos e Estruturas de Dados"),
        ("Como implementar ordenação bubble sort?", "Algoritmos e Estruturas de Dados"),
        ("O que é uma árvore binária?", "Algoritmos e Estruturas de Dados"),
        ("Algoritmo de busca em grafos", "Algoritmos e Estruturas de Dados"),
        
        # Ferramentas
        ("Qual IDE usar para Python?", "Ferramentas de Desenvolvimento"),
        ("Como debugar código no VS Code?", "Ferramentas de Desenvolvimento"),
        ("Configurar linter no projeto", "Ferramentas de Desenvolvimento"),
        ("Refactoring tools recomendadas", "Ferramentas de Desenvolvimento"),
        
        # Perguntas que podem ser classificadas como "Outros"
        ("Obrigado pela explicação", "Outros"),
        ("Entendi perfeitamente", "Outros"),
        ("Vou testar agora", "Outros"),
    ]
    
    print("🤖 TESTE DO AGENTE DE CLASSIFICAÇÃO DE TÓPICOS")
    print("=" * 60)
    
    correct_predictions = 0
    total_predictions = len(test_cases)
    
    for question, expected_topic in test_cases:
        predicted_topic = agent.classify_topic(question)
        is_correct = predicted_topic == expected_topic
        
        if is_correct:
            correct_predictions += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} Pergunta: {question}")
        print(f"   Esperado: {expected_topic}")
        print(f"   Predito:  {predicted_topic}")
        print()
    
    accuracy = (correct_predictions / total_predictions) * 100
    print(f"📊 RESULTADOS:")
    print(f"   Acertos: {correct_predictions}/{total_predictions}")
    print(f"   Precisão: {accuracy:.1f}%")
    
    return accuracy


def demonstrate_agent_features():
    """Demonstra outras funcionalidades do agente"""
    
    agent = SoftwareEngineeringTopicAgent()
    
    print("\n🔍 FUNCIONALIDADES DO AGENTE")
    print("=" * 60)
    
    # Mostrar todos os tópicos disponíveis
    print("📚 TÓPICOS DISPONÍVEIS:")
    topics = agent.get_all_topics()
    for i, topic in enumerate(topics, 1):
        print(f"   {i:2d}. {topic['name']}")
        print(f"       {topic['description']}")
        print(f"       Keywords: {topic['keywords_count']}, Patterns: {topic['patterns_count']}")
        print()
    
    # Testar sugestões
    print("💡 SUGESTÕES DE TÓPICOS:")
    test_searches = ["python", "web", "test", "git", "docker"]
    for search in test_searches:
        suggestions = agent.get_topic_suggestions(search)
        print(f"   '{search}' → {suggestions}")
    
    # Detalhes de um tópico específico
    print("\n🔎 DETALHES DE UM TÓPICO:")
    details = agent.get_topic_details("Programação e Desenvolvimento")
    if details:
        print(f"   Nome: {details['name']}")
        print(f"   Descrição: {details['description']}")
        print(f"   Keywords (primeiras 10): {details['keywords'][:10]}")
        print(f"   Patterns: {details['patterns']}")


if __name__ == "__main__":
    # Executa os testes
    accuracy = test_agent_classification()
    
    # Demonstra funcionalidades
    demonstrate_agent_features()
    
    print(f"\n🎯 RESUMO: O agente alcançou {accuracy:.1f}% de precisão nos testes!") 