// Presentation only. Keep candidate facts in the importing document.
// Libertinus Serif ships with Typst; alternative fonts must be locally installed.
#let resume(name: none, contact: none, title: "Resume", font: "Libertinus Serif", body) = {
  set document(title: title, author: name)
  set page(
    paper: "us-letter",
    margin: (x: 0.5in, top: 0.32in, bottom: 0.32in),
  )
  set text(font: font, size: 9.1pt)
  set par(justify: true, leading: 0.44em)
  set list(spacing: 4.5pt)
  show link: it => text(fill: rgb("#17569b"), underline(it))

  align(center)[
    #text(size: 15pt, weight: "bold", name) \
    #v(1pt)
    #text(size: 8.5pt, fill: rgb("#333333"), contact)
  ]
  v(-3pt)
  body
}

#let section(title) = {
  v(3pt)
  text(weight: "bold", size: 9.8pt, fill: rgb("#111111"))[#upper(title)]
  v(-5pt)
  line(length: 100%, stroke: 0.5pt + rgb("#cccccc"))
  v(2pt)
}

#let entry(company, role, location, dates, body) = {
  grid(
    columns: (1fr, auto),
    [#strong(company) | #emph(role)], [#align(right)[#emph(location) | #strong(dates)]],
  )
  v(1pt)
  body
  v(2pt)
}
