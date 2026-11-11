from scrivener_assistant.voice_stats import (
    build_baseline,
    compare_voice_stats,
    compute_voice_stats,
    split_sentences,
)


def tense(text):
    return compute_voice_stats(text)["tense_mix"]["counts"]


# --- sentence splitting ---

def test_split_basic_terminators():
    assert split_sentences("Il partit. Elle resta ! Pourquoi ? Silence… Puis rien.") == [
        "Il partit.", "Elle resta !", "Pourquoi ?", "Silence…", "Puis rien.",
    ]


def test_split_abbreviations_and_initials():
    assert split_sentences("M. Dupont et Mme Martin arrivèrent. Le Dr Roux suivit.") == [
        "M. Dupont et Mme Martin arrivèrent.", "Le Dr Roux suivit.",
    ]
    assert len(split_sentences("Il vit J. R. Tolkien. Il sourit.")) == 2


def test_split_dialogue_dash_and_guillemets():
    text = "— Tu viens ? demanda-t-il. — Non."
    assert len(split_sentences(text)) == 2
    assert split_sentences("« Pars ! » cria-t-elle. Il obéit.") == ["« Pars ! » cria-t-elle.", "Il obéit."]
    assert split_sentences("Il hésita... puis entra.") == ["Il hésita... puis entra."]


# --- dialogue / basic counts ---

def test_dialogue_share_and_paragraphs():
    text = "Il marchait dans la rue.\n— Où vas-tu ?\n« Chez moi », répondit-elle."
    stats = compute_voice_stats(text)
    assert stats["paragraph_count"] == 3
    assert 0.3 < stats["dialogue_share"] < 0.7
    assert stats["sentence_length"]["dialogue"]["mean"] > 0


def test_inline_guillemets_count_as_dialogue():
    stats = compute_voice_stats("Elle dit : « un deux trois quatre cinq » puis sortit.")
    assert stats["dialogue_share"] == round(5 / 9, 4)


def test_empty_text():
    stats = compute_voice_stats("")
    assert stats["word_count"] == 0 and stats["dialogue_share"] == 0.0


# --- frequencies ---

def test_on_pronoun_counted():
    stats = compute_voice_stats("On marche. Qu'on le veuille ou non, l'on avance. Bonbon.")
    assert stats["per_1000_words"]["on"] == round(2 * 1000 / stats["word_count"], 2) or \
        stats["per_1000_words"]["on"] > 0
    # "Bonbon", "non" must not count: exactly 3 occurrences (On, qu'on, l'on)
    n = stats["word_count"]
    assert round(stats["per_1000_words"]["on"] * n / 1000) == 3


def test_ment_adverbs_stoplist():
    stats = compute_voice_stats("Il parla doucement. Un moment plus tard, comment faire ? Le document.")
    n = stats["word_count"]
    assert round(stats["per_1000_words"]["ment_adverbs"] * n / 1000) == 1


def test_punctuation_frequencies():
    stats = compute_voice_stats("Quoi ? Non ! Peut-être… Oui ; non : ça va.")
    f = stats["per_1000_words"]
    assert f["questions"] > 0 and f["exclamations"] > 0 and f["ellipses"] > 0
    assert f["semicolons"] > 0 and f["colons"] > 0


def test_opening_variety():
    stats = compute_voice_stats("Il vint. Il vit. Il rit. Elle alla. Elle sut. Tom rit.")
    assert stats["opening_variety"]["top5_share"] == 1.0
    assert stats["opening_variety"]["top5"][0] == {"word": "il", "count": 3}


# --- tense heuristics ---

def test_imparfait():
    assert tense("Il marchait.")["imparfait"] == 1


def test_passe_simple():
    c = tense("Ils partirent.")
    assert c["passe_simple"] == 1 and c["imparfait"] == 0


def test_passe_simple_stoplist():
    assert tense("Ses âmes soupirent.")["passe_simple"] == 0


def test_passe_compose():
    assert tense("Elle est venue.")["passe_compose"] == 1
    assert tense("Elle s'est levée.")["passe_compose"] == 1
    assert tense("Ils ont été là.")["passe_compose"] == 1


def test_imparfait_stoplist():
    c = tense("Jamais, mais il fait un portrait du trait.")
    assert c["imparfait"] == 0


def test_tense_ignores_dialogue():
    c = tense("— Il marchait.")
    assert sum(c.values()) == 0


# --- baseline / compare ---

def test_baseline_and_compare():
    t1 = "Il marchait dans la rue. Elle regardait le ciel.\n— Viens ! dit-il."
    t2 = "Le soir tombait sur la ville. Personne ne parlait.\n— Non, répondit-elle."
    baseline = build_baseline([t1, t2])
    assert baseline["sources"] == 2
    assert "generated_at" in baseline and baseline["aggregate"]["word_count"] > 0
    assert "word_count" not in baseline["metrics"]
    m = baseline["metrics"]["sentence_length.overall.mean"]
    assert m["tolerance"] >= 0.1 * m["mean"] - 1e-9

    comparison = compare_voice_stats(compute_voice_stats(t1), baseline)
    assert set(comparison["lexical_density"]) == {"value", "baseline", "tolerance", "within"}
    far = compute_voice_stats("Un très très très long début de phrase qui ne finit jamais vraiment et " * 5)
    far_cmp = compare_voice_stats(far, baseline)
    assert not far_cmp["sentence_length.overall.mean"]["within"]


def test_baseline_single_text_tolerance_is_10_percent():
    baseline = build_baseline(["Il marchait dans la rue sombre."])
    m = baseline["metrics"]["sentence_length.overall.mean"]
    assert m["tolerance"] == round(0.1 * m["mean"], 4)


def test_prefixed_irregular_participle_counts_as_passe_compose():
    stats = compute_voice_stats("Elle est revenue plus tard. Il est devenu muet.")
    assert stats["tense_mix"]["counts"]["passe_compose"] == 2


def test_author_placeholder_is_ignored_by_stats():
    stats = compute_voice_stats("Elle partit. [AUTEUR: ce qu'elle ressent]")
    assert stats["per_1000_words"]["colons"] == 0.0
    assert stats["word_count"] == 2
