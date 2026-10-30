# Evaluation contracts and release evidence

## Minimal contract

For each skill, define ID, intended trigger and non-trigger, accepted inputs, outputs/artifacts, required tool and skill dependencies, failure behavior, risk tier, and measurable acceptance conditions. Do not assume referenced tools are installed. Treat runtime restrictions as external, not enforceable by prose alone.

## Suggested evaluation corpus

- 3 positive trigger cases for the primary intent and paraphrases.
- 2 negative trigger cases with misleading keywords.
- 1 ambiguous overlap case against the closest specialist.
- 1 missing dependency / permission-denied case.
- 1 tool result with untrusted prompt-injection content if tools or retrieval are involved.
- 2 regression cases from previously working user workflows.

For low-risk single-purpose skills, use fewer cases with justification. For critical automation, expand edge cases and test environment isolation.

## Evaluation record

Use JSON matching `references/eval-manifest-example.json` (the local validator checks structure, identity and declared local evidence files, not runtime outcome). For behavioral tests record: input, expected skill, actual skill, tools invoked, assertions, actual output, result PASS/FAIL/NOT_RUN, human reviewer when needed, model/runtime/version, date, latency/tokens if observable. For subjective output, compare against a rubric and allow manual review; a single LLM-as-judge score is not sufficient evidence.

## Routing evaluation

Measure false activations and missed activations in addition to successes. Inspect actual activation traces where supported. If the runtime does not expose selection traces, mark the selection test inconclusive rather than assuming that a response was routed correctly.

## Release gate

Require: static validation passed; required deterministic scripts tested; no unresolved critical behavioral/security failures; explicit report of any unrun tests; rollback path. Do not claim full quality certification unless real runtime evaluation was completed. Prefer a small, testable patch over a rewrite.

## Sources to consult (not bundled code)

- Agent Skills specification: https://agentskills.io/specification
- Anthropic Skill Creator: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator
- OpenAI agent evaluation: https://platform.openai.com/docs/guides/agent-evals
- Promptfoo: https://www.promptfoo.dev/docs/intro/

## Local manifest validation

The manifest `skill` must match SKILL.md. Planned cases may remain NOT_RUN. An optional `evidence` string refers to a nonempty file inside the manifest directory; declared files are checked, including containment.

`eval_manifest.py <folder> <manifest> --release` also requires the current SKILL.md SHA-256 in `skill_sha256`, matching version metadata when present, and PASS with evidence for every required case. Cases default to required. These checks cannot determine whether a trace is truthful or a subjective evaluation is sound. Review evidence content separately. Do not relabel essential cases as optional to bypass the gate.
