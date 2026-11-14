"""Independent grounded-answer evaluation (evaluator v1).

The previous evaluator, app/eval/evaluate_grounded.py, built the answers it scored
from the reference answers (issue #1), so its 37/50 result is not evidence of
grounding. This evaluator keeps answering and scoring apart. Run both phases from
the repository root:

    python app/eval/evaluate_grounded_v1.py answer
        retrieval results + processed chunks -> answers, abstentions, citations.
        Uses only the question and the retrieved passages; never opens the
        reference file.
    python app/eval/evaluate_grounded_v1.py score
        answers + reference QA -> four separate measures: answer correctness,
        evidence support, citation accuracy and appropriate abstention.

Version, inputs, methodology and limits: docs/grounded-evaluation.md.
Any change to the criteria below needs a new EVALUATOR_VERSION.
"""
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

EVALUATOR_NAME = "pakgov-grounded-eval"
EVALUATOR_VERSION = "1.0.0"
UNKNOWN = "unknown"

# Evaluation contract (explained in docs/grounded-evaluation.md).
TOP_K = 5                    # retrieved passages the answerer and the scorer use
WINDOW_SENTENCES = 2         # an answer is one sentence or two consecutive sentences
MIN_ANSWER_WORDS = 12        # shorter windows (headings, list entries) are not evidence
MIN_MATCHED_TERMS = 2        # distinct question terms an answer window must contain
MIN_COVERAGE = 0.9           # share of a text's words that another text must contain, in order, to contain it
ANSWER_PRECISION = 0.5       # share of a correct answer's words that must come from the reference answer
STOPWORDS = frozenset(
    "a an the of in on at to for from by with and or nor but if as is are was were be been "
    "being do does did what which who whom whose how when where why that this these those "
    "it its into than then there their they about regarding say says said state states "
    "stated provide provides provided guarantee guarantees grant grants article articles "
    "section sections".split()
)

ROOT = Path(__file__).resolve().parents[2]
ALIASES_PATH = ROOT / "evaluation" / "generation" / "document_aliases.json"
RETRIEVAL_PATH = Path("data/interim/hybrid_rrf_results_50.jsonl")
CHUNKS_PATH = Path("data/processed/chunks.jsonl")
REFERENCE_PATH = Path("data/eval/verified_qa_50.jsonl")
ANSWERS_PATH = Path("data/interim/grounded_v1_answers_50.jsonl")
SCORES_PATH = Path("data/interim/grounded_v1_scores_50.jsonl")
METRICS_PATH = Path("evaluation/generation/grounded_v1_metrics.json")

# Arabic-Indic (U+0660..) and Eastern Arabic-Indic (U+06F0..) digits map to ASCII digits.
_ARABIC_DIGITS = {base + i: str(i) for base in (0x0660, 0x06F0) for i in range(10)}
_PAGE_HEADER = re.compile(r"\bpage\s+\d+\s+of\s+\d+\b", re.IGNORECASE)
# A sentence ends at . ! ? or the Urdu full stop (\u06d4) and question mark (\u061f), optionally followed by ] or ).
_SENTENCE_END = re.compile(r"(?:(?<=[.!?\u06d4\u061f])|(?<=[.!?\u06d4\u061f][\])]))\s+")


# --- text helpers -----------------------------------------------------------

def tokenize(text):
    text = unicodedata.normalize("NFC", text if isinstance(text, str) else "")
    return re.findall(r"[^\W_]+", text.replace("\u00ad", "").translate(_ARABIC_DIGITS).casefold())


def is_numbering(part):
    """A fragment that is only numbering ("16.", "1[25A."): it belongs to the sentence after it."""
    words = tokenize(part)
    return 0 < len(words) <= 2 and all(any(c.isdigit() for c in w) for w in words)


def split_sentences(text):
    text = unicodedata.normalize("NFC", text if isinstance(text, str) else "")
    text = re.sub(r"\s+", " ", _PAGE_HEADER.sub(" ", text)).strip()
    sentences, carry = [], ""
    for part in _SENTENCE_END.split(text):
        part = (carry + " " + part).strip()
        if not part or is_numbering(part):
            carry = part
        else:
            sentences.append(part)
            carry = ""
    return sentences  # numbering left at the end belongs to the next passage and is dropped


