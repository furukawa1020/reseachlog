# Research Infrastructure Setup

- Period: 2026-04-21 to 2026-04-21
- Source logs: 1
- Themes: H1, H2, H3

## Main Focus

- Bootstrapping the research log infrastructure and fixing the 2026 research focus

## Current Focus

- How should the repository be structured so that daily work can be reused for presentations and papers?
- What should be fixed first so that the 2026 research plan and day-to-day work stay aligned?

## What We Did

- Rebased the repository structure on `研究計画本番のコピー-2.pdf`
- Organized working directories and READMEs for H1, H2, and H3
- Added a daily logging template and a slide-outline generation script
- Fixed the 2026 focus as `H1 meta-review / H2 WESAD analysis / n=20-30 follow-up / connection to Lazarus theory`
- Updated the H2 dataset registry so that WESAD is the primary dataset and CASE is treated as an extension

## Key Takeaways

- A daily structure with `question / actions / findings / slide notes / next step` is enough to support both research logging and presentation preparation
- For 2026, the project becomes stronger if WESAD remains the analytical core and theory plus follow-up study design are built around it
- CASE and other datasets are still valuable, but they should be handled as expansion targets rather than replacing the main axis

## Slide-Ready Claims

- Background: After the rejection from Mitou, the research still needs a workflow that converts ongoing work into presentable materials
- Method: The repository was rebuilt around H1, H2, H3 and the 2026 research plan, with a path from daily logs to slide outlines
- Result: H2 is now organized around WESAD as the main dataset, while CASE and other datasets remain available for extension
- Claim: In an early-stage research project, fixing the winning axis for the year matters more than increasing the amount of work

## Blockers

- The definition of `mismatch` in H2 is still not fixed as a concise statement
- The visual framing for the connection to Lazarus theory still needs work

## Next Steps

- Fix four review axes for H1
- Write a three-line definition of `mismatch` for H2
- Fill the basic WESAD information in the dataset registry
- Summarize the link to Lazarus theory in a one-page note

## Sources

- 研究計画本番のコピー-2.pdf
- README.md
- docs/research-plan.md
- docs/workflow.md
- research/H2_dataset_analysis/dataset_registry.md
- scripts/new_daily_log.py
- scripts/build_slide_outline.py
