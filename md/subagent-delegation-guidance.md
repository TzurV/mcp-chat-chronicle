# Subagent Delegation Guidance

This guide records how to request and brief a subagent clearly. It addresses a
failure mode observed in this project: a spawned agent inherited the phrase
"spawn one subagent" and interpreted it as an instruction to delegate again,
rather than recognizing that it was the requested subagent.

## Separate The Two Instructions

A subagent workflow has two different prompts:

1. **The owner-to-manager request** tells the manager to spawn an agent.
2. **The manager-to-subagent assignment** tells the spawned agent to perform
   the work itself.

Do not copy the owner-to-manager wording into the subagent assignment without
rewriting the role boundary. In particular, remove instructions such as
"spawn," "delegate," or "create another agent" unless nested delegation is
actually intended.

## Owner-To-Manager Template

Use this pattern when asking the development manager to delegate work:

```text
Spawn exactly one subagent for this research task.

The manager should delegate the work and monitor completion. The spawned
subagent must perform the research itself; it must not spawn or delegate to
another agent.

Subagent assignment:
- Research how teacher-created FABLE references support prompt optimization.
- Compare reference scoring with LLM-as-judge and human review.
- Cover costs, benefits, limitations, BootstrapFewShot, DSPy, and GEPA.
- Prefer primary and official sources.
- Write the research brief to:
  md/research/fable-references-prompt-optimization-research.md
- Do not write the final LinkedIn article.
- Modify no file except the named deliverable.
- Do not stage or commit changes.

The manager should report when the subagent is started and review the returned
artifact when it completes.
```

## Manager-To-Subagent Template

The manager should send an assignment that begins with an explicit role:

```text
You are the research subagent already spawned for this assignment.

Perform the work yourself. Do not spawn another agent, create another task,
delegate the research, or return instructions for someone else. Do not stop at
a plan or proposal; complete the required deliverable.

Objective:
Research how teacher-created FABLE references can support prompt optimization
and reduce repeated strong-model calls.

Required coverage:
1. Define the terminology and distinguish project-specific language from
   established industry terms.
2. Explain teacher references, silver labels, evaluation sets, prompt search,
   LLM-as-judge, and human review.
3. Cover DSPy, BootstrapFewShot, and GEPA using primary sources.
4. Provide cost and time formulas with clearly fictional examples.
5. Explain limitations, privacy, bias, leakage, versioning, overfitting, and
   the need for a holdout.
6. Separate sourced facts, project facts, and your inferences.

Required deliverable:
md/research/fable-references-prompt-optimization-research.md

Write only that file. Do not modify other files. Do not stage or commit.

At completion report:
- the deliverable path;
- a concise findings summary;
- the principal sources used;
- every file changed; and
- git status.
```

## Assignment Checklist

Every delegated assignment should state:

- **Role:** "You are the spawned subagent."
- **Execution ownership:** "Perform the work yourself."
- **No recursive delegation:** unless explicitly intended.
- **Objective:** one concrete outcome, not a broad topic alone.
- **Scope:** required questions and excluded work.
- **Inputs:** exact files, URLs, or other sources the agent may inspect.
- **Deliverable:** exact output format and path.
- **Write boundary:** files the agent may modify, or read-only status.
- **Security boundary:** data and identifiers that must remain private.
- **Validation:** checks or evidence required before completion.
- **Git boundary:** whether staging and commits are prohibited.
- **Completion report:** what the agent must return to the manager.

## Context Inheritance

When the subagent inherits the parent conversation, assume it can see prior
manager instructions. The assignment must override ambiguous inherited wording:

```text
The phrase "spawn a subagent" in the parent conversation was addressed to the
manager and has already been completed. You are that subagent. Do not delegate
again.
```

Use inherited context when the task depends on project history. Start without
inherited context when the task is fully self-contained and previous discussion
would create ambiguity or expose unnecessary private information.

## Monitoring And Correction

After spawning:

1. Record the agent identity and assignment.
2. Let the agent work without duplicating the same research locally.
3. Check progress only when needed; avoid repeated polling.
4. If the agent returns a plan instead of the artifact, correct it explicitly:

```text
You are the assigned executor. Perform the task now. Do not delegate. Create
the required file and return only after the deliverable is complete.
```

5. Review the returned file, sources, privacy boundary, and Git status before
accepting or committing it.
6. Close the subagent when its work is complete and no follow-up is needed.

## Choosing A Subagent Task

Good subagent work is concrete, bounded, independently verifiable, and does not
block an urgent next action. Suitable examples include source research,
documentation audits, focused test analysis, and a code change with a disjoint
file boundary.

Keep the work with the manager when it is the immediate critical-path action,
requires ongoing owner decisions, has an unclear security boundary, or is too
tightly coupled to concurrent changes for an independent agent to complete
safely.
