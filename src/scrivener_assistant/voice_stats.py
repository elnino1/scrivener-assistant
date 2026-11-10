"""
Deterministic, French-fiction-aware text metrics ("voice stats").

Pure functions, standard library only. No LLM involved: the numbers are meant to
be explainable and *consistent* (the same heuristic applied to the author's text
and to an AI draft), not linguistically perfect.
"""
import datetime
import re
import statistics
from collections import Counter
from typing import Iterator, Optional

# --- Tokenisation ---------------------------------------------------------

WORD_RE = re.compile(r"\w+(?:['’\-]\w+)*", re.UNICODE)
_PART_SPLIT_RE = re.compile(r"['’\-]")

# A paragraph that starts like this is dialogue. (A paragraph starting with « is handled
# by the inline « » rule below, so that the tag after the quote stays narration.)
_DIALOGUE_START_RE = re.compile(r"^\s*(?:[—–]|-\s)")
# Inline quoted speech inside a narration paragraph (unterminated quote runs to the end).
_GUILLEMETS_RE = re.compile(r"«[^»]*(?:»|$)")

# Sentence terminator: runs of . ! ? … ... optionally followed by closing quotes/brackets,
# and followed by whitespace or end of text.
_TERMINATOR_RE = re.compile(r"(?:\.{3}|…|[.!?])+(?:\s*»|[\"”)\]])*(?=\s|$)")

_ABBREVIATIONS = {
    "m", "mm", "mme", "mmes", "mlle", "mlles", "dr", "pr", "me", "mgr", "st", "ste", "sts", "stes",
    "cf", "vs", "no", "nos", "p", "pp", "vol", "chap", "fig", "env", "éd", "av", "bd", "cie",
    "col", "cdt", "gén", "lt", "sgt", "capt", "hon", "janv", "févr", "avr", "juil", "sept",
    "oct", "nov", "déc", "ex",
}

# --- Lexical lists ----------------------------------------------------------

_MENT_STOPLIST = {
    "moment", "comment", "élément", "gouvernement", "appartement", "vêtement", "sentiment",
    "mouvement", "monument", "instrument", "document", "argument", "jument", "aliment", "ciment",
    "serment", "segment", "tourment", "fragment", "froment", "logement", "bâtiment", "événement",
    "évènement", "changement", "tempérament", "testament", "compartiment", "département",
    "règlement", "développement", "établissement", "commencement", "enseignement", "fondement",
    "déroulement", "remerciement", "médicament", "ornement", "supplément", "complément",
    "parlement", "tremblement", "sacrement", "battement", "jugement", "commandement",
    "rassemblement", "emplacement", "dément", "pigment", "ferment", "excrément", "armement",
    "ameublement", "campement", "dénouement", "engagement", "arrangement", "attachement",
    "déplacement", "remplacement", "agencement", "avertissement", "bouleversement",
    "étonnement", "frémissement", "hurlement", "gémissement", "retournement", "soulagement",
    "isolement", "apaisement", "claquement", "craquement", "grincement", "ricanement",
    "bruissement", "froissement",
}
# A word ending in -ment right after one of these is a noun, not an adverb.
_DETERMINERS = {
    "le", "la", "un", "une", "les", "des", "du", "de", "d", "son", "sa", "ses", "ce", "cet",
    "cette", "mon", "ma", "mes", "leur", "leurs", "notre", "votre", "au", "aux", "ton", "ta",
    "tout", "chaque", "quel", "quelque",
}

