# Biblioteca de Skills

Biblioteca central de skills reutilizáveis e versionadas.

- **[Skill Global](skills/skill-global/SKILL.md)**: orquestração geral, pesquisa verificável, diálogo intelectual e seleção de especialistas.
- **[Skill Creator V2](skills/skill-creator/SKILL.md)**: criação, edição, avaliação e empacotamento de skills de uso avulso.

As duas skills são independentes. Este repositório guarda o código-fonte; publicar arquivos aqui **não** instala nem atualiza automaticamente skills em ChatGPT ou Codex.

## Atualização e verificação

Antes de alterar uma skill, comparar com a versão instalada, preservar a identidade e executar a validação estrutural e os testes relevantes. A Skill Global contém a revisão de interação intelectual baseada em evidências; a revisão instalada na conta deve ser comparada antes de aplicar futuras atualizações.

## Instalação global no Codex

Consulte [instalação e carregamento global](docs/codex-installation.md) para backup, atualização das duas skills, roteamento local e incorporação da Skill Global nas instruções globais.

A Skill Creator V2 inclui a revisão local 2.1.0: correções de contenção de caminhos, empacotamento seguro, validação de metadados/manifestos de evidência e 32 testes de regressão determinísticos. Ativação automática e qualidade de resposta exigem avaliação separada no host.
