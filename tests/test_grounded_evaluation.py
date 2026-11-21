import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "app" / "eval" / "evaluate_grounded_v1.py"
spec = importlib.util.spec_from_file_location("evaluate_grounded_v1", SCRIPT)
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)

CONSTITUTION = "PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review"
PENAL_CODE = "PAKISTANCODE__Pakistan_Penal_Code_18602026-09-27EN_Under_Review"
ASSEMBLY = (
    "Every citizen shall have the right to assemble peacefully and without arms, "
    "subject to any reasonable restrictions imposed by law in the interest of public order."
)
ASSOCIATION = (
    "Every citizen shall have the right to form associations or unions, subject to any "
    "reasonable restrictions imposed by law in the interest of public order or morality."
)
HEADED_ASSEMBLY = "16. Freedom of assembly. " + ASSEMBLY
WEATHER = "Unrelated weather fixture. Heavy rain is expected in the northern districts all week."
ARTICLE16 = "What does Article 16 guarantee about freedom of assembly?"
ANSWERS = "data/interim/grounded_v1_answers_50.jsonl"
SCORES = "data/interim/grounded_v1_scores_50.jsonl"
METRICS = "evaluation/generation/grounded_v1_metrics.json"


def jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)


class Workspace:
    """A temporary repository root with the evaluator's input files."""

    def __init__(self, case, chunks, retrieval, reference=None):
        self.case = case
        directory = tempfile.TemporaryDirectory()
        case.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.write("data/processed/chunks.jsonl", chunks)
        self.write("data/interim/hybrid_rrf_results_50.jsonl", retrieval)
        if reference is not None:
            self.write("data/eval/verified_qa_50.jsonl", reference)

    def write(self, relative, rows):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(jsonl(rows), encoding="utf-8")

    def run(self, phase, seed=0, check=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), phase],
            cwd=self.root,
            env=dict(os.environ, PYTHONHASHSEED=str(seed)),
            capture_output=True,
            text=True,
            timeout=60,
        )
        if check:
            self.case.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def read(self, relative):
        text = (self.root / relative).read_text(encoding="utf-8")
        if relative.endswith(".json"):
            return json.loads(text)
        return [json.loads(line) for line in text.splitlines()]

    def answers(self):
        return {r["id"]: r for r in self.read(ANSWERS)}

    def scores(self):
        return {r["id"]: r for r in self.read(SCORES)}

    def sha256(self, relative):
        data = (self.root / relative).read_bytes().replace(b"\r\n", b"\n")
        return hashlib.sha256(data).hexdigest()


def chunk(chunk_id, text, source=CONSTITUTION + ".txt", page=None):
    record = {"chunk_id": chunk_id, "text": text}
    if source:
        record["source_file"] = source
    if page is not None:
        record["page"] = page
    return record


def row(qid, question, chunks, ids, lang="en", **extra):
    by_id = {c["chunk_id"]: c for c in chunks}
    return dict(
        id=qid, question=question, lang=lang, retrieved_chunk_ids=ids,
        retrieved_sources=[by_id[i].get("source_file", "") for i in ids], **extra,
    )


def reference(qid, answer, source=CONSTITUTION + ".pdf", page=7):
    return {"id": qid, "answer": answer, "source_file": source, "page": page}


def measure_fixture():
    """Six questions; each one fails a different measure."""
    chunks = [
        chunk("weather", WEATHER, "Other.txt", 99),
        chunk("assembly", HEADED_ASSEMBLY, page=7),
        chunk("assembly_nopage", HEADED_ASSEMBLY),
        chunk("association", "17. Freedom of association. " + ASSOCIATION, page=8),
    ]
    retrieval = [
        row("ok", ARTICLE16, chunks, ["weather", "assembly"]),
        row("no_page", ARTICLE16, chunks, ["assembly_nopage"]),
        row("wrong_document", ARTICLE16, chunks, ["assembly"]),
        row("abstain_ok", "What does Article 99 provide about tides?", chunks, ["weather"]),
        row("abstain_missed", "آرٹیکل 16 اجتماع کی آزادی کے بارے میں کیا کہتا ہے؟", chunks, ["assembly"], lang="ur"),
        row("unsupported", "What does Article 17 say about freedom of association?", chunks, ["association"]),
    ]
    references = [
        reference("ok", ASSEMBLY),
        reference("no_page", ASSEMBLY),
        reference("wrong_document", ASSEMBLY, source="PAKISTANCODE__Pakistan_Penal_Code_1860.pdf"),
        reference("abstain_ok", ASSEMBLY),
        reference("abstain_missed", ASSEMBLY),
        reference("unsupported", ASSEMBLY, page=9),
    ]
    return chunks, retrieval, references


