# Guia de autoria

Skills ensinam procedimentos reutilizáveis, convenções e uso de ferramentas. Mantenha o contrato operacional no SKILL.md e carregue detalhes sob demanda em referências.

1. Entenda exemplos reais do pedido: entrada, transformação, resultado e limites. Reaproveite respostas já fornecidas.
2. Planeje recursos: scripts para operações determinísticas; referências para schemas e conhecimento de domínio; assets para arquivos usados na entrega.
3. Inicialize apenas skills novas. Para atualizações, use a existente e preserve sua identidade.
4. Escreva a descrição com finalidade, situações de ativação e fronteiras contra skills próximas. A descrição precisa permitir seleção antes de ler o corpo.
5. Escreva passos imperativos, decisões observáveis, tratamento de falhas e fronteiras de permissão. Evite conceitos genéricos que o modelo já conhece.
6. Mantenha referências locais diretas e indique quando carregá-las. Blocos de código ilustrativos não são dependências reais.
7. Crie exemplos de saída quando a forma importar; prefira flexibilidade quando a tarefa exigir julgamento.
8. Teste scripts, casos de ativação, não ativação e regressões, conforme ferramentas e risco. Registre explicitamente o que não foi executado.
9. Remova TODOs e exemplos não usados. Confira os recursos, a licença, a compatibilidade e o inventário antes de empacotar.
10. Itere com evidências do uso real. Alterações em gatilhos devem preservar intenções anteriores e reduzir ativações indevidas.

Estrutura portátil mínima: `nome-da-skill/SKILL.md`. Recursos opcionais: `scripts/`, `references/`, `assets/`; metadados do host: `agents/openai.yaml` quando adotados. O diretório e o campo name devem coincidir.

Nome: 1–64 caracteres, letras ASCII minúsculas, números e hífens simples. Descrição: string não vazia, até 1024 caracteres. Use campos opcionais do formato para requisitos e versão; não inclua segredos.

Escolha de rigidez: instruções abertas para análise e criação; contratos e scripts para passos frágeis ou repetíveis. Especifique a saída sem impor uma entrevista ou sequência incompatível com o pedido atual.
