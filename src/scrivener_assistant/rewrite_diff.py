"""
Draft vs final comparison ("rewrite diff").

Measures how much the author changed an AI draft when retouching it. Pure
functions, standard library only (difflib).
"""
import re
from difflib import SequenceMatcher
from scrivener_assistant.voice_stats import PLACEHOLDER_RE, split_sentences
_MARKER_RE = re.compile(r"⟦PH(\d+)⟧")
_PAIR_THRESHOLD = 0.3
_PLACEHOLDER_MIN_SIM = 0.5


def normalize(text: str) -> str:
    """
    Normalise text for comparison only: nbsp -> space, curly quotes -> straight,
    guillemets -> straight double quotes (inner spaces dropped), `...` -> `…`,
    dash variants -> `—`, no space before `? ! ; :`, whitespace collapsed.
    """
    text = text.replace(" ", " ").replace(" ", " ").replace(" ", " ")
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"«\s*", '"', text)
    text = re.sub(r"\s*»", '"', text)
    text = text.replace("...", "…").replace("–", "—")
    text = re.sub(r"\s+([?!;:])", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def _substitute_placeholders(text: str):
    """Replace each [AUTEUR: …] by a one-token marker; same content -> same marker."""
    markers = {}   # marker -> original text
    keys = {}      # normalised placeholder -> marker

    def repl(m):
        key = normalize(m.group(0)).lower()
        if key not in keys:
            keys[key] = f"⟦PH{len(keys)}⟧"
            markers[keys[key]] = m.group(0)
        return keys[key]

    return PLACEHOLDER_RE.sub(repl, text), markers


def _restore(text: str, markers: dict) -> str:
    return _MARKER_RE.sub(lambda m: markers.get(m.group(0), m.group(0)), text)


def _prepare(text: str):
    """Return (paragraphs, sentences, markers); a paragraph is a list of sentence dicts."""
    text, markers = _substitute_placeholders(text)
    paragraphs = []
    sentences = []
    for line in text.splitlines():
        line = line.strip()
        if not line or not re.search(r"\w", line):   # blank lines, "***", "---"...
            continue
        para = []
        for s in split_sentences(line):
            norm = normalize(s)
            item = {
                "idx": len(sentences),
                "orig": _restore(s, markers),
                "norm": norm,
                "tokens": norm.split(),
            }
            sentences.append(item)
            para.append(item)
        if para:
            paragraphs.append(para)
    return paragraphs, sentences, markers


def _has_marker(token: str) -> bool:
    return "⟦PH" in token


def _ratio(a: list, b: list) -> float:
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def _pair_ordered(dsents: list, fsents: list) -> list:
    """Order-preserving pairing maximising total similarity. Returns [(i, j)]."""
    m, n = len(dsents), len(fsents)
    if m == n:
        return [(i, i) for i in range(m)]
    sim = [[0.0] * n for _ in range(m)]
    for i, d in enumerate(dsents):
        has_ph = any(_has_marker(t) for t in d["tokens"])
        for j, f in enumerate(fsents):
            sm = SequenceMatcher(None, d["tokens"], f["tokens"], autojunk=False)
            s = sm.ratio() if sm.quick_ratio() >= _PAIR_THRESHOLD else 0.0
            if has_ph:
                s = max(s, _PLACEHOLDER_MIN_SIM)
            sim[i][j] = s if s >= _PAIR_THRESHOLD else 0.0
    dp = [[0.0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            best = max(dp[i - 1][j], dp[i][j - 1])
            if sim[i - 1][j - 1] > 0:
                best = max(best, dp[i - 1][j - 1] + sim[i - 1][j - 1])
            dp[i][j] = best
    pairs = []
    i, j = m, n
    while i > 0 and j > 0:
        if sim[i - 1][j - 1] > 0 and abs(dp[i][j] - (dp[i - 1][j - 1] + sim[i - 1][j - 1])) < 1e-12:
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif dp[i][j] == dp[i - 1][j]:
            i -= 1
        else:
            j -= 1
    return list(reversed(pairs))


def _word_diff(dtoks: list, ftoks: list):
    """Word-level ops for one sentence pair. Returns (stats, fill_ins)."""
    stats = {"deleted": 0, "inserted": 0, "replaced": 0}
    fill_ins = []
    sm = SequenceMatcher(None, dtoks, ftoks, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        d_slice = dtoks[i1:i2]
        non_ph = [t for t in d_slice if not _has_marker(t)]
        has_ph = len(non_ph) != len(d_slice)
        if has_ph and tag == "replace":
            # words replacing a placeholder are a fill-in, not an edit
            fill_ins.append({"markers": [t for t in d_slice if _has_marker(t)],
                             "filled_with": " ".join(ftoks[j1:j2])})
            stats["deleted"] += len(non_ph)
        elif tag == "replace":
            stats["replaced"] += len(d_slice)
        elif tag == "delete":
            stats["deleted"] += len(non_ph)
        else:  # insert
            stats["inserted"] += j2 - j1
    return stats, fill_ins


def compute_rewrite_diff(draft: str, final: str) -> dict:
    """
    Compare an AI draft with the author's final text.

    Both texts are normalised (whitespace, quotes, nbsp, ellipsis, dashes) before
    comparison; reported sentences keep the original text.

    Alignment: paragraphs first (identical paragraphs are skipped), then sentences
    inside each non-identical region (difflib on sentence lists; replace blocks are
    paired by best similarity, order preserving; leftovers become delete / insert),
    then word-level ops for modified sentence pairs. Words are whitespace-separated
    tokens (punctuation attached), so changing "sortit." to "sortit," is one word.

    Placeholders `[AUTEUR: …]` in the draft: words that replace a placeholder are a
    fill-in (listed in `fill_ins`), not an edit; placeholder words are excluded from
    the draft word count. Edits made inside the same replaced span as a placeholder
    are attributed to the fill-in. A placeholder-only sentence is paired with the
    nearest final sentence; extra sentences inserted around it still count as inserts.

    edit_rate = (deleted + inserted + replaced words) / draft_words, where
    - deleted: draft words removed (draft side),
    - replaced: draft words replaced by other words (draft side),
    - inserted: words added in the final (final side),
    - draft_words: draft word count, placeholder words excluded.
    Unpaired deleted/inserted sentences count all their words. similarity is the
    difflib ratio of the two word lists (fill-ins included).

    Returns: edit_rate, similarity, draft_words, final_words, changed_words
    {deleted, inserted, replaced, total}, sentences {kept, modified, deleted,
    inserted, filled_in}, fill_ins, pairs. Each pair is
    {op: "modify"|"delete"|"insert", before, after, position, category: None,
    changed_words?}; position is the 0-based sentence index in the draft (in the
    final for inserts). `category` is filled in later by the classification step.
    """
    d_paras, d_sents, d_markers = _prepare(draft)
    f_paras, f_sents, f_markers = _prepare(final)

    kept = modified = deleted_s = inserted_s = filled = 0
    changed = {"deleted": 0, "inserted": 0, "replaced": 0}
    pairs, fill_ins = [], []

    para_sm = SequenceMatcher(
        None,
        [" ".join(s["norm"] for s in p) for p in d_paras],
        [" ".join(s["norm"] for s in p) for p in f_paras],
        autojunk=False,
    )
    for tag, i1, i2, j1, j2 in para_sm.get_opcodes():
        d_region = [s for p in d_paras[i1:i2] for s in p]
        f_region = [s for p in f_paras[j1:j2] for s in p]
        if tag == "equal":
            kept += len(d_region)
            continue
        sent_sm = SequenceMatcher(None, [s["norm"] for s in d_region], [s["norm"] for s in f_region],
                                  autojunk=False)
        for stag, a1, a2, b1, b2 in sent_sm.get_opcodes():
            ds, fs = d_region[a1:a2], f_region[b1:b2]
            if stag == "equal":
                kept += len(ds)
                continue
            paired = _pair_ordered(ds, fs) if ds and fs else []
            paired_d = {i for i, _ in paired}
            paired_f = {j for _, j in paired}
            events = []   # (sort key, kind, payload)
            for i, j in paired:
                events.append((ds[i]["idx"], "pair", (ds[i], fs[j])))
            for i, d in enumerate(ds):
                if i not in paired_d:
                    events.append((d["idx"], "delete", d))
            for j, f in enumerate(fs):
                if j not in paired_f:
                    events.append((f["idx"], "insert", f))
            order = {"pair": 0, "delete": 1, "insert": 2}
            events.sort(key=lambda e: (e[0] if e[1] != "insert" else 10 ** 9 + e[0], order[e[1]]))
            for _, kind, payload in events:
                if kind == "pair":
                    d, f = payload
                    stats, fills = _word_diff(d["tokens"], f["tokens"])
                    total = sum(stats.values())
                    for k in changed:
                        changed[k] += stats[k]
                    for fill in fills:
                        fill_ins.append({
                            "placeholder": " ".join(_restore(t, d_markers) for t in fill["markers"]),
                            "filled_with": _restore(fill["filled_with"], f_markers),
                            "position": d["idx"],
                        })
                    if total == 0 and fills:
                        filled += 1
                    else:
                        modified += 1
                        pairs.append({"op": "modify", "before": d["orig"], "after": f["orig"],
                                      "position": d["idx"], "category": None, "changed_words": total})
                elif kind == "delete":
                    deleted_s += 1
                    n = sum(1 for t in payload["tokens"] if not _has_marker(t))
                    changed["deleted"] += n
                    pairs.append({"op": "delete", "before": payload["orig"], "after": None,
                                  "position": payload["idx"], "category": None, "changed_words": n})
                else:
                    inserted_s += 1
                    n = len(payload["tokens"])
                    changed["inserted"] += n
                    pairs.append({"op": "insert", "before": None, "after": payload["orig"],
                                  "position": payload["idx"], "category": None, "changed_words": n})

    d_tokens = [t for s in d_sents for t in s["tokens"]]
    f_tokens = [t for s in f_sents for t in s["tokens"]]
    draft_words = sum(1 for t in d_tokens if not _has_marker(t))
    total_changed = sum(changed.values())

    return {
        "edit_rate": round(total_changed / draft_words, 4) if draft_words else 0.0,
        "similarity": round(_ratio(d_tokens, f_tokens), 4) if (d_tokens or f_tokens) else 1.0,
        "draft_words": draft_words,
        "final_words": len(f_tokens),
        "changed_words": {**changed, "total": total_changed},
        "sentences": {
            "kept": kept,
            "modified": modified,
            "deleted": deleted_s,
            "inserted": inserted_s,
            "filled_in": filled,
        },
        "fill_ins": fill_ins,
        "pairs": pairs,
    }