class IssueFailureCaseTests(unittest.TestCase):
    """The failure cases of issue #1, reproduced on temporary fixtures."""

    def test_answers_do_not_change_with_the_reference_or_the_gold_fields(self):
        # Issue #1 repro: the passages never change; the reference and the gold_* fields do.
        scenarios = {
            "issue repro": ([chunk("other", "Unrelated weather fixture.", "Other.txt", 99),
                             chunk("constitution", "Another weather fixture.", "Constitution.txt", 7)],
                            "What is the fixture answer?"),
            "supported answer, no page": ([chunk("other", WEATHER, "Other.txt", 99),
                                           chunk("constitution", HEADED_ASSEMBLY)], ARTICLE16),
        }
        variants = [("Constitution.pdf", 7, "GOLD ANSWER A"), ("Other.pdf", 8, "GOLD ANSWER B"),
                    ("Other.txt", None, ""), ("", 7, "GOLD ANSWER A")]
        for name, (chunks, question) in scenarios.items():
            runs = []
            for gold_source, gold_page, gold_answer in variants:
                retrieval = [row("fixture", question, chunks, ["other", "constitution"],
                                 gold_source_file=gold_source, gold_page=gold_page)]
                ws = Workspace(self, chunks, retrieval,
                               [reference("fixture", gold_answer, gold_source or "x.pdf", gold_page)])
                ws.run("answer")
                # The retrieval files differ, so only the recorded input hash may differ.
                runs.append([{k: v for k, v in r.items() if k != "generator"} for r in ws.read(ANSWERS)])
            with self.subTest(name):
                for later in runs[1:]:
                    self.assertEqual(runs[0], later)
                self.assertNotIn("GOLD ANSWER", json.dumps(runs[0]))
        self.assertEqual(runs[0][0]["status"], "answered")  # the second scenario is not vacuous
        self.assertEqual(runs[0][0]["citation"]["page"], "unknown")

    def test_answer_phase_runs_without_any_reference_file(self):
        chunks = [chunk("c1", HEADED_ASSEMBLY, page=7)]
        ws = Workspace(self, chunks, [row("q", ARTICLE16, chunks, ["c1"])])
        ws.run("answer")
        self.assertFalse((ws.root / "data/eval").exists())
        self.assertEqual(ws.answers()["q"]["status"], "answered")

    def test_support_comes_from_the_retrieved_text_not_the_filename(self):
        # The retrieved filename is the gold document, but its text is unrelated.
        chunks = [chunk("c1", WEATHER, page=7)]
        ws = Workspace(self, chunks, [row("q", ARTICLE16, chunks, ["c1"])], [reference("q", ASSEMBLY)])
        ws.run("answer")
        ws.run("score")
        self.assertEqual(ws.answers()["q"]["status"], "abstained")
        self.assertFalse(ws.scores()["q"]["evidence_sufficient"])
        self.assertTrue(ws.scores()["q"]["abstention_appropriate"])

    def test_citation_points_to_the_supporting_passage_not_the_first_result(self):
        chunks = [chunk("other", WEATHER, "Other.txt", 99), chunk("support", HEADED_ASSEMBLY, page=7)]
        ws = Workspace(self, chunks, [row("q", ARTICLE16, chunks, ["other", "support"])])
        ws.run("answer")
        self.assertEqual(ws.answers()["q"]["citation"], {
            "chunk_id": "support", "rank": 2, "source": CONSTITUTION + ".txt", "page": 7})

    def test_missing_page_and_source_stay_unknown(self):
        chunks = [chunk("support", HEADED_ASSEMBLY, source=None)]
        retrieval = [row("q", ARTICLE16, chunks, ["support"],
                         gold_source_file=CONSTITUTION + ".pdf", gold_page=7)]
        retrieval[0]["retrieved_sources"] = []
        ws = Workspace(self, chunks, retrieval, [reference("q", ASSEMBLY, page=7)])
        ws.run("answer")
        ws.run("score")
        self.assertEqual(ws.answers()["q"]["citation"]["page"], "unknown")
        self.assertEqual(ws.answers()["q"]["citation"]["source"], "unknown")
        score = ws.scores()["q"]
        self.assertEqual((score["citation_page"], score["citation_source"]), ("unknown", "unknown"))
        self.assertFalse(score["citation_correct"])

    def test_document_match_uses_exact_aliases_not_a_constitution_substring(self):
        table = ev.load_aliases()
        constitution = ev.resolve_document(CONSTITUTION + ".pdf", table)
        self.assertEqual(ev.resolve_document(CONSTITUTION + ".txt", table), constitution)
        self.assertNotEqual(ev.resolve_document(PENAL_CODE + ".txt", table), constitution)
        self.assertEqual(ev.resolve_document("PAKISTANCODE__Pakistan_Penal_Code_1860.pdf", table),
                         ev.resolve_document(PENAL_CODE + ".txt", table))
        for name in ("Constitution_Amendment_Notes.txt",           # no alias at all
                     CONSTITUTION + "_Amendment_Notes.txt",         # an alias as a prefix
                     "Old_" + CONSTITUTION + ".txt", None, "", "unknown"):
            self.assertIsNone(ev.resolve_document(name, table), name)

    def test_oracle_style_answers_are_not_credited_as_grounded(self):
        # What the previous evaluator produced: the reference text, cited to the top result.
        chunks = [chunk("top", WEATHER, "Other.txt", None)]
        ws = Workspace(self, chunks, [row("q", "What does Article 16 guarantee?", chunks, ["top"])],
                       [reference("q", ASSEMBLY)])
        ws.run("answer")
        record = ws.read(ANSWERS)[0]
        record.update(status="answered", answer=ASSEMBLY, abstain_reason=None, matched_terms=[],
                      citation={"chunk_id": "top", "rank": 1, "source": "Other.txt", "page": 7})
        ws.write(ANSWERS, [record])
        ws.run("score")
        score = ws.scores()["q"]
        self.assertTrue(score["answer_correct"])           # the text equals the reference ...
        self.assertFalse(score["evidence_supported"])      # ... but the cited passage does not contain it
        self.assertFalse(score["citation_recorded"])       # and the cited page was not the passage's page
        self.assertFalse(score["citation_correct"])


