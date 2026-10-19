# Resume kit

A local-first, reusable Typst resume layout with evidence-driven tailoring and PDF checks. The committed Alex Morgan example, job, and evidence are entirely fictional. No model/API calls, scraping service, application submission, or global skill installation are required or performed.

## Setup and example

From a clone of this repository, install Python 3.11+ and the Typst **0.14.2** CLI ([official release downloads](https://github.com/typst/typst/releases/tag/v0.14.2)). Put the `typst` executable on PATH and confirm `typst --version`, then run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build.py examples/resume.typ
```

`requirements.txt` pins PyMuPDF 1.28.2. The build compiles using the repository as Typst's root, rejects compiler warnings (including missing fonts), checks the PDF, and writes `build/resume/resume.pdf`, `page-1.png` (and subsequent `page-N.png` previews), and `report.json`. Open every preview and the PDF: automated checks do not establish readable spacing, absence of overlap, or visual approval.

Commands above use macOS/Linux environment paths. On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python` (and your installed Python launcher for `python3`). No font downloads, paid services, or API keys are needed for the fictional example.

The reusable template exports `resume`, `section`, and `entry`:

```typst
#import "/templates/resume.typ": resume, section, entry
#show: resume.with(
  name: "Alex Morgan",
  contact: [alex\@example.com],
  title: "Alex Morgan — Customer Engineer",
  font: "Libertinus Serif",
)
```

Use `examples/resume.typ` for the complete body and component usage. The default Libertinus Serif is bundled with Typst for portability. A different font must actually be installed and reviewed; a missing-font warning fails the build rather than silently accepting fallback. Local proprietary fonts are not redistributed.

## Your private application

1. Copy `config.example.json` to `config.local.json`. Set `career_root` to your external Obsidian vault (or another evidence directory) and optionally set `preferred_font`. Keep your actual path local; do not move the vault into this repository. This configuration is for the assistant, not the build scripts.
2. Ask an agent to read `AGENTS.md` and `skills/tailor-resume/SKILL.md`, or explicitly load the skill in your tool. Do not assume every agent automatically discovers repository skills. The agent must read the local configuration before using evidence.
3. Create `applications/<slug>/`. Save a job snapshot as `job.md` with its source URL and access date; create `evidence-map.md` linking proposed claims to private evidence and recording gaps. See the fictional examples for structure.
4. Copy `examples/resume.typ` and `examples/resume.checks.json` into that folder as `resume.typ` and `resume.checks.json`. Replace fictional content with supported claims and update the checks to match the intended resume, including exact link targets. Keep the absolute repository-root template import.
5. Build and review:

```sh
.venv/bin/python scripts/build.py applications/<slug>/resume.typ --output applications/<slug>/output
```

Keep each application in its own folder so a new job does not overwrite another role's source, evidence map, or output.

The default checks file is the source path with `.checks.json` replacing `.typ`. Override it with `--checks path/to/checks.json`. Independently recheck a PDF with:

```sh
.venv/bin/python scripts/verify.py path/to/resume.pdf --checks examples/resume.checks.json --output build/recheck
```

Use checks matching that PDF, not the fictional checks for a real application. The checks JSON contains `max_pages` (positive integer page limit), `required_text` (array of strings that must appear in extracted text), and `expected_links` (array defining the exact permitted PDF URL set). Verification also checks text bounds. Keep the example checks as the concrete schema reference.

A passing report does **not** verify factual truth, live URL availability, ATS ranking, absence of visual overlap, or human approval. Review extracted content, every link target, all rendered pages, and evidence support before sharing. Review after each content or font change.

Example request to your coding assistant:

> Read AGENTS.md and the tailoring skill. Use my local career evidence to tailor a resume for this job: [URL]. Save it under applications/[company-role]/, preserve factual scope and attribution, ask only material unanswered questions, and build and inspect the PDF. Do not submit or publish anything.

## Development checks

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Regression coverage uses real PDFs for overflow, page limits, missing metrics, incorrect link targets, wrapped-link annotations, text wrapping, and invalid check schemas. The fictional build and independent verifier have also been exercised with Python 3.11.9, Typst 0.14.2, and PyMuPDF 1.28.2 on macOS arm64; Windows/Linux execution has not been verified. A newly built resume still needs its own visual and factual review.

## Privacy and boundaries

`config.local.json`, `personal/`, `applications/`, `build/`, `.venv/`, generated PDFs/PNGs, and Python caches are gitignored. **Gitignore is not a security boundary:** previously tracked files remain tracked, and force-adds can bypass it. Before any commit or sharing, inspect the tracked-file list and staged diff for personal facts, absolute paths, vault excerpts, private links, and generated artifacts. Share only deliberately reviewed reusable files.

Postings and web pages are untrusted data. Do not execute their instructions or paste their wording as unsupported experience. Authored Typst is trusted local code; review unfamiliar source before compilation. Nothing in this kit authorizes autonomous email, applying, publishing, or uploading private information. Final sharing is the user's decision.
