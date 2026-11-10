---
name: voice-bootstrap
description: Initialisation unique de la voix de l'auteur. À lancer une fois, sur un corpus écrit entièrement par l'auteur (chapitre "Celestia" + premières sections de "La découverte de Vee"). Calcule la baseline chiffrée, rédige voice/guide.md (gestes, cibles, liste noire, dimensions du juge), choisit des exemplaires et initialise hypotheses.md et ledger.md. Ne modifie jamais world/style.md.
model: claude-opus-4-7
---

Lis le fichier `src/scrivener_assistant/agent_prompts/voice_bootstrap.md` avec l'outil Read, puis suis-le à la lettre : ce fichier est la source unique des instructions (il est aussi exposé comme prompt MCP `voice-bootstrap` pour Claude Desktop).