def lcs_length(a, b):
    previous = [0] * (len(b) + 1)
    for x in a:
        current = [0]
        for j, y in enumerate(b, 1):
            current.append(previous[j - 1] + 1 if x == y else max(previous[j], current[j - 1]))
        previous = current
    return previous[-1]


def coverage(needle, haystack):
    """Share of the words in needle found in haystack, in the same order."""
    return lcs_length(needle, haystack) / len(needle) if needle else 0.0


def clean_page(value):
    if isinstance(value, bool):
        return UNKNOWN
    if isinstance(value, int) and value >= 1:
        return value
    if isinstance(value, str) and value.strip().isdecimal() and int(value) >= 1:
        return int(value)
    return UNKNOWN


# --- phase 1: answers from the question and the retrieved passages only ------

def build_passages(row, chunks):
    """Top-k retrieved passages with their own metadata. Nothing comes from the reference."""
    ids = row.get("retrieved_chunk_ids") or []
    sources = row.get("retrieved_sources") or []
    passages = []
    for rank, chunk_id in enumerate(ids[:TOP_K], 1):
        chunk = chunks.get(chunk_id) or {}
        retrieved_source = sources[rank - 1] if rank <= len(sources) else None
        text = chunk.get("text")
        passages.append({
            "rank": rank,
            "chunk_id": chunk_id,
            "source": chunk.get("source_file") or retrieved_source or UNKNOWN,
            "page": clean_page(chunk.get("page")),
            "text": text if isinstance(text, str) and text.strip() else None,
        })
    return passages


def _abstain(reason):
    return {"status": "abstained", "answer": "", "abstain_reason": reason,
            "citation": None, "matched_terms": []}


def starts_with_number(words, locators):
    """True when a sentence opens with one of the locators as its numbering ("16.", "1[25A.")."""
    return bool(words) and (words[0] in locators
                            or (len(words) > 1 and words[0].isdigit() and words[1] in locators))


def answer_question(question, passages):
    """Extract an answer from the passages, or abstain. Takes no reference data."""
    terms = list(dict.fromkeys(t for t in tokenize(question) if t not in STOPWORDS))
    if not terms:
        return _abstain("empty_question")
    usable = [p for p in passages if isinstance(p.get("text"), str) and p["text"].strip()]
    if not usable:
        return _abstain("no_passage_text")
    term_set = set(terms)
    locators = [t for t in terms if any(c.isdigit() for c in t)]  # e.g. "9", "19a"

    best, numbered = None, False
    for passage in usable:
        sentences = split_sentences(passage["text"])
        for i, first in enumerate(sentences):
            first_words = tokenize(first)
            if locators and not starts_with_number(first_words, locators):
                continue  # with a number in the question, an answer starts at that number
            if term_set.isdisjoint(first_words):
                continue  # otherwise a window starts at a sentence that matches the question
            numbered = True
            for size in range(1, WINDOW_SENTENCES + 1):
                window = sentences[i:i + size]
                if len(window) < size:
                    break
                words = tokenize(" ".join(window))
                word_set = set(words)
                if any(t not in word_set for t in locators):
                    continue
                if sum(1 for w in words if not w.isdigit()) < MIN_ANSWER_WORDS:
                    continue
                matched = [t for t in terms if t in word_set]
                key = (len(matched), -passage["rank"], -len(words), -i)
                if best is None or key > best[0]:
                    best = (key, " ".join(window), passage, matched)
    if locators and not numbered:
        return _abstain("locator_not_found")
    if best is None or len(best[3]) < MIN_MATCHED_TERMS:
        return _abstain("insufficient_support")
    _, answer, passage, matched = best
    return {
        "status": "answered",
        "answer": answer,
        "abstain_reason": None,
        "citation": {k: passage[k] for k in ("chunk_id", "rank", "source", "page")},
        "matched_terms": matched,
    }


def answer_config():
    """What shapes the answers. It is stored with them so `score` can refuse a mismatch."""
    return {"top_k": TOP_K, "window_sentences": WINDOW_SENTENCES,
            "min_answer_words": MIN_ANSWER_WORDS, "min_matched_terms": MIN_MATCHED_TERMS,
            "stopwords_sha256": hashlib.sha256(" ".join(sorted(STOPWORDS)).encode("utf-8")).hexdigest()}