class AnswerRuleTests(unittest.TestCase):
    def ask(self, question, *texts):
        passages = [{"rank": i, "chunk_id": f"c{i}", "source": CONSTITUTION + ".txt", "page": 7, "text": t}
                    for i, t in enumerate(texts, 1)]
        return ev.answer_question(question, passages)

    def test_each_abstention_reason(self):
        cases = [
            ("empty_question", "What does the say?", [HEADED_ASSEMBLY]),
            ("no_passage_text", ARTICLE16, [None, "  \n ", ["not text"]]),
            ("locator_not_found", "What does Article 99 provide about tides?", [HEADED_ASSEMBLY]),
            ("insufficient_support", "آرٹیکل 16 اجتماع کی آزادی کے بارے میں کیا کہتا ہے؟", [HEADED_ASSEMBLY]),
        ]
        for reason, question, texts in cases:
            with self.subTest(reason):
                result = self.ask(question, *texts)
                self.assertEqual((result["status"], result["abstain_reason"], result["citation"]),
                                 ("abstained", reason, None))

    def test_the_number_in_the_question_must_open_the_answer(self):
        abstain = {
            # the next article's number cut off at the end of a chunk is not evidence for that article
            "trailing number": ("What does Article 17 say about freedom of association?",
                                "16. Freedom of assembly.—" + ASSEMBLY + " 17."),
            "page header": ("What does Article 23 say about property?",
                            "Right to property. Every citizen shall have the right to acquire, hold and dispose "
                            "of property in any part of Pakistan. Page 23 of 179 trailing words about security."),
            "number inside a sentence": ("What does Article 16 say about assembly?",
                                         "As amended, Article 16 now says that every citizen shall have the right "
                                         "to assemble peacefully and without arms."),
        }
        for name, (question, text) in abstain.items():
            with self.subTest(name):
                self.assertEqual(self.ask(question, text)["abstain_reason"], "locator_not_found")
        answer = {
            "heading then provision": (ARTICLE16, HEADED_ASSEMBLY, HEADED_ASSEMBLY),
            "footnote marker, sentence tail before it": (
                "What does Article 25A state about right to education?",
                "by law. 1[25A. Right to education.__ The State shall provide free and compulsory education "
                "to all children of the age of five to sixteen years in such manner as may be determined by law.] 26.",
                "1[25A. Right to education.__ The State shall provide free and compulsory education "
                "to all children of the age of five to sixteen years in such manner as may be determined by law.]"),
            "chunk starts mid-sentence": (
                "What does Article 17 say about freedom of association?",
                "of public order. 17. Freedom of association.__ (1) " + ASSOCIATION,
                "17. Freedom of association.__ (1) " + ASSOCIATION),
            "long heading, provision in the next sentence": (
                "What does Article 20 guarantee regarding freedom of religion?",
                "20. Freedom to profess religion and to manage religious institutions. Subject to law, public "
                "order and morality, every citizen shall have the right to profess, practice and propagate his religion.",
                "20. Freedom to profess religion and to manage religious institutions. Subject to law, public "
                "order and morality, every citizen shall have the right to profess, practice and propagate his religion."),
            "number after a page header": (
                "What does Article 11 prohibit regarding slavery and forced labour?",
                "Page 23 of 176 11. Slavery, forced labour, etc., prohibited.—(1) Slavery is non-existent and "
                "forbidden and no law shall permit or facilitate its introduction into Pakistan in any form.",
                "11. Slavery, forced labour, etc., prohibited.—(1) Slavery is non-existent and forbidden and "
                "no law shall permit or facilitate its introduction into Pakistan in any form."),
        }
        for name, (question, text, expected) in answer.items():
            with self.subTest(name):
                result = self.ask(question, text)
                self.assertEqual((result["status"], result["answer"]), ("answered", expected))

    def test_ties_go_to_more_terms_then_higher_rank_then_shorter_then_earlier(self):
        movement = ("Every citizen shall have the right to move freely throughout Pakistan and to reside "
                    "and settle in any part thereof.")
        question = "Which citizen may assemble peacefully without arms?"
        # more matched terms beat a better rank
        self.assertEqual(self.ask(question, movement, ASSEMBLY)["citation"]["rank"], 2)
        # equal matches: the higher-ranked passage
        self.assertEqual(self.ask(question, ASSEMBLY, ASSEMBLY)["citation"]["rank"], 1)
        # equal matches in one passage: the shorter window, so no trailing sentence
        trailing = " The State shall provide free and compulsory education to all children."
        self.assertEqual(self.ask(question, ASSEMBLY + trailing)["answer"], ASSEMBLY)
        # equal matches and length: the earlier sentence
        first = "Alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu."
        second = first[:-3] + "nu."
        self.assertEqual(self.ask("alpha beta", first + " " + second)["answer"], first)

    def test_passages_take_metadata_from_the_chunk_then_the_row_and_stop_at_top_k(self):
        chunks = {"a": {"chunk_id": "a", "source_file": "A.txt", "page": "12", "text": "x"},
                  "b": {"chunk_id": "b", "page": "²", "text": "  "}}
        retrieval = {"retrieved_chunk_ids": ["a", "b", "gone"] + ["z1", "z2", "z3"],
                     "retrieved_sources": ["row-a.txt", "row-b.txt"]}
        passages = ev.build_passages(retrieval, chunks)
        self.assertEqual([p["rank"] for p in passages], list(range(1, ev.TOP_K + 1)))
        self.assertEqual((passages[0]["source"], passages[0]["page"], passages[0]["text"]), ("A.txt", 12, "x"))
        self.assertEqual((passages[1]["source"], passages[1]["page"], passages[1]["text"]),
                         ("row-b.txt", "unknown", None))
        self.assertEqual((passages[2]["source"], passages[2]["page"], passages[2]["text"]),
                         ("unknown", "unknown", None))


