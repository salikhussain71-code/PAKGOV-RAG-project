# Grounded-answer evaluation

| | |
| --- | --- |
| Evaluator | `app/eval/evaluate_grounded_v1.py` |
| Version | `1.0.0` (`EVALUATOR_VERSION`) |
| Replaces | `app/eval/evaluate_grounded.py`, now labelled the previous evaluator |
| Dependencies | Python standard library only; no model, no network |

A change to the criteria, thresholds, alias table or output schema needs a new
version, so results from different versions are never compared as if they were
one measurement.

## Why the previous evaluator was replaced

Issue #1: the previous evaluator built each answer from the reference answer,
decided `grounded` by comparing retrieved filenames with the gold source (or the
word "Constitution"), cited the first result even when another result was the
match, and took the page from the reference when the chunk had none. Its result
says whether a filename matched, not whether any retrieved text supports an
answer.

## Previous evaluator (preserved)

| Artifact | Result |
| --- | --- |
| `data/interim/grounded_answers_50.jsonl` | 37 `grounded`, 13 `insufficient` |
| `evaluation/retrieval/grounded_metrics.json` | `grounded_cited` 37 of 50 (74%) |

Both files are unchanged and still pinned by a test (SHA-256 with line endings
normalised: `a2519970…b268` and `5b07c7f9…689b`). The 74% is an oracle
source-coverage count; do not report it as a grounding result. Running
`app/eval/evaluate_grounded.py` overwrites these files, so run it in a copy of the
repository. The revised evaluator never writes to these paths.

## Inputs

| Input | Default path | Read by | Fields used |
| --- | --- | --- | --- |
| Retrieval results | `data/interim/hybrid_rrf_results_50.jsonl` | `answer` | `id`, `question`, `lang`, `retrieved_chunk_ids`, `retrieved_sources`. The `gold_*` fields in the same file are ignored. |
| Processed chunks | `data/processed/chunks.jsonl` | `answer` | `chunk_id`, `text`, `source_file`, optional `page` |
| Reference QA | `data/eval/verified_qa_50.jsonl` | `score` only | `id`, `answer`, `source_file`, `page` |
| Document aliases | `evaluation/generation/document_aliases.json` | `score` | see below |
| Answer records | `data/interim/grounded_v1_answers_50.jsonl` | `score` | written by `answer` |

The processed chunks are not part of a fresh checkout; `answer` stops with a message
if the file is missing. Chunks written by `app/chunk.py` have no `page` field. An
empty file, a row without a required field, invalid JSON or a duplicate id also stops
the run with a message that names the file (and the line, for the first two JSON problems).

## Methodology

### 1. Answers and abstentions (`answer`)

The reference file is never opened in this phase. For each question the evaluator
takes the top 5 retrieved passages, each with its own source, page and text.

- Question terms are its words minus `STOPWORDS` (function words, the question-frame verbs
  say/state/provide/guarantee/grant, and "article"/"section"). Terms containing a digit
  (`9`, `19a`) are locators; Arabic-Indic digits are mapped to ASCII.
- Passage text is cut into sentences after removing `Page N of M` headers. Numbering on its
  own (`16.`, `1[25A.`) joins the sentence after it; numbering left at the end of a passage
  belongs to the next passage and is dropped.
- A candidate answer is one sentence, or that sentence plus the next one. When the question
  has a locator, the candidate must start at a sentence that opens with that number and
  contain every locator. Otherwise it starts at a sentence that contains a question term.
  Windows with fewer than 12 non-numeric words (headings, list entries) are skipped, so a
  long heading is answered together with the sentence after it.
- The chosen candidate matches the most distinct question terms; ties go to the
  higher-ranked passage, then the shorter window, then the earlier sentence.

Abstention rules, each recorded as `abstain_reason`:

| Reason | When |
| --- | --- |
| `empty_question` | no question term is left after removing stop words |
| `no_passage_text` | none of the top 5 passages has text in the chunks file |
| `locator_not_found` | the question has a locator and no sentence of any top-5 passage opens with it |
| `insufficient_support` | the best candidate matches fewer than 2 distinct question terms, or there is none |

### 2. Citations

An answer cites the passage its text came from: `chunk_id`, `rank`, `source`, `page`,
all from that chunk's own record (the source falls back to the retrieval row's
source). A missing source or page is stored as `"unknown"`. It is never filled from
the reference or from another passage.

### 3. Document aliases

`document_aliases.json` lists the names of each document under a canonical id
(`SRC-0001`…, as in `docs/source-registry.csv`). Names are compared after dropping
the directory and the `.pdf`/`.txt` extension, lowercasing, and removing every
character that is not a letter or digit. There is no substring or prefix matching,
so a name that is not listed is `unknown` rather than a match. The metrics list
`sources_not_in_alias_table`, from the retrieved passages and the reference file.