# --- document aliases ---------------------------------------------------------

def normalize_name(name):
    stem = str(name or "").replace("\\", "/").rsplit("/", 1)[-1]
    stem = re.sub(r"\.(pdf|txt)$", "", stem, flags=re.IGNORECASE)
    return "".join(c for c in stem.casefold() if c.isalnum())


def load_aliases(path=ALIASES_PATH):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    table = {}
    for doc_id, document in data["documents"].items():
        for alias in document["aliases"]:
            if table.setdefault(normalize_name(alias), doc_id) != doc_id:
                raise ValueError(f"alias {alias!r} is listed under two documents")
    return table


def resolve_document(name, table):
    """Canonical document id, or None when the name is missing or not a listed alias."""
    if not name or name == UNKNOWN:
        return None
    return table.get(normalize_name(name))


# --- phase 2: scoring against the reference ----------------------------------

def score_answer(record, reference, table):
    ref_words = tokenize(reference["answer"])
    passages = {p["chunk_id"]: p for p in record["passages"]}
    holders = [p["rank"] for p in record["passages"]
               if coverage(ref_words, tokenize(p.get("text"))) >= MIN_COVERAGE]
    score = {
        "id": record["id"], "lang": record.get("lang") or UNKNOWN, "status": record["status"],
        "evidence_sufficient": bool(holders), "reference_passage_ranks": holders,
        "abstention_appropriate": bool(holders) == (record["status"] == "answered"),
    }
    if record["status"] != "answered":
        score.update(answer_correct=False, answer_recall=None, answer_precision=None,
                     evidence_supported=None, cited_passage_has_reference=None,
                     citation_recorded=None, citation_source=None, citation_page=None,
                     citation_correct=None)
        return score

    answer_words = tokenize(record.get("answer"))
    shared = lcs_length(ref_words, answer_words)
    recall = shared / len(ref_words) if ref_words else 0.0
    precision = shared / len(answer_words) if answer_words else 0.0
    score["answer_recall"], score["answer_precision"] = round(recall, 4), round(precision, 4)
    score["answer_correct"] = recall >= MIN_COVERAGE and precision >= ANSWER_PRECISION

    citation = record.get("citation") or {}
    cited = passages.get(citation.get("chunk_id"))
    cited_words = tokenize(cited.get("text")) if cited else []
    score["evidence_supported"] = bool(cited) and coverage(answer_words, cited_words) >= MIN_COVERAGE
    score["cited_passage_has_reference"] = coverage(ref_words, cited_words) >= MIN_COVERAGE
    score["citation_recorded"] = bool(
        cited
        and citation.get("source") == cited.get("source")
        and clean_page(citation.get("page")) == clean_page(cited.get("page"))
    )
    cited_doc = resolve_document(citation.get("source"), table)
    ref_doc = resolve_document(reference.get("source_file"), table)
    score["citation_source"] = (
        UNKNOWN if cited_doc is None or ref_doc is None
        else "match" if cited_doc == ref_doc else "mismatch")
    cited_page, ref_page = clean_page(citation.get("page")), clean_page(reference.get("page"))
    score["citation_page"] = (
        UNKNOWN if UNKNOWN in (cited_page, ref_page)
        else "match" if cited_page == ref_page else "mismatch")
    score["citation_correct"] = (score["evidence_supported"] and score["citation_recorded"]
                                 and score["citation_source"] == "match"
                                 and score["citation_page"] == "match")
    return score


def measures(rows):
    answered = [r for r in rows if r["status"] == "answered"]

    def ratio(count, total):
        return {"value": round(count / total, 4) if total else None,
                "numerator": count, "denominator": total}

    return {
        "answer_correctness": ratio(sum(r["answer_correct"] for r in rows), len(rows)),
        "evidence_support": ratio(sum(r["evidence_supported"] for r in answered), len(answered)),
        "citation_accuracy": ratio(sum(r["citation_correct"] for r in answered), len(answered)),
        "appropriate_abstention": ratio(sum(r["abstention_appropriate"] for r in rows), len(rows)),
    }


