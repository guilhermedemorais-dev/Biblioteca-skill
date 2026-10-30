# Instalação e carregamento global no Codex

Estas são skills locais, com recursos próprios. Os scripts Python da Skill Creator não exigem um plugin. Publicar este repositório não atualiza instalações existentes.

## Instalar ou atualizar

1. Resolva `CODEX_HOME`; quando não estiver definido, use `~/.codex`.
2. Compare as versões existentes de `skill-global` e `skill-creator`, inclusive em `~/.agents/skills` e no catálogo efetivo do host. Faça backup fora dos diretórios de descoberta antes de substituir.
3. Copie integralmente `skills/skill-global` e `skills/skill-creator` para `<CODEX_HOME>/skills/`, mantendo scripts, referências, testes, assets e metadados de UI. Não misture arquivos de versões antigas.
4. Mantenha apenas a versão escolhida de cada identificador habilitada. Não remova outras skills. Se houver uma Skill Creator nativa concorrente, desabilite somente essa cópia usando a configuração de skills do Codex.
5. Confira os hashes copiados e recarregue o catálogo. A validação estática e os testes abaixo não provam ativação automática.

A revisão da Skill Creator é `2.1.0`, uma revisão local do pacote V2 aprovado pelo usuário, não uma versão oficial upstream. Python 3.10+ e PyYAML são necessários para os validadores; o empacotador seguro foi validado em Linux/POSIX com `O_NOFOLLOW`. Não houve validação em Windows.

## Carregar a Skill Global em todas as tarefas

A presença no catálogo não garante seleção automática. Para fornecer o conteúdo em toda nova tarefa, faça backup de `<CODEX_HOME>/AGENTS.md` e incorpore nele o corpo atual de `skills/skill-global/SKILL.md`, sem o frontmatter, dentro de um bloco claramente delimitado. Preserve as instruções já existentes.

Registre junto ao bloco o caminho canônico da skill e o SHA-256 de seu SKILL.md. Instrua o assistente a resolver referências relativas a partir da pasta da skill e a sincronizar o bloco quando a fonte for atualizada. Não duplique o bloco em atualizações seguintes. Essa opção aumenta o contexto inicial pela extensão do corpo incorporado.

A regra global coordena a conversa e carrega especialistas quando pertinentes; não desativa a Skill Creator ao encaminhar uma tarefa. A Skill Creator continua como skill independente, identificada por `skill-creator`, com seus recursos Python. Não exigir uma URI de plugin para encontrar a instalação local.

Teste o carregamento em uma nova sessão, com um identificador registrado no bloco e sem permitir leitura de arquivos no teste. Isso comprova presença no contexto no runtime testado, não qualidade comportamental nem adesão universal às instruções. Instruções pessoais e AGENTS.md da máquina não devem ser publicados neste repositório.

## Verificar a cópia deste repositório

Na raiz do repositório, com Python e PyYAML disponíveis:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 skills/skill-creator/scripts/quick_validate.py skills/skill-global --profile codex
PYTHONDONTWRITEBYTECODE=1 python3 skills/skill-creator/scripts/quick_validate.py skills/skill-creator --profile codex
PYTHONDONTWRITEBYTECODE=1 python3 skills/skill-creator/scripts/eval_manifest.py skills/skill-creator skills/skill-creator/references/eval-manifest-example.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/skill-creator/tests -v
```

O manifesto é um plano com casos `NOT_RUN`. Os testes de regressão são determinísticos e não executam modelos. Para comportamento, registrar prompts, rastros, versão, ferramentas e resultados reais; conservar `NOT_RUN`/`INCONCLUSIVE` quando apropriado.