class ScoreRuleTests(unittest.TestCase):
    def score(self, answer=HEADED_ASSEMBLY, status="answered", ref=ASSEMBLY, ref_source=CONSTITUTION + ".pdf",
              ref_page=7, text=HEADED_ASSEMBLY, page=7, citation=None, source=CONSTITUTION + ".txt"):
        passage = {"rank": 1, "chunk_id": "c1", "source": source, "page": page, "text": text}
        cited = {"chunk_id": "c1", "rank": 1, "source": source, "page": page}
        record = {"id": "q", "lang": "en", "status": status, "passages": [passage],
                  "answer": answer if status == "answered" else "",
                  "citation": (citation or cited) if status == "answered" else None}
        return ev.score_answer(record, reference("q", ref, ref_source, ref_page), ev.load_aliases())

    def test_a_fully_verified_answer_is_correct_supported_and_cited(self):
        score = self.score()
        self.assertTrue(score["answer_correct"] and score["evidence_supported"] and score["citation_correct"])

    def test_every_citation_condition_is_required(self):
        base = {"chunk_id": "c1", "rank": 1, "source": CONSTITUTION + ".txt", "page": 7}
        cases = {
            "source not the passage's": (dict(citation=dict(base, source="Other.txt")), "citation_recorded"),
            "page not the passage's": (dict(citation=dict(base, page=8)), "citation_recorded"),
            "cited chunk not retrieved": (dict(citation=dict(base, chunk_id="gone")), "evidence_supported"),
            "answer not in the cited passage": (dict(answer="Citizens may assemble freely at any time and "
                                                            "place without any restriction at all."),
                                                "evidence_supported"),
            "reference page differs": (dict(ref_page=8), "citation_page"),
            "reference document differs": (dict(ref_source="PAKISTANCODE__Pakistan_Penal_Code_1860.pdf"),
                                           "citation_source"),
            "page unknown": (dict(page="unknown"), "citation_page"),
        }
        for name, (change, flag) in cases.items():
            with self.subTest(name):
                score = self.score(**change)
                self.assertFalse(score["citation_correct"])
                self.assertIn(score[flag], (False, "mismatch", "unknown"))

    def test_a_page_or_source_copied_from_the_reference_is_not_accurate(self):
        base = {"chunk_id": "c1", "rank": 1, "source": CONSTITUTION + ".txt", "page": 7}
        copied_page = self.score(page=5, citation=dict(base, page=7))             # passage says 5, reference says 7
        copied_source = self.score(source="Other.txt", citation=dict(base, source=CONSTITUTION + ".pdf"))
        for name, score in (("page", copied_page), ("source", copied_source)):
            with self.subTest(name):
                self.assertEqual((score["citation_source"], score["citation_page"]), ("match", "match"))
                self.assertFalse(score["citation_recorded"])
                self.assertFalse(score["citation_correct"])

    def test_answer_correctness_needs_recall_and_precision(self):
        padding = " " + " ".join(f"filler{i}" for i in range(40))
        cases = {"too long": ASSEMBLY + padding, "too short": ASSEMBLY[:60],
                 "near-duplicate provision": "17. Freedom of association. " + ASSOCIATION}
        self.assertTrue(self.score(answer=ASSEMBLY)["answer_correct"])
        for name, answer in cases.items():
            with self.subTest(name):
                self.assertFalse(self.score(answer=answer, text=answer)["answer_correct"])
        self.assertEqual(self.score(answer=ASSEMBLY + padding, text=ASSEMBLY + padding)["answer_recall"], 1.0)

    def test_abstaining_is_appropriate_only_without_sufficient_evidence(self):
        self.assertFalse(self.score(status="abstained")["abstention_appropriate"])
        self.assertTrue(self.score(status="abstained", text=WEATHER)["abstention_appropriate"])
        self.assertFalse(self.score(text=WEATHER, answer=WEATHER)["abstention_appropriate"])
        self.assertTrue(self.score()["abstention_appropriate"])