def definitions():
    cover, prec = f"{MIN_COVERAGE:.0%}", f"{ANSWER_PRECISION:.0%}"
    return {
        "answer_correctness": (
            f"Answers containing at least {cover} of the reference answer's words in order, with at least "
            f"{prec} of the answer's words from it, over all questions. An abstention is not a correct answer."),
        "evidence_support": (
            f"Answered questions whose answer is contained (at least {cover} of its words, in order) in the "
            "retrieved passage it cites, over answered questions."),
        "citation_accuracy": (
            "Answered questions whose answer is supported by the cited passage, whose citation carries the "
            "source and page recorded for that passage, whose source resolves to the reference document "
            "through the alias table, and whose page equals the reference page, over answered questions. "
            "An unknown source or page is not accurate."),
        "appropriate_abstention": (
            f"Questions where the system answered and some top-{TOP_K} passage contains the reference answer, "
            "or abstained and none does, over all questions."),
    }


def summarize(rows, records):
    answered = [r for r in rows if r["status"] == "answered"]
    abstained = [r for r in rows if r["status"] != "answered"]
    return {
        "questions": len(rows),
        "answered": len(answered),
        "abstained": len(abstained),
        "measures": measures(rows),
        "breakdown": {
            "abstain_reasons": dict(sorted(Counter(
                r["abstain_reason"] for r in records if r["status"] == "abstained").items())),
            "reference_in_retrieved_passages": sum(r["evidence_sufficient"] for r in rows),
            "decisions": {
                "answered_with_evidence": sum(r["evidence_sufficient"] for r in answered),
                "answered_without_evidence": sum(not r["evidence_sufficient"] for r in answered),
                "abstained_with_evidence": sum(r["evidence_sufficient"] for r in abstained),
                "abstained_without_evidence": sum(not r["evidence_sufficient"] for r in abstained),
            },
            "answered_cited_passage_has_reference": sum(r["cited_passage_has_reference"] for r in answered),
            "answered_citation_source": dict(Counter(r["citation_source"] for r in answered)),
            "answered_citation_page": dict(Counter(r["citation_page"] for r in answered)),
            "retrieved_passages_without_text": sum(
                1 for rec in records for p in rec["passages"] if not p.get("text")),
        },
        "by_lang": {
            lang: {"questions": sum(r["lang"] == lang for r in rows),
                   "measures": measures([r for r in rows if r["lang"] == lang])}
            for lang in sorted({r["lang"] for r in rows})
        },
    }


# --- input/output ---------------------------------------------------------------

def read_jsonl(path, required=()):
    path = Path(path)
    if not path.is_file():
        sys.exit(f"error: {path} not found")
    rows = []
    with path.open(encoding="utf-8-sig") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError as error:
                sys.exit(f"error: {path}:{number}: invalid JSON ({error})")
            missing = [k for k in required if not isinstance(row, dict) or k not in row]
            if missing:
                sys.exit(f"error: {path}:{number}: missing {', '.join(missing)}")
            rows.append(row)
    if not rows:
        sys.exit(f"error: {path} has no records")
    return rows


def index_by(rows, key, path):
    index = {}
    for row in rows:
        if row[key] in index:
            sys.exit(f"error: duplicate {key} {row[key]!r} in {path}")
        index[row[key]] = row
    return index


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def file_info(path, shown=None, **extra):
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")  # same hash for LF and CRLF checkouts
    return {"path": Path(shown or path).as_posix(), "sha256": hashlib.sha256(data).hexdigest(), **extra}


