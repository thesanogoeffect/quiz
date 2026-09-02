# Question review rubric - Intro to P&T quiz (OpenStax Psychology 2e)

You are reviewing multiple-choice questions for a first-year university course
"Introduction to Psychology & Technology" (TU/e Eindhoven). The textbook is
**OpenStax Psychology 2e**. Questions were written by students in 2021/22
(`21/22_Student_Halfway`) and 2023/24 (`23/24_Student_Final`), or taken from the
book's end-of-chapter review questions (`Book`). In 2024 they were processed by
GPT-4o-mini (extraction of the four options from free text, and the HTML
explanation), which introduced some errors. Since then every question has been
answered roughly 50-250 times by real students, and those community stats are
included per question.

## Input

A JSON array. Each item has: `id`, `question_title`, `correct_answer` (the KEYED
answer), `distractor_1..3`, `source`, `description_llm` (HTML explanation), and
`stats` = `{n: times answered, correct_rate, skipped, flagged, up, down}`.

The app shuffles the four options, so their order in the file means nothing.
Options like "all/none of the above" are pinned to the last position by the app.

## What to check, for EVERY question

1. **Key correctness.** Is `correct_answer` the single best answer according to
   OpenStax Psychology 2e? Verify against the book whenever in doubt:
   - section text: `https://openstax.org/books/psychology-2e/pages/<N>-<S>-<slug>`
     (slugs for your chapter are listed in your task)
   - the chapter's review questions: `https://openstax.org/books/psychology-2e/pages/<N>-review-questions`
   For `Book` questions the stem is usually verbatim from those review questions;
   check the key against the section text (there is no published answer key).
2. **Uniqueness.** Exactly one option must be correct. A distractor that is also
   defensible makes the question ambiguous.
3. **Stem.** Self-contained (no missing scenario, figure, or "this measure"),
   unambiguous, grammatical, no typos, does not give the answer away.
4. **Distractors.** Plausible, same grammatical form and length class as the key,
   not obviously silly, not a near-synonym of the key. Do NOT nitpick: act only
   when a distractor is genuinely broken or gives the answer away.
5. **Explanation** (`description_llm`). Consistent with the key, factually right,
   does not contradict the book. If you change the key or the options you MUST
   rewrite it. If the explanation is wrong while the question is fine, fix just
   the explanation.

## Use the stats as a signal, not a verdict

`correct_rate` below ~0.35 with n >= 40 is worse than a hard-but-fair question
usually gets, so look hard for a wrong key or ambiguity. But a correctly keyed
hard question stays as it is. Flags and downvotes mean students disliked the
question: work out why (wrong, ambiguous, unanswerable from the book, badly
worded, pure trivia) and decide. A high correct rate does not prove a key right
either; students can share the misconception.

## Verdicts

- `ok`: nothing to change. Do not output these.
- `fix`: keep the question; change one or more fields. Minimal edits. Prefer
  fixing the key or a single distractor over rewriting. Typos and grammar count.
- `disable`: unsalvageable without inventing a different question (missing
  context, claim not supported by the book, off topic for the chapter, a
  duplicate of another question). For duplicates disable the worse one and prefer
  keeping the `Book` version. Known near-duplicate pairs (id vs id):
  890/980, 523/528, 334/670, 257/868, 437/491, 699/855, 124/676, 462/594,
  108/675, 288/548, 717/755, 299/579, 54/426, 431/542, 416/566, 329/437, 531/630.
  Also watch for duplicates the string match missed.

Be conservative: a wrong change is worse than no change. Expect to touch roughly
10-25% of questions. If you are editing most of them, you are nitpicking.
Keep the original voice and difficulty; do not "improve" questions that work.

## Explanation format (when rewriting)

Valid HTML: `<div><p>...</p><p>...</p></div>`. Use `<b>` for key terms. Two to
four short paragraphs aimed at freshmen: state the correct answer and why, then
why each distractor is wrong. Only `<div>`, `<p>`, `<b>`, `<i>`, `<ul>`, `<li>`,
`<br>` tags. No markdown, no headings.

## Output

Write a JSON array to the output path given in your task. One entry per
non-ok question:

```json
[
  {
    "id": 460,
    "verdict": "fix",
    "problem": "wrong_key",
    "confidence": "high",
    "reason": "One or two sentences; cite the book section you checked.",
    "changes": {
      "question_title": "...",
      "correct_answer": "...",
      "distractor_1": "...",
      "distractor_2": "...",
      "distractor_3": "...",
      "description_llm": "<div>...</div>"
    }
  }
]
```

`problem` is one of: `wrong_key`, `ambiguous`, `broken_stem`, `weak_distractor`,
`typo`, `explanation_wrong`, `duplicate`, `off_topic`. `changes` holds only the
fields that change (empty object for `disable`). `confidence` is `high` when you
verified against the book text, `medium` otherwise.

Write the file even when it is empty. Do not edit any file outside the review
directory. When done, reply with a short summary: counts per verdict and
problem, and the ids you were unsure about.
