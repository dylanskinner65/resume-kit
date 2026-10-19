#import "/templates/resume.typ": resume, section, entry
#show: resume.with(
  name: "Alex Morgan",
  title: "Alex Morgan — Customer Engineer",
  contact: [#link("mailto:alex@example.com")[alex\@example.com] | #link("https://example.com")[example.com]],
)

#section("Technical Skills")
*Languages:* TypeScript, Python, SQL \
*Agent Systems:* Agent SDK development, tool calling, RAG \
*Evaluation & Infrastructure:* Evaluation datasets, Redis, PostgreSQL, GitHub Actions

#section("Professional Experience")
#entry("Example Learning", "Engineer", "Remote", "Jan 2023 — Present", [
  - *Co-built a TypeScript agent SDK with one teammate* and migrated a lesson-planning workflow into production.
  - *Helped reduce average cost per completed run by 32%* for the lesson-planning workflow through model changes, comparing runs on the same evaluation dataset.
  - *Helped improve safety evaluation scores from 88% to 92%* on the same internal test set; helped reduce time to first token by *18%* on the same workload.
  - *Supported two internal engineering teams adopting the SDK* through developer documentation, technical sessions, and adoption PR reviews.
  - *Mentored a junior engineer* through pair programming and code reviews.
])

#section("Selected Project")
#link("https://example.com/projects/support-search")[*Support Search Demo*] — Built a TypeScript retrieval demo that searches a small public support-document collection and returns source-linked answers.

#section("Selected Talk")
#link("https://example.com/talks/agent-evaluation")[*Evaluating Agent Workflows*] — Developer meetup session on repeatable evaluation datasets and inspecting failures.

#section("Education")
#grid(
  columns: (1fr, auto),
  [*Example University* \ #emph[B.S. Computer Science]], [#align(right)[*May 2022*]],
)
