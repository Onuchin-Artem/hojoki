// Reusable content components for the print PDF.

#import "typography.typ": *

// Grey italic credit line — after a verse or at the end of a poem (STYLE.md).
#let credit(body) = {
  set text(font: sans, size: 9.5pt, style: "italic", fill: grey)
  body
}
