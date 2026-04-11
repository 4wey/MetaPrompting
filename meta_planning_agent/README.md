# Meta Planning Agent

This project is a minimal учебный MVP of an LLM-based agent for prompt meta-planning.

Research question:
Does an agent with meta-planning improve the quality of solving complex multi-step tasks compared with a baseline LLM?

The core idea is to separate the work into roles:
- Planner builds a strategy and step-by-step plan.
- Solver follows the plan and produces a draft solution.
- Critic reviews the result and can request replanning.

Current status:
- local MVP;
- deterministic LLM stub instead of a real API;
- prompts stored separately in `.md` files;
- run logs saved as `.json`;
- dataset stored in `.csv`.

## Project structure

- `app/` - core Python modules
- `prompts/` - prompt templates for Planner, Solver, Critic
- `data/` - test dataset
- `logs/` - saved run logs
- `notebooks/` - future analysis notebooks
- `main.py` - one local test run

## How to run

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the MVP:

```bash
python main.py
```

## Notes

- The project runs locally without an external model API.
- All model interaction goes through `app/llm.py`.
- Later, the stub in `app/llm.py` can be replaced with a real API client without rebuilding the whole project.