class MeasureTests(unittest.TestCase):
    def run_all(self, seed=0):
        ws = Workspace(self, *measure_fixture())
        ws.run("answer", seed)
        # An answer that its cited passage does not contain (the extractive answerer cannot produce one).
        records = ws.read(ANSWERS)
        next(r for r in records if r["id"] == "unsupported")["answer"] = "Citizens may associate without any restriction at all."
        ws.write(ANSWERS, records)
        ws.run("score", seed)
        return ws

    def test_four_measures_are_reported_separately(self):
        measures = self.run_all().read(METRICS)["measures"]
        self.assertEqual(set(measures), {"answer_correctness", "evidence_support",
                                         "citation_accuracy", "appropriate_abstention"})
        counts = {k: (m["numerator"], m["denominator"]) for k, m in measures.items()}
        self.assertEqual(counts, {
            "answer_correctness": (3, 6),      # ok, no_page, wrong_document
            "evidence_support": (3, 4),        # "unsupported" cites a passage that lacks its answer
            "citation_accuracy": (1, 4),       # only "ok": passage, source and page all verified
            "appropriate_abstention": (4, 6),  # abstain_missed and unsupported were wrong calls
        })

    def test_each_failure_is_attributed_to_its_own_measure(self):
        ws = self.run_all()
        scores = ws.scores()
        self.assertEqual(scores["no_page"]["citation_page"], "unknown")    # not taken from the reference
        self.assertEqual(scores["wrong_document"]["citation_source"], "mismatch")
        self.assertEqual(ws.answers()["abstain_missed"]["abstain_reason"], "insufficient_support")
        self.assertEqual(ws.answers()["abstain_ok"]["abstain_reason"], "locator_not_found")
        self.assertTrue(scores["abstain_missed"]["evidence_sufficient"])
        self.assertFalse(scores["unsupported"]["answer_correct"])
        self.assertFalse(scores["unsupported"]["evidence_supported"])
        self.assertFalse(scores["unsupported"]["cited_passage_has_reference"])
        breakdown = ws.read(METRICS)["breakdown"]
        self.assertEqual(breakdown["answered_cited_passage_has_reference"], 3)
        self.assertEqual(breakdown["abstain_reasons"], {"insufficient_support": 1, "locator_not_found": 1})
        self.assertEqual(breakdown["decisions"], {
            "answered_with_evidence": 3, "answered_without_evidence": 1,
            "abstained_with_evidence": 1, "abstained_without_evidence": 1,
        })

    def test_metrics_document_version_inputs_and_criteria(self):
        ws = self.run_all()
        metrics = ws.read(METRICS)
        self.assertEqual(metrics["evaluator"]["version"], ev.EVALUATOR_VERSION)
        self.assertIn("37/50", metrics["evaluator"]["label"])
        inputs = metrics["inputs"]
        for name, relative in [("answers", ANSWERS), ("reference", "data/eval/verified_qa_50.jsonl")]:
            self.assertEqual(inputs[name], {"path": relative, "sha256": ws.sha256(relative), "records": 6})
        generator = inputs["generator"]
        self.assertEqual(generator["retrieval"]["sha256"], ws.sha256("data/interim/hybrid_rrf_results_50.jsonl"))
        self.assertEqual(generator["chunks"]["sha256"], ws.sha256("data/processed/chunks.jsonl"))
        self.assertEqual(inputs["document_aliases"]["sha256"],
                         hashlib.sha256((ROOT / "evaluation/generation/document_aliases.json")
                                        .read_bytes().replace(b"\r\n", b"\n")).hexdigest())
        self.assertEqual(metrics["config"], {**ev.answer_config(), "min_coverage": ev.MIN_COVERAGE,
                                             "answer_precision": ev.ANSWER_PRECISION})
        self.assertEqual(set(metrics["definitions"]), set(metrics["measures"]))
        self.assertEqual(set(metrics["by_lang"]), {"en", "ur"})
        self.assertNotIn("grounded_rate", metrics)

    def test_names_missing_from_the_alias_table_are_listed(self):
        chunks, retrieval, references = measure_fixture()
        references[0]["source_file"] = "Unlisted_Document.pdf"
        chunks[0]["source_file"] = "Other.txt"
        ws = Workspace(self, chunks, retrieval, references)
        ws.run("answer")
        ws.run("score")
        self.assertEqual(ws.read(METRICS)["sources_not_in_alias_table"], ["Other.txt", "Unlisted_Document.pdf"])

    def test_input_hashes_do_not_depend_on_line_endings(self):
        ws = Workspace(self, *measure_fixture())
        expected = {name: ws.sha256(name) for name in ("data/interim/hybrid_rrf_results_50.jsonl",
                                                       "data/processed/chunks.jsonl")}
        for name in expected:
            path = ws.root / name
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        ws.run("answer")
        generator = ws.answers()["ok"]["generator"]
        self.assertEqual(generator["retrieval"]["sha256"], expected["data/interim/hybrid_rrf_results_50.jsonl"])
        self.assertEqual(generator["chunks"]["sha256"], expected["data/processed/chunks.jsonl"])
        self.assertEqual(ws.answers()["ok"]["status"], "answered")

    def test_outputs_do_not_depend_on_the_hash_seed(self):
        first, second = self.run_all(seed=0), self.run_all(seed=1)
        for relative in (ANSWERS, SCORES, METRICS):
            self.assertEqual((first.root / relative).read_bytes(), (second.root / relative).read_bytes())


