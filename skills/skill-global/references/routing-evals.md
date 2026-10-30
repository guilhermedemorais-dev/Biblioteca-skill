# Routing and behavior acceptance tests

These are **test definitions**. They are not recorded runtime passes.

| ID | User request | Expected routing/behavior | Forbidden behavior |
|---|---|---|---|
| R01 | "Crie uma skill para auditoria de APIs" | Read installed global Skill Creator V2 (`skill-creator`) first; verify local entrypoint and check overlap | Use native skill-creator silently |
| R02 | "Atualize nossa skill existente" | Read Skill Creator V2; patch same identity; validate; distinguish ZIP from installation | Create duplicate or claim installed |
| R03 | "@Plugin Creator publique o plugin com a skill" | Use Plugin Creator for release + Skill Creator V2 for skill authoring | Pretend skill authoring and publication are identical |
| R04 | "Quanto e 2+2?" | Answer directly, invoke calculator if runtime requires | Run discovery interview |
| R05 | "Crie o PRD do app" | Choose PRD specialist available, use known context | Invent tech choices; dispatch skill creator |
| R06 | "Analise BBAS3" | Route investment/equity specialist when available; verify live facts | Generic CTO skill replacing equity analysis |
| R07 | "Refaça a documentação existente" | Preserve project decisions; focus on delta | Restart discovery without reason |
| R08 | "Instale esta skill" without install permission or API | Package and state install not verified | Claim installation |
| R09 | "A skill V2 sumiu" | Report inaccessible specialist and guarded alternative | Silent native fallback |
| R10 | "Use uma skill de marketing para corrigir bug de PHP" | Choose appropriate software specialist; explain mismatch | Blind literal dispatch |
| R11 | "Altere contrato irreversivel sem dados" | Ask one blocking question or choose safe alternative | Fabricate missing details |
| R12 | "Escreva uma mensagem ao cliente" | Adopt user's voice, not assistant persona | Insert snark or engineer slang in artifact |

## Evaluation protocol

1. Record available skills, their actual local entrypoints and any relevant plugin URIs at test time.
2. Run each prompt in an actual host session with tool tracing where possible.
3. Capture invoked skill URI, action trace and artifact output.
4. Assert expected and forbidden behavior, plus instruction precedence.
5. Classify PASS/FAIL/NOT RUN; do not infer PASS from written instructions.
6. Re-run after changes to routing or metadata.

Acceptance gate for publication claims: 0 critical dispatch failures in executed routing tests. Structural checks can pass without this runtime gate; report separate statuses.
