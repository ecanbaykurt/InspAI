# Contributing to InspAI

We aim to keep InspAI **transparent** and **usable** for civil engineers, architects, inspectors, and developers. Contributions that improve documentation, fix bugs, or add features (with clear scope) are welcome.

---

## How you can contribute

- **Bug reports:** Open an issue with steps to reproduce, environment (OS, Python version), and expected vs actual behavior.  
- **Documentation:** Fix typos, clarify use cases, add examples (e.g. for a specific drone or camera), or translate docs.  
- **Code:** Fixes and small features are best as pull requests; larger features (e.g. new label schemas, new endpoints) are better discussed in an issue first.  
- **Use cases and labels:** Share how you use descriptions and labels (e.g. critical building tagging) so we can align terminology and schemas; open an issue or discussion.

---

## Repo structure (quick reference)

- **`api/`** — FastAPI service; single model (LLaVA-1.5-7B), `POST /v1/analyze` and batch.  
- **`structural_damage_model/`** — Training data prep, inference scripts, eval (BLEU/ROUGE).  
- **`docs/`** — API, deployment, embedding (drones/cameras), audience/use cases, terminology/labels, limitations.  
- **`examples/`** — Example client for the API.

---

## Pull request process

1. Fork the repo and create a branch from `main`.  
2. Make your changes; keep docs and code in sync if you add behavior.  
3. Run any relevant tests or lint (e.g. `structural_damage_model/run_eval.py` with `--no-inference` if you touch eval).  
4. Open a PR with a short description and, if needed, a link to an issue.  
5. Maintainers will review and may ask for adjustments.

---

## Code and documentation standards

- **Documentation:** Prefer clear, concise English; explain “why” where it helps engineers or inspectors.  
- **API:** Keep backward compatibility for existing endpoints and response fields; new optional fields are fine.  
- **Transparency:** New features that affect safety or professional use (e.g. new “criticality” fields) should be documented in `docs/` and, if relevant, in [LIMITATIONS_AND_TRANSPARENCY.md](docs/LIMITATIONS_AND_TRANSPARENCY.md).

---

## License

By contributing, you agree that your contributions will be under the same license as the project (see [LICENSE](LICENSE)).