class InputValidationTests(unittest.TestCase):
    def check(self, phase, expected, edit):
        ws = Workspace(self, *measure_fixture())
        ws.run("answer")
        edit(ws)
        result = ws.run(phase, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(expected, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return ws

    def test_answer_phase_rejects_bad_inputs_with_a_message(self):
        retrieval = "data/interim/hybrid_rrf_results_50.jsonl"
        chunks_path = "data/processed/chunks.jsonl"
        cases = {
            "chunks.jsonl not found": lambda ws: (ws.root / chunks_path).unlink(),
            "has no records": lambda ws: ws.write(retrieval, []),
            "duplicate chunk_id": lambda ws: ws.write(chunks_path, ws.read(chunks_path) * 2),
            "duplicate id": lambda ws: ws.write(retrieval, ws.read(retrieval) * 2),
            "chunks.jsonl:1: invalid JSON": lambda ws: (ws.root / chunks_path).write_text("{oops\n", encoding="utf-8"),
            "missing id": lambda ws: ws.write(retrieval, [{"question": "q"}]),
        }
        for expected, edit in cases.items():
            with self.subTest(expected):
                ws = Workspace(self, *measure_fixture())
                edit(ws)
                result = ws.run("answer", check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse((ws.root / ANSWERS).exists())  # nothing half-written

    def test_a_byte_order_mark_is_accepted(self):
        ws = Workspace(self, *measure_fixture())
        path = ws.root / "data/interim/hybrid_rrf_results_50.jsonl"
        path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())
        ws.run("answer")
        self.assertEqual(len(ws.answers()), 6)

    def test_score_phase_rejects_mismatched_inputs_with_a_message(self):
        reference_path = "data/eval/verified_qa_50.jsonl"

        def other_generator(ws):
            records = ws.read(ANSWERS)
            records[0]["generator"] = dict(records[0]["generator"], name="another")
            ws.write(ANSWERS, records)

        def other_config(ws):
            records = ws.read(ANSWERS)
            for record in records:
                record["generator"]["config"]["top_k"] = 10
            ws.write(ANSWERS, records)

        cases = {
            "answer ids and reference ids differ": lambda ws: ws.write(reference_path, ws.read(reference_path)[:-1]),
            "duplicate id": lambda ws: ws.write(reference_path, ws.read(reference_path) * 2),
            "missing answer": lambda ws: ws.write(reference_path, [{"id": "ok"}]),
            "more than one generator": other_generator,
            "different version or configuration": other_config,
        }
        for expected, edit in cases.items():
            with self.subTest(expected):
                self.check("score", expected, edit)


class HelperTests(unittest.TestCase):
    def test_numbering_stays_with_its_heading_and_other_fragments_do_not(self):
        text = "...in any part thereof. \n16. Freedom of assembly. Every citizen shall \nhave the right to assemble. 17."
        self.assertEqual(ev.split_sentences(text), [
            "...in any part thereof.", "16. Freedom of assembly.",
            "Every citizen shall have the right to assemble."])
        self.assertEqual(ev.split_sentences("by law. 1[25A. Right to education.__ The State shall act."),
                         ["by law.", "1[25A. Right to education.__ The State shall act."])
        self.assertEqual(ev.split_sentences("Page 2 of 176 11. Slavery is forbidden here."),
                         ["11. Slavery is forbidden here."])
        self.assertEqual(ev.split_sentences(None), [])
        self.assertEqual(len(ev.split_sentences("کیا یہ درست ہے؟ جی ہاں، یہ بالکل درست ہے۔ اور یہ تیسرا جملہ ہے۔")), 3)

    def test_tokenize_maps_arabic_indic_digits_and_ignores_markup_and_soft_hyphens(self):
        self.assertEqual(ev.tokenize("آرٹیکل ۱۰ و 1[19A.__ Right]"), ["آرٹیکل", "10", "و", "1", "19a", "right"])
        self.assertEqual(ev.tokenize("accor\u00addance"), ["accordance"])

    def test_coverage_counts_words_in_order(self):
        self.assertEqual(ev.coverage(["a", "b", "c"], ["a", "x", "b", "y", "c"]), 1.0)
        self.assertAlmostEqual(ev.coverage(["a", "b", "c"], ["c", "b", "a"]), 1 / 3)
        self.assertEqual(ev.coverage([], ["a"]), 0.0)

    def test_page_is_a_positive_integer_or_unknown(self):
        values = (7, "12", " 3 ", "٧", 0, None, "", True, "x", "²", "①", 7.5)
        self.assertEqual([ev.clean_page(v) for v in values],
                         [7, 12, 3, 7] + ["unknown"] * 8)

    def test_alias_table_covers_the_committed_data_without_collisions(self):
        table = ev.load_aliases()
        names = set()
        for name in ("verified_qa_50", "hybrid_rrf_results_50", "bm25_results_50", "dense_results_50"):
            path = next((ROOT / "data").rglob(name + ".jsonl"))
            for line in path.read_text(encoding="utf-8").splitlines():
                record = json.loads(line)
                names.update(record.get("retrieved_sources", []))
                names.add(record.get("source_file") or record.get("gold_source_file"))
        names.discard(None)
        self.assertEqual([n for n in sorted(names) if ev.resolve_document(n, table) is None], [])

    def test_an_alias_listed_under_two_documents_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aliases.json"
            path.write_text(json.dumps({"documents": {"A": {"aliases": ["Same.pdf"]},
                                                      "B": {"aliases": ["same.txt"]}}}), encoding="utf-8")
            with self.assertRaises(ValueError):
                ev.load_aliases(path)


class DocumentationTests(unittest.TestCase):
    def test_documentation_states_the_evaluator_version_and_thresholds(self):
        doc = (ROOT / "docs/grounded-evaluation.md").read_text(encoding="utf-8")
        for expected in (f"`{ev.EVALUATOR_VERSION}`", f"top {ev.TOP_K}", f"{ev.MIN_ANSWER_WORDS} non-numeric words",
                         f"fewer than {ev.MIN_MATCHED_TERMS} distinct question terms",
                         f"{ev.MIN_COVERAGE:.0%} of the", f"{ev.ANSWER_PRECISION:.0%} reference words"):
            self.assertIn(expected, doc)


class PreviousEvaluatorTests(unittest.TestCase):
    """The 37/50 outputs stay as they were and are labelled as the previous evaluator's."""

    def digest(self, relative):
        data = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n")
        return hashlib.sha256(data).hexdigest()

    def test_previous_outputs_are_preserved(self):
        self.assertEqual(self.digest("data/interim/grounded_answers_50.jsonl"),
                         "a2519970e339182f4dbc4097ba564795f462d47a8e11e5fffc1cffd07351b268")
        self.assertEqual(self.digest("evaluation/retrieval/grounded_metrics.json"),
                         "5b07c7f9a03be556dd4e7d26cc2e81f1e8b3f740dc2e05a507570be26afa689b")
        metrics = json.loads((ROOT / "evaluation/retrieval/grounded_metrics.json").read_text(encoding="utf-8"))
        self.assertEqual((metrics["grounded_cited"], metrics["total_qa"]), (37, 50))

    def test_revised_outputs_use_separate_paths(self):
        previous = {"data/interim/grounded_answers_50.jsonl", "evaluation/retrieval/grounded_metrics.json"}
        revised = {ev.ANSWERS_PATH.as_posix(), ev.SCORES_PATH.as_posix(), ev.METRICS_PATH.as_posix()}
        self.assertEqual(previous & revised, set())

    def test_previous_result_is_labelled_where_it_is_reported(self):
        results = (ROOT / "evaluation/retrieval/FINAL_RESULTS.md").read_text(encoding="utf-8").splitlines()
        for needle in ("37 cited", "grounded_answers_50.jsonl"):
            self.assertIn("previous evaluator", next(l for l in results if needle in l), needle)
        readme = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
        for needle in ("badge/Grounded", "Best MRR", "###"):
            line = next(l for l in readme if needle in l and ("Grounded" in l))
            self.assertIn("previous", line.lower(), needle)
        script = (ROOT / "app/eval/evaluate_grounded.py").read_text(encoding="utf-8")
        self.assertIn("PREVIOUS EVALUATOR", script.splitlines()[0])


if __name__ == "__main__":
    unittest.main()
