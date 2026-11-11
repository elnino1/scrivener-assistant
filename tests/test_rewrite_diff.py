from scrivener_assistant.rewrite_diff import compute_rewrite_diff

DRAFT = "Il marchait dans la rue. Le ciel était gris. Elle l'attendait au coin.\nLa pluie tombait."


def test_identical_has_zero_edit_rate():
    d = compute_rewrite_diff(DRAFT, DRAFT)
    assert d["edit_rate"] == 0.0 and d["similarity"] == 1.0
    assert d["sentences"] == {"kept": 4, "modified": 0, "deleted": 0, "inserted": 0, "filled_in": 0}
    assert d["pairs"] == []


def test_one_sentence_modified():
    final = DRAFT.replace("Le ciel était gris.", "Le ciel était noir.")
    d = compute_rewrite_diff(DRAFT, final)
    assert d["sentences"]["modified"] == 1 and d["sentences"]["kept"] == 3
    pair = d["pairs"][0]
    assert pair["op"] == "modify" and pair["position"] == 1 and pair["category"] is None
    assert pair["before"] == "Le ciel était gris." and pair["after"] == "Le ciel était noir."
    assert d["changed_words"]["replaced"] == 1
    assert d["edit_rate"] == round(1 / d["draft_words"], 4)


def test_deletion():
    final = "Il marchait dans la rue. Elle l'attendait au coin.\nLa pluie tombait."
    d = compute_rewrite_diff(DRAFT, final)
    assert d["sentences"]["deleted"] == 1
    assert d["pairs"][0]["op"] == "delete" and d["pairs"][0]["before"] == "Le ciel était gris."
    assert d["changed_words"]["deleted"] == 4


def test_insertion():
    final = DRAFT + "\nUn chien aboya au loin."
    d = compute_rewrite_diff(DRAFT, final)
    assert d["sentences"]["inserted"] == 1
    p = d["pairs"][0]
    assert p["op"] == "insert" and p["after"] == "Un chien aboya au loin." and p["before"] is None
    assert d["changed_words"]["inserted"] == 5


def test_placeholder_fill_in_excluded():
    draft = "Elle entra. [AUTEUR: ce que Vee ressent en voyant la maison]\nIl partit."
    final = "Elle entra. Un vide immense l'envahit.\nIl partit."
    d = compute_rewrite_diff(draft, final)
    assert d["edit_rate"] == 0.0
    assert d["draft_words"] == 4
    assert len(d["fill_ins"]) == 1
    assert d["fill_ins"][0]["filled_with"] == "Un vide immense l'envahit."
    assert "AUTEUR" in d["fill_ins"][0]["placeholder"]
    assert d["pairs"] == [] and d["sentences"]["filled_in"] == 1


def test_placeholder_case_insensitive_inline():
    draft = "Elle [auteur: un geste] et sortit."
    final = "Elle haussa les épaules et sortit."
    d = compute_rewrite_diff(draft, final)
    assert d["edit_rate"] == 0.0 and len(d["fill_ins"]) == 1


def test_quote_and_space_normalisation():
    draft = "Il dit : « Viens. » Elle l’attendait..."
    final = 'Il dit : "Viens." Elle l\'attendait…'
    d = compute_rewrite_diff(draft, final)
    assert d["edit_rate"] == 0.0
    assert d["sentences"]["modified"] == 0


def test_scene_break_lines_ignored():
    d = compute_rewrite_diff("Il partit.\n***\nElle resta.", "Il partit.\nElle resta.")
    assert d["edit_rate"] == 0.0
