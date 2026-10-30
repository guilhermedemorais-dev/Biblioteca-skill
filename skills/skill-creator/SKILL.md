---
name: skill-creator
description: Crie, edite, melhore, audite, valide, teste e empacote skills existentes ou novas, preservando identidade e funções. Use para pedidos sobre SKILL.md, gatilhos de ativação, avaliações e distribuição de skills, inclusive perguntas sobre como criá-las. Create, edit, audit, validate, test or package agent skills. Não ativar para habilidades pessoais, auditoria de aplicações sem skills ou dúvidas técnicas gerais.
compatibility: Codex Desktop/CLI ou host com arquivos locais; scripts exigem Python 3.10+ e PyYAML. Ferramentas de execução de modelos são opcionais e devem ser verificadas no ambiente.
metadata:
  version: "2.1.0"
  required-files: "agents/openai.yaml scripts/init_skill.py scripts/quick_validate.py scripts/eval_manifest.py scripts/package_skill.py references/evaluation-contracts.md references/eval-manifest-example.json references/authoring-guide.md references/workflows.md references/output-patterns.md references/sample-prompts.md tests/test_regression.py"
---

# Skill Creator V2

Esta distribuição atualiza a skill `skill-creator`. Preserve esse identificador e sua responsabilidade; não crie uma especialista duplicada. A versão 2.1.0 é uma revisão local autorizada do ZIP V2 fornecido pelo usuário, sem alegação de versão oficial upstream.

## Escolher o fluxo

Identifique a intenção e o resultado antes de agir:

| Pedido | Ação | Entrega |
| --- | --- | --- |
| Explicar skills | Responder no contexto do host real | Explicação ou exemplos úteis |
| Criar | Definir contrato, exemplos e avaliações; inicializar e implementar | Skill completa e `skill.zip` |
| Atualizar | Inventariar baseline e preservar funções; alterar o delta aprovado | Skill atualizada e `skill.zip` |
| Auditar | Ler e testar em área temporária; não editar a instalação | Achados por prioridade, evidências e melhorias |
| Validar | Executar verificações pertinentes e declarar limites | Diagnóstico; não reempacotar por obrigação |
| Testar | Usar fixtures e runtime disponível, respeitando efeitos externos | Casos, rastros e resultados reais |
| Empacotar | Inspecionar inventário e gerar ZIP seguro | `skill.zip`, hash e exclusões |
| Instalar | Usar o instalador disponível, backup e descoberta real do host | Caminho, integridade e estado de ativação |

Não presuma interface `/skills`, importador de plugin ou ferramentas de outro produto. Esta pasta local não cria um plugin nem uma URI `skills://plugins/...`. Verifique as capacidades disponíveis. Autorias e regras de uma skill não ampliam permissões do usuário ou runtime.

## Contexto e contrato

Antes de criar ou atualizar, leia [o contrato de avaliação](references/evaluation-contracts.md) e inventarie gatilhos, dependências, scripts, referências, funções existentes e restrições.

Use o contexto já fornecido. Pergunte apenas por dados indispensáveis ainda ausentes; entrada, saída e conectores podem ser inferidos de requisitos explícitos, sem entrevista fixa. Um pedido de auditoria ou validação não autoriza modificar a skill.

Defina entradas, saídas, dependências, limites, recuperação de falhas e critérios observáveis. Prepare casos positivos, negativos, ambíguos, falhas e regressões proporcionais ao risco antes do patch. Em roteadores, avaliar delegação e não delegação. Não delegue por mera coincidência de palavras.

## Criar e editar

Consulte [o guia de autoria](references/authoring-guide.md), [padrões de workflow](references/workflows.md), [padrões de saída](references/output-patterns.md) e [exemplos de pedidos](references/sample-prompts.md) conforme a tarefa.

```sh
python3 scripts/init_skill.py nome-da-skill --path /destino/aprovado
```

O inicializador gera um rascunho com TODOs e exemplos, não uma skill pronta. Preencha instruções e metadados, remova exemplos desnecessários e teste os scripts alterados. Preserve recursos e funções existentes em atualizações; documente qualquer remoção deliberada.