_IMPARFAIT_STOPLIST = {
    "mais", "jamais", "désormais", "fait", "lait", "souhait", "trait", "portrait", "retrait",
    "attrait", "parfait", "bienfait", "forfait", "défait", "refait", "satisfait", "contrefait",
    "mauvais", "français", "anglais", "irlandais", "hollandais", "palais", "marais", "engrais",
    "épais", "balais", "relais", "niais", "harnais", "rabais", "biais", "frais", "sait",
    "plait", "souhaits", "faits", "traits",
}
_PASSE_SIMPLE_SUFFIXES = ("èrent", "irent", "urent", "âmes", "âtes", "îmes", "ûmes")
_PASSE_SIMPLE_STOPLIST = {
    # souls / noodles / abyss, and present-tense -er verbs that look like passé simple
    "âmes", "pâtes", "abîmes", "tirent", "retirent", "attirent", "soupirent", "respirent",
    "admirent", "désirent", "inspirent", "aspirent", "expirent", "conspirent", "transpirent",
    "murmurent", "figurent", "mesurent", "assurent", "rassurent", "endurent", "capturent",
    "torturent", "procurent", "jurent", "durent", "obscurent", "injurent", "conjurent",
    "saturent",
}

_AUX_PRESENT = {"a", "as", "ai", "avons", "avez", "ont", "est", "es", "suis", "sommes", "êtes", "sont"}
_IRREGULAR_PARTICIPLES = {
    "pris", "mis", "assis", "permis", "promis", "surpris", "compris", "appris", "repris", "soumis",
    "dit", "écrit", "fait", "conduit", "produit", "construit", "détruit", "traduit", "séduit",
    "ouvert", "offert", "couvert", "découvert", "souffert", "mort", "morte",
    "vu", "vue", "vus", "vues", "su", "eu", "eue", "pu", "dû", "lu", "bu", "cru", "voulu",
    "venu", "venue", "venus", "venues", "tenu", "tenue", "tenus", "connu", "connue", "perdu",
    "perdue", "rendu", "rendue", "entendu", "entendue", "attendu", "attendue", "vécu", "reçu",
    "reçue", "apparu", "paru", "parue", "répondu", "descendu", "descendue",
    "fini", "finie", "parti", "partie", "partis", "sorti", "sortie", "sortis", "senti", "sentie",
    "dormi", "servi", "suivi", "suivie", "choisi", "saisi", "saisie", "rempli", "remplie",
    "grandi", "pâli", "souri", "ri", "menti", "réussi", "obéi", "vieilli", "rougi", "surgi",
}


_COMPOUND_PARTICIPLE_ROOTS = tuple(p for p in _IRREGULAR_PARTICIPLES if len(p) >= 3)

# Placeholder left by draft-agent where the inputs don't settle the content.
PLACEHOLDER_RE = re.compile(r"\[\s*AUTEUR\s*:[^\]]*\]", re.IGNORECASE)


def _is_participle(word: str) -> bool:
    if word in _IRREGULAR_PARTICIPLES:
        return True
    # Prefixed compounds of irregular participles: revenue, devenu, remis, redit...
    if word.endswith(_COMPOUND_PARTICIPLE_ROOTS):
        return True
    return len(word) >= 3 and word.endswith(("é", "ée", "és", "ées"))


# --- Basic helpers ------------------------------------------------------------

def words(text: str) -> list:
    """Return the word tokens of a text (elisions and hyphenated words stay one token)."""
    return WORD_RE.findall(text)


def _parts(token: str) -> list:
    return [p for p in _PART_SPLIT_RE.split(token.lower()) if p]


