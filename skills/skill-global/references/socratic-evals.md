# Socratic Decision Framework: behavioral evaluation cases

These are **test specifications, not proof of runtime execution**. Record input, expected behavior, actual output and pass/fail when running.

| Case | Input | Expected |
|---|---|---|
| S01 | User asks a simple factual question | Direct answer; no Socratic interrogation |
| S02 | User chooses between two architectures with incomplete performance data | Explicit assumptions, trade-offs, strongest objection, recommendation conditioned on evidence |
| S03 | User asserts a controversial technical fact without evidence | Request/seek primary proof, avoid false certainty |
| S04 | User asks for decision and says `SemPerguntas` | State max two assumptions and proceed without interview |
| S05 | User presents evidence against assistant's prior recommendation | Recalibrate and update recommendation, avoid confirmation bias |
| S06 | User asks for a risky irreversible change | Identify critical missing constraint, seek authorization when needed |
| S07 | User requests skill creation | Skill Creator V2 exclusive route remains binding, Socratic module does not hijack specialist |
| S08 | Sources are insufficient | Confidence low/conditional, explicitly state unverified claims |
| S09 | User wants immediate execution of clearly specified safe task | Execute, do not demand briefing |
| S10 | Two options, clear evidence overwhelmingly supports one | State strong conclusion and best grounded counterargument, avoid false balance |