O formato portátil exige `SKILL.md`; `agents/openai.yaml` é opcional nesse formato. Para a distribuição Codex deste pacote, forneça metadados de UI e valide com `--profile codex`. Campos opcionais válidos incluem `compatibility`, `license`, `allowed-tools` e `metadata`; não invente campos superiores. Nome e diretório devem coincidir.

## Receber ZIPs

Inspecione os membros antes de extrair: rejeite caminhos absolutos, `..`, separadores ambíguos, symlinks e entradas especiais; limite número de arquivos, tamanho descomprimido e razão de compressão conforme o ambiente. Extraia em área temporária, conferindo contenção dos caminhos.

Localize `SKILL.md` e identifique as skills reais. Se houver múltiplas skills, explique a composição e use um fluxo de instalação/publicação compatível ou delimite o escopo; não presuma um importador de plugins inexistente. Não execute código de um ZIP recebido como validador confiável sem inspecioná-lo. Use os validadores já confiáveis do ambiente.

Validação não significa instalação. Instalação não comprova ativação. Não extraia sobre uma skill ativa; mantenha o original e o rollback até validar a candidata. Não reempacote automaticamente um ZIP recebido só para auditar ou validar.

## Validar e avaliar

```sh
python3 scripts/quick_validate.py /pasta/nome-da-skill
python3 scripts/quick_validate.py /pasta/nome-da-skill --profile codex
python3 scripts/eval_manifest.py /pasta/nome-da-skill /pasta-das-evidencias/manifest.json
python3 -m unittest discover -s tests -v
```

`quick_validate.py` verifica metadados, identidade, links Markdown locais fora de exemplos cercados por fences, recursos de `metadata.required-files` e UI quando aplicável. Não certifica semântica das instruções, todo formato possível de link nem conteúdo livre de segredos.

`eval_manifest.py` verifica estrutura, identidade e evidências locais declaradas. O manifesto de exemplo desta skill é um plano, com casos `NOT_RUN`; não é resultado de testes. Para verificar registros de liberação:

```sh
python3 scripts/eval_manifest.py /pasta/nome-da-skill /pasta-das-evidencias/manifest.json --release
```

Esse modo exige versão, hash atual de SKILL.md e PASS com arquivo de evidência para casos obrigatórios. O script não executa modelos, nem prova que a evidência é verdadeira. O responsável precisa avaliar seu conteúdo. Não contorne o gate marcando casos essenciais como opcionais.

Quando houver runner disponível, executar os mesmos casos contra baseline e candidata, registrando modelo/runtime, prompts, seleção da skill quando observável, ferramentas, saídas, falhas, permissões e custo/latência quando disponíveis. Usar assertions determinísticas quando possível. Não transformar julgamento subjetivo de um único modelo em certificação.

Sem runner, entregar plano executável e registrar `NOT_RUN`. Sem evidência de seleção, registrar `INCONCLUSIVE`. Bloquear liberação em falha crítica ou regressão material; comunicar separadamente testes determinísticos, comportamento observado e lacunas.

## Empacotar e entregar

```sh
python3 scripts/package_skill.py /pasta/nome-da-skill /destino-fora-da-skill --dry-run
python3 scripts/package_skill.py /pasta/nome-da-skill /destino-fora-da-skill
```

Revisar o inventário antes de distribuir. O script rejeita symlinks e saídas dentro da origem; exclui arquivos sensíveis conhecidos, caches e seu próprio artefato; mantém `.env.example`. Recursos obrigatórios excluídos bloqueiam o pacote. Para exceções legítimas, revisar/renomear os recursos ou ajustar conscientemente a política; não desativar os controles silenciosamente.

O pacote é escrito em temporário, conferido e substituído atomicamente como `skill.zip`. O limite padrão local é 25 MiB, não uma afirmação sobre todo host. Conferir o limite real de destino. A política por nome não detecta segredos em qualquer texto: revisar o conteúdo antes de publicação. Empacotar uma árvore local estável, sem processos concorrentes alterando seus diretórios.

Para criação, atualização ou empacotamento solicitado, entregar o ZIP completo, hash, verificações, limitações e rollback pertinente. Na instalação, comprovar leitura posterior e descoberta pelo host. Preservar a versão anterior em erro. Nunca chamar ZIP preparado de instalado, validação estática de teste comportamental, ou descoberta de ativação automática garantida.
