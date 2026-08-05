# LP-4.2 Publication Record

## Status

Published and closed, owner-reported 2026-08-05.

## Publication

- Work item: LP-4.2 RunPod Qwen hardware/context follow-up LinkedIn article.
- Previous article: `md/handoffs/reports/LP-4.1-article-draft-v2.md`.
- Planning handoff:
  `md/handoffs/LP-4.2-runpod-qwen-context-followup-linkedin-article.md`.
- Accepted technical evidence:
  `md/handoffs/reports/WP-5.2C1-completion-report.md`.
- Posted source package:
  `md/20260805_linkedin-runpod-qwen-followup-article/`.
- External LinkedIn article URL: not supplied.

## Retained Artifacts

The posted source package contains:

- `LP-4.2-runpod-qwen-followup-article-draft-v2.md`: long-form article source;
- `article feed.txt`: LinkedIn feed copy;
- `lp42-reliability-progression.png` and `.svg`: reliability chart;
- `lp42-wall-time.png` and `.svg`: wall-time chart; and
- `Gemini_Generated_Image_1f837y1f837y1f83.png`: published cover-image asset.

## Evidence Review

The retained article reports the accepted study boundaries and headline results:

- local Qwen 8K: 84/120 schema-valid outputs;
- remote Qwen 8K repeatability: 89/120 on both runs;
- remote Qwen 262K maximum-context reference: 119/120;
- hosted Gemini control: 112/120;
- remote wall times of 131 seconds, 129 seconds, and 169 seconds;
- matched 110-case semantic means of 3.830/4 for Qwen and 3.892/4 for Gemini;
- peak sampled Qwen memory of 11,896 MiB at maximum context; and
- the explicit limitation that 262K is a reference endpoint, not a demonstrated
  minimum context requirement.

These values reconcile with the accepted WP-5.2C1 completion report. The article
also preserves the development-corpus, fixed-judge, environment-comparison, and
repeatability caveats needed to avoid presenting the study as a general hardware
or provider benchmark.

## Process Note

The owner completed the analysis, editorial decisions, article drafting, and
publication outside the repository's planned gated handoff sequence. The posted
source package supplied by the owner is therefore the authoritative publication
artifact. The unexecuted handoff remains tracked as process history.

## Repository Boundary

Only publication source, visual assets, and project documentation are retained.
No frozen database, private transcript, benchmark package, credential, access
token, private provider identifier, or private absolute path is included in this
publication record or the retained text sources.