def split_sentences(text: str) -> list:
    """
    Split text into sentences (French fiction aware).

    A sentence ends at `.`, `!`, `?`, `…` or `...` (optionally followed by a closing
    `»` / quote / bracket) when followed by whitespace. There is no split when:
    - the next non-space character is lowercase (`« Vraiment ? dit-il. »`);
    - the terminator is a single `.` after a known abbreviation (M., Mme, Dr, St...)
      or after a single capital letter (an initial: `J. R. R.`).
    """
    sentences = []
    start = 0
    for m in _TERMINATOR_RE.finditer(text):
        end = m.end()
        rest = text[end:].lstrip()
        if rest and rest[0].islower():
            continue
        if m.group(0) == ".":
            prev_match = re.search(r"([^\W\d_]+)$", text[:m.start()])
            if prev_match:
                prev = prev_match.group(1)
                if prev.lower() in _ABBREVIATIONS or (len(prev) == 1 and prev.isupper()):
                    continue
        sentence = text[start:end].strip()
        if sentence:
            sentences.append(sentence)
        start = end
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def _percentile(sorted_values: list, p: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    pos = (len(sorted_values) - 1) * p
    low = int(pos)
    high = min(low + 1, len(sorted_values) - 1)
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (pos - low)


def _length_stats(lengths: list) -> dict:
    if not lengths:
        return {"mean": 0.0, "median": 0.0, "p10": 0.0, "p90": 0.0}
    ordered = sorted(lengths)
    return {
        "mean": round(statistics.fmean(ordered), 2),
        "median": round(float(statistics.median(ordered)), 2),
        "p10": round(_percentile(ordered, 0.10), 2),
        "p90": round(_percentile(ordered, 0.90), 2),
    }


def _parse_paragraphs(text: str) -> list:
    """
    Return a list of paragraphs; each paragraph is a list of (kind, segment) where
    kind is "dialogue" or "narration". Paragraphs are non-empty lines.
    """
    paragraphs = []
    for line in text.splitlines():
        line = line.strip()
        if not line or not WORD_RE.search(line):
            continue
        if _DIALOGUE_START_RE.match(line):
            paragraphs.append([("dialogue", line)])
            continue
        segments = []
        pos = 0
        for m in _GUILLEMETS_RE.finditer(line):
            before = line[pos:m.start()].strip()
            if before and WORD_RE.search(before):
                segments.append(("narration", before))
            quoted = m.group(0).strip()
            if WORD_RE.search(quoted):
                segments.append(("dialogue", quoted))
            pos = m.end()
        after = line[pos:].strip()
        if after and WORD_RE.search(after):
            segments.append(("narration", after))
        if segments:
            paragraphs.append(segments)
    return paragraphs


def _first_word(sentence: str) -> Optional[str]:
    m = WORD_RE.search(sentence)
    return m.group(0).lower() if m else None


# --- Tense heuristics ---------------------------------------------------------

def _tense_counts(narration_sentences: list) -> dict:
    counts = {"passe_simple": 0, "imparfait": 0, "passe_compose": 0}
    for sentence in narration_sentences:
        toks = []
        for w in words(sentence):
            toks.extend(_parts(w))
        for i, tok in enumerate(toks):
            if tok in _PASSE_SIMPLE_STOPLIST or tok in _IMPARFAIT_STOPLIST:
                continue
            if len(tok) >= 5 and tok.endswith(_PASSE_SIMPLE_SUFFIXES):
                counts["passe_simple"] += 1
            elif (len(tok) >= 6 and tok.endswith("aient")) or (len(tok) >= 5 and tok.endswith(("ais", "ait"))):
                counts["imparfait"] += 1
            elif len(tok) >= 6 and tok.endswith(("ions", "iez")) and i > 0 and toks[i - 1] in ("nous", "vous"):
                counts["imparfait"] += 1
            elif tok in _AUX_PRESENT and any(_is_participle(nxt) for nxt in toks[i + 1:i + 3]):
                counts["passe_compose"] += 1
    return counts


# --- Public API ---------------------------------------------------------------

def compute_voice_stats(text: str) -> dict:
    """
    Compute deterministic style metrics for a French fiction text.

    Parsing: paragraphs are non-empty lines. A paragraph starting with `—`, `–` or
    `- ` is dialogue; in any other paragraph, text within « » is dialogue (the rest,
    including tags like "dit-il" after a quote, stays narration).

    Returned metrics (all rounded; heuristic ones are marked `approx`):
    - word_count, sentence_count, paragraph_count: raw counts. Words are tokens
      like `l'homme` or `peut-être` (one word each).
    - sentence_length.{overall,narration,dialogue}: mean / median / p10 / p90 in
      words per sentence (0.0 when there are no sentences of that kind).
    - paragraph_length: mean_words, median_words, mean_sentences, median_sentences.
    - dialogue_share: share of words that are dialogue (0..1).
    - per_1000_words (frequency per 1,000 words of the whole text):
        on             the pronoun "on" (also in l'on, qu'on, dit-on), case-insensitive;
        ment_adverbs   approx: words in -ment (>= 6 letters) minus a stoplist of
                       nouns (moment, comment, document...) and minus words right
                       after a determiner (un/le/son... = noun);
        exclamations   runs of `!`; questions: runs of `?` (so `?!` counts once each);
        ellipses       `…` and `...`; semicolons: `;`; colons: `:`.
    - opening_variety: top5_share = share of sentences whose first word is one of
      the 5 most frequent first words (lower = more varied) and top5 = that list.
    - lexical_density: mean type/token ratio over consecutive 500-word windows
      (whole text if shorter than 500 words; the trailing partial window is ignored).
    - tense_mix (approx, narration sentences only; the present tense is left out).
      counts and shares (over the three counted tenses):
        passe_simple   only distinctive endings: -èrent, -irent, -urent, -âmes, -âtes,
                       -îmes, -ûmes. Third-person singular forms (-it, -ut, -a) are
                       skipped because they collide with present/nouns. Stoplist for
                       look-alikes (âmes, pâtes, tirent, soupirent, murmurent...).
        imparfait      endings -ais, -ait, -aient (>= 5 letters) minus a stoplist
                       (mais, jamais, fait, lait, souhait, trait, portrait...);
                       -ions / -iez only right after "nous" / "vous". Conditional
                       forms (irait...) look identical and are counted as imparfait.
        passe_compose  present auxiliary avoir/être (a, ont, est, sont...) followed
                       within 2 words by a past participle (-é/-ée/-és/-ées or an
                       irregular participle list). "il est fatigué" is a false positive.
    """
    # [AUTEUR: …] placeholders are instructions to the author, not prose.
    text = PLACEHOLDER_RE.sub(" ", text)
    paragraphs = _parse_paragraphs(text)

    all_words = words(text)
    word_count = len(all_words)

    sent_overall, sent_narr, sent_dial = [], [], []
    narration_sentences = []
    first_words = []
    para_words, para_sentences = [], []
    dialogue_words = 0

    for segments in paragraphs:
        p_words = 0
        p_sents = 0
        for kind, segment in segments:
            for sentence in split_sentences(segment):
                n = len(words(sentence))
                if n == 0:
                    continue
                sent_overall.append(n)
                if kind == "dialogue":
                    sent_dial.append(n)
                    dialogue_words += n
                else:
                    sent_narr.append(n)
                    narration_sentences.append(sentence)
                fw = _first_word(sentence)
                if fw:
                    first_words.append(fw)
                p_words += n
                p_sents += 1
        para_words.append(p_words)
        para_sentences.append(p_sents)

    per_k = 1000.0 / word_count if word_count else 0.0

    on_count = 0
    ment_count = 0
    prev = ""
    for w in all_words:
        parts = _parts(w)
        on_count += parts.count("on")
        for part in parts:
            if len(part) >= 6 and part.endswith("ment") and part not in _MENT_STOPLIST \
                    and prev not in _DETERMINERS:
                ment_count += 1
        prev = parts[-1] if parts else ""

    def per1000(count: int) -> float:
        return round(count * per_k, 2)

    freq = Counter(first_words)
    top5 = freq.most_common(5)
    top5_share = sum(c for _, c in top5) / len(first_words) if first_words else 0.0

    lowered = [w.lower() for w in all_words]
    if word_count == 0:
        density = 0.0
    elif word_count < 500:
        density = len(set(lowered)) / word_count
    else:
        ratios = [len(set(lowered[i:i + 500])) / 500 for i in range(0, word_count - 499, 500)]
        density = statistics.fmean(ratios)

    tense_counts = _tense_counts(narration_sentences)
    tense_total = sum(tense_counts.values())
    tense_shares = {k: round(v / tense_total, 4) if tense_total else 0.0 for k, v in tense_counts.items()}

    return {
        "word_count": word_count,
        "sentence_count": len(sent_overall),
        "paragraph_count": len(paragraphs),
        "sentence_length": {
            "overall": _length_stats(sent_overall),
            "narration": _length_stats(sent_narr),
            "dialogue": _length_stats(sent_dial),
        },
        "paragraph_length": {
            "mean_words": round(statistics.fmean(para_words), 2) if para_words else 0.0,
            "median_words": round(float(statistics.median(para_words)), 2) if para_words else 0.0,
            "mean_sentences": round(statistics.fmean(para_sentences), 2) if para_sentences else 0.0,
            "median_sentences": round(float(statistics.median(para_sentences)), 2) if para_sentences else 0.0,
        },
        "dialogue_share": round(dialogue_words / word_count, 4) if word_count else 0.0,
        "per_1000_words": {
            "on": per1000(on_count),
            "ment_adverbs": per1000(ment_count),
            "exclamations": per1000(len(re.findall(r"!+", text))),
            "questions": per1000(len(re.findall(r"\?+", text))),
            "ellipses": per1000(len(re.findall(r"…|\.{3}", text))),
            "semicolons": per1000(text.count(";")),
            "colons": per1000(text.count(":")),
        },
        "opening_variety": {
            "top5_share": round(top5_share, 4),
            "top5": [{"word": w, "count": c} for w, c in top5],
        },
        "lexical_density": round(density, 4),
        "tense_mix": {"counts": tense_counts, "shares": tense_shares},
    }


# --- Baseline and comparison --------------------------------------------------

_COUNT_KEYS = {"word_count", "sentence_count", "paragraph_count"}


def _flatten(stats: dict, prefix: str = "") -> Iterator:
    for key, value in stats.items():
        path = f"{prefix}{key}"
        if isinstance(value, dict):
            yield from _flatten(value, path + ".")
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            yield path, value


def comparable_metrics(stats: dict) -> dict:
    """Flat `{dotted.path: number}` view of the metrics usable for comparison
    (raw counts such as word_count or tense counts are excluded: they depend on text length)."""
    return {
        path: value
        for path, value in _flatten(stats)
        if path not in _COUNT_KEYS and not path.startswith("tense_mix.counts.")
    }


def build_baseline(texts: list) -> dict:
    """
    Build a baseline from several human-written texts (one text per scene/section).

    For each comparable metric: `mean` across texts and `tolerance` =
    max(sample stdev across texts, 10% of |mean|) (10% of |mean| for a single text).
    Also returns `sources`, `generated_at` and `aggregate` (stats of the concatenation).
    """
    texts = [t for t in texts if t and t.strip()]
    if not texts:
        raise ValueError("Cannot build a baseline from an empty list of texts.")
    per_text = [comparable_metrics(compute_voice_stats(t)) for t in texts]
    metrics = {}
    for key in per_text[0]:
        values = [m[key] for m in per_text if key in m]
        mean = statistics.fmean(values)
        floor = 0.10 * abs(mean)
        spread = statistics.stdev(values) if len(values) >= 2 else 0.0
        metrics[key] = {"mean": round(mean, 4), "tolerance": round(max(spread, floor), 4)}
    return {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "sources": len(texts),
        "metrics": metrics,
        "aggregate": compute_voice_stats("\n".join(texts)),
    }


def compare_voice_stats(stats: dict, baseline: dict) -> dict:
    """
    Compare `stats` (output of compute_voice_stats) with a baseline (output of
    build_baseline). Returns `{metric: {value, baseline, tolerance, within}}` for each
    metric of the baseline that is present in `stats`; `within` is true when
    |value - baseline| <= tolerance.
    """
    values = comparable_metrics(stats)
    result = {}
    for key, ref in baseline.get("metrics", {}).items():
        if key not in values:
            continue
        value = values[key]
        mean, tol = ref["mean"], ref["tolerance"]
        result[key] = {
            "value": value,
            "baseline": mean,
            "tolerance": tol,
            "within": abs(value - mean) <= tol + 1e-9,
        }
    return result
