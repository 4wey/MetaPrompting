"""Simple entrypoint for one local MVP run."""

from app.runner import load_tasks_from_csv, run_single_task, save_run_log


def main() -> None:
    tasks = load_tasks_from_csv()
    if not tasks:
        raise ValueError("No tasks found in data/tasks.csv")

    task_record = tasks[0]
    state = run_single_task(task_id=task_record.id, task=task_record.task)
    log_path = save_run_log(state)

    print(f"task_id: {state.task_id}")
    print(f"task: {state.task}")
    print(f"strategy: {state.plan.strategy if state.plan else ''}")
    print(f"steps: {state.plan.steps if state.plan else []}")
    print(f"draft_solution: {state.draft_solution}")
    print(f"critic_feedback: {state.critic_feedback}")
    print(f"final_answer: {state.final_answer}")
    print(f"replan_count: {state.replan_count}")
    print(f"log_path: {log_path}")


if __name__ == "__main__":
    main()