### 4. Evidence-support criteria

The support unit is one retrieved passage. Page and source are checked separately;
the reference set does not annotate articles or spans, so those are not evaluated.
A text *contains* another when at least 90% of the second text's words appear in the
first, in the same order (longest common subsequence over lower-cased, NFC-normalised
words; punctuation, markup, soft hyphens and line breaks are ignored). An answer is
*supported* when the passage it cites contains it. Evidence is *sufficient* for a
question when one of the top 5 passages contains the reference answer. For comparison,
the largest overlap between reference answers for different articles in the committed
set is 0.81 (Article 16 against Article 17), and a passage-sized text made of three
other articles' answers reaches 0.85.

### 5. Measures

Four measures, never combined. Each is a numerator and denominator in the metrics file.

| Measure | Counts | Over |
| --- | --- | --- |
| `answer_correctness` | answers that contain the reference answer (90%) and are at least 50% reference words | all questions; an abstention is not correct |
| `evidence_support` | answers contained in the retrieved passage they cite | answered questions |
| `citation_accuracy` | supported answers whose citation carries the source and page recorded for the passage, resolves to the reference document through the alias table, and has the reference page | answered questions; `unknown` is not accurate |
| `appropriate_abstention` | answered with sufficient evidence, or abstained without it | all questions |

The extractive baseline takes each answer from the passage it cites, so
`evidence_support` is 1.0 for it by construction. The measure matters for other
generators, and the previous evaluator's outputs (answers built from the reference)
fail it. `appropriate_abstention` judges the decision only: a system that always
answers scores the share of questions whose reference answer is in the top 5
(`reference_in_retrieved_passages`), so read it with the four decision counts. The
breakdown also reports how many answered questions cite a passage that contains the
reference answer (`answered_cited_passage_has_reference`), the abstain reasons,
`match`/`mismatch`/`unknown` for citation source and page, and the same measures per
language.

## Outputs

- `data/interim/grounded_v1_answers_50.jsonl`: answer, citation and the passages used,
  with the thresholds used for answering and the SHA-256 of the retrieval and chunk files.
- `data/interim/grounded_v1_scores_50.jsonl`: one record per question.
- `evaluation/generation/grounded_v1_metrics.json`: evaluator version, inputs with
  SHA-256, thresholds, definitions, measures, breakdown and `by_lang`.

Hashes are taken with CRLF read as LF. `score` refuses answers made by another version
or with other answer-phase thresholds. Outputs contain no timestamps and do not depend
on `PYTHONHASHSEED`. `.gitignore` excludes `*.jsonl`, so the two `data/interim` files are
not tracked unless added with `git add -f`, as the previous evaluator's were; the metrics
file is tracked normally.

## Results

None are published with this version. The processed chunks are not in the repository,
so the evaluator has not been run on the 50 questions. After regenerating them, run
`answer` and `score`, then record the `measures` block here with the version and input
hashes from the metrics file. These results are not comparable with 37/50.

## Limitations

- The answerer is a lexical baseline. It matches question words against passage text,
  so Urdu-script questions match only on digits and Latin words and usually abstain;
  their scores describe this answerer, not the retriever. Read `by_lang`.
- With a number in the question, only a sentence that opens with that number can start
  an answer. A chunk that cuts a provision off from its number cannot answer it, and a
  numbered table can match like a provision.
- Headings and tables of contents can match question terms and be returned as answers.
  They are scored as incorrect, and as inappropriate answers when no top-5 passage
  contains the reference answer.
- Without a `page` on the chunks every citation page is `unknown`, so `citation_accuracy`
  stays 0 while `answered_citation_source` in the breakdown still shows document-level results.
- Words split by line-end hyphenation in the extracted text lower coverage; for a 14-word
  reference two such splits already fall below 90%.
- The 50 questions have 16 distinct reference answers (the same articles asked in
  English, Urdu and mixed form), so results are correlated across languages. Reference
  pages differ between rows for the same article (Article 9: page 12 in `en_01`, 20 in
  `en_09`; Article 19A: 18 in `mix_01`, 31 in `en_06`), and `ur_01` is a short paraphrase
  rather than a quotation, so it may not reach 90% coverage in the right passage.
- Thresholds are fixed defaults, not validated against human judgement. Evidence
  sufficiency is a lower bound when retrieved passages have no text.

## Running

```sh
python app/eval/evaluate_grounded_v1.py answer
python app/eval/evaluate_grounded_v1.py score
python -m unittest discover -s tests -v
```

The tests are offline. They run both phases on temporary fixtures that reproduce the
failure cases of issue #1, and check that the previous outputs are unchanged.