def run_answer():
    if not CHUNKS_PATH.is_file():
        sys.exit(
            f"error: {CHUNKS_PATH} not found. The processed chunks are not part of a fresh "
            "checkout; regenerate them with app/chunk.py (needs the PDFs in data/raw) or "
            "place the file there.")
    rows = read_jsonl(RETRIEVAL_PATH, ("id",))
    index_by(rows, "id", RETRIEVAL_PATH)
    chunks = index_by(read_jsonl(CHUNKS_PATH, ("chunk_id",)), "chunk_id", CHUNKS_PATH)
    generator = {
        "name": "extractive-lexical", "evaluator": EVALUATOR_NAME, "version": EVALUATOR_VERSION,
        "config": answer_config(),
        "retrieval": file_info(RETRIEVAL_PATH, records=len(rows)),
        "chunks": file_info(CHUNKS_PATH, records=len(chunks)),
    }
    records = []
    for row in rows:  # reads id, lang, question and the retrieved ids/sources; never the gold_* fields
        question = row.get("question") or ""
        passages = build_passages(row, chunks)
        records.append({"id": row["id"], "lang": row.get("lang") or UNKNOWN, "question": question,
                        **answer_question(question, passages), "passages": passages,
                        "generator": generator})
    write_jsonl(ANSWERS_PATH, records)
    reasons = Counter(r["abstain_reason"] for r in records if r["status"] == "abstained")
    missing = sum(1 for r in records for p in r["passages"] if not p["text"])
    print(f"{EVALUATOR_NAME} {EVALUATOR_VERSION}: {len(records)} questions, "
          f"{sum(r['status'] == 'answered' for r in records)} answered, "
          f"{sum(reasons.values())} abstained {dict(sorted(reasons.items()))}")
    if missing:
        print(f"warning: {missing} retrieved passages have no text in {CHUNKS_PATH}; "
              "evidence found there is a lower bound")
    print(f"Saved: {ANSWERS_PATH}")


def run_score():
    records = read_jsonl(ANSWERS_PATH, ("id", "status", "passages"))
    index_by(records, "id", ANSWERS_PATH)
    references = index_by(read_jsonl(REFERENCE_PATH, ("id", "answer")), "id", REFERENCE_PATH)
    ids = {r["id"] for r in records}
    if ids != set(references):
        sys.exit("error: answer ids and reference ids differ: "
                 f"only in answers {sorted(ids - set(references))}, "
                 f"only in reference {sorted(set(references) - ids)}")
    generators = {json.dumps(r.get("generator"), sort_keys=True) for r in records}
    if len(generators) != 1:
        sys.exit("error: answers come from more than one generator or input set")
    generator = json.loads(next(iter(generators))) or {}
    if generator.get("version") != EVALUATOR_VERSION or generator.get("config") != answer_config():
        sys.exit("error: the answers were made with a different version or configuration; "
                 "run `answer` again")
    table = load_aliases()
    rows = [score_answer(r, references[r["id"]], table) for r in records]
    names = {p["source"] for r in records for p in r["passages"]}
    names |= {q.get("source_file") for q in references.values()}
    unresolved = sorted(n for n in names if n and n != UNKNOWN and resolve_document(n, table) is None)
    write_jsonl(SCORES_PATH, rows)
    result = {
        "evaluator": {"name": EVALUATOR_NAME, "version": EVALUATOR_VERSION,
                      "label": "revised evaluator; not comparable with the previous evaluator's 37/50"},
        "inputs": {
            "answers": file_info(ANSWERS_PATH, records=len(records)),
            "reference": file_info(REFERENCE_PATH, records=len(references)),
            "document_aliases": file_info(ALIASES_PATH, shown=ALIASES_PATH.relative_to(ROOT)),
            "generator": generator,
        },
        "config": {**generator["config"], "min_coverage": MIN_COVERAGE,
                   "answer_precision": ANSWER_PRECISION},
        "definitions": definitions(),
        **summarize(rows, records),
        "sources_not_in_alias_table": unresolved,
    }
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with METRICS_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"{EVALUATOR_NAME} {EVALUATOR_VERSION} on {result['questions']} questions "
          f"({result['answered']} answered, {result['abstained']} abstained)")
    for name, m in result["measures"].items():
        value = "n/a" if m["value"] is None else f"{m['value']:.3f}"
        print(f"  {name:<24} {value}  ({m['numerator']}/{m['denominator']})")
    print("Not comparable with the previous evaluator's 37/50 (see docs/grounded-evaluation.md).")
    print(f"Saved: {SCORES_PATH}\nSaved: {METRICS_PATH}")


def main(argv):
    if len(argv) != 2 or argv[1] not in ("answer", "score"):
        sys.exit("usage: python app/eval/evaluate_grounded_v1.py answer|score")
    if argv[1] == "answer":
        run_answer()
    else:
        run_score()


if __name__ == "__main__":
    main(sys.argv)
