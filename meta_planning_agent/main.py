"""CLI entrypoint for the meta-planning agent.

Usage examples:
    python main.py single
    python main.py single --task-id q03
    python main.py dataset
    python main.py chat
"""

from __future__ import annotations

import argparse
import sys

from app.config import config
from app.runner import load_tasks_from_csv, run_dataset, run_single_task, save_run_log


def print_state(state) -> None:
    print(f"task_id: {state.task_id}")
    print(f"task: {state.task}")
    print(f"strategy: {state.plan.strategy if state.plan else ''}")
    print(f"steps: {state.plan.steps if state.plan else []}")
    print(f"draft_solution: {state.draft_solution}")
    print(f"critic_feedback: {state.critic_feedback}")
    print(f"final_answer: {state.final_answer}")
    print(f"replan_count: {state.replan_count}")


def run_single(task_id: str | None = None) -> int:
    tasks = load_tasks_from_csv()
    if not tasks:
        raise ValueError("No tasks found in data/tasks.csv")

    task_record = next((item for item in tasks if item.id == task_id), tasks[0])
    state = run_single_task(task_id=task_record.id, task=task_record.task)
    log_path = save_run_log(state)
    print_state(state)
    print(f"log_path: {log_path}")
    return 0


def run_all_tasks() -> int:
    tasks = load_tasks_from_csv()
    if not tasks:
        raise ValueError("No tasks found in data/tasks.csv")
    results, output_path = run_dataset(tasks)
    print(f"provider: {config.LLM_PROVIDER}")
    print(f"tasks_processed: {len(results)}")
    print(f"results_csv: {output_path}")
    return 0


def run_chat() -> int:
    print("Интерактивный режим. Напишите задачу. Для выхода введите exit.")
    counter = 1
    while True:
        try:
            task = input("\nВы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            return 0
        if not task:
            continue
        if task.lower() in {"exit", "quit", "q", "выход"}:
            print("Выход.")
            return 0

        state = run_single_task(task_id=f"chat_{counter:03d}", task=task)
        print("\nАгент:")
        print(state.final_answer)
        print("\n[Стратегия]", state.plan.strategy if state.plan else "")
        counter += 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Meta-planning agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    single_parser = subparsers.add_parser("single", help="Run one task from CSV")
    single_parser.add_argument("--task-id", help="Task ID from data/tasks.csv", default=None)

    subparsers.add_parser("dataset", help="Run all tasks from CSV")
    subparsers.add_parser("chat", help="Interactive question-answer mode")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "single":
        return run_single(task_id=args.task_id)
    if args.command == "dataset":
        return run_all_tasks()
    if args.command == "chat":
        return run_chat()

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
