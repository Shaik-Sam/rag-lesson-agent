import argparse
import json
import sys

from .config import Settings
from .graph import Pipeline
from .llm import AnthropicLLM
from .memory import Memory
from .mock_llm import MockLLM
from .rubric import CHECKPOINTS


def build_llm(args, settings):
    if args.llm == "mock":
        return MockLLM(args.scenario)
    if not settings.api_key:
        print("ANTHROPIC_API_KEY is missing. Add it to .env or run with --llm mock for an offline demo.")
        raise SystemExit(2)
    return AnthropicLLM(settings.api_key, settings.generate_model, settings.judge_model)


def command_run(args):
    settings = Settings.from_env()
    if args.memory_path:
        settings.memory_path = type(settings.memory_path)(args.memory_path)
    if args.output_dir:
        settings.output_root = type(settings.output_root)(args.output_dir)
    memory = Memory(settings.memory_path, settings.promote_threshold)
    llm = build_llm(args, settings)
    print(f"Topic: {args.topic}")
    print(f"Model backend: {llm.name} | max retries: {settings.clamped_retries(args.max_retries)} | inject error: {args.inject_error}")
    print("-" * 78)
    pipeline = Pipeline(settings, llm, memory)
    state = pipeline.run(args.topic, inject_error=args.inject_error, max_retries=args.max_retries)
    print("-" * 78)
    print(f"RESULT: {state['status']} after {len(state['attempts'])} attempt(s)")
    print(f"Output folder: {state['summary']['output_dir']}")
    return 0 if state["status"] == "SHIPPED" else 1


def command_memory(args):
    settings = Settings.from_env()
    memory = Memory(args.memory_path or settings.memory_path, settings.promote_threshold)
    print(json.dumps(memory.snapshot(), indent=2, ensure_ascii=False))
    return 0


def command_feedback(args):
    settings = Settings.from_env()
    memory = Memory(args.memory_path or settings.memory_path, settings.promote_threshold)
    memory.add_feedback(args.text, args.check)
    print("Feedback saved. It will be sent to the generator on every future run.")
    return 0


def command_reset(args):
    settings = Settings.from_env()
    memory = Memory(args.memory_path or settings.memory_path, settings.promote_threshold)
    memory.reset()
    print("Memory cleared.")
    return 0


def command_rubric(args):
    for index, checkpoint in enumerate(CHECKPOINTS, start=1):
        print(f"{index:>2}. {checkpoint.id}  [{checkpoint.kind}]  {checkpoint.dimension}")
        print(f"    {checkpoint.requirement}")
    return 0


def make_parser():
    parser = argparse.ArgumentParser(prog="main.py", description="Self-evaluating lesson content generator")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="generate, evaluate and regenerate a lesson")
    run.add_argument("--topic", default=Settings.topic)
    run.add_argument("--llm", choices=["anthropic", "mock"], default="anthropic")
    run.add_argument("--scenario", choices=["struggle", "clean"], default="struggle")
    run.add_argument("--max-retries", type=int, default=None)
    run.add_argument("--inject-error", action="store_true")
    run.add_argument("--memory-path", default=None)
    run.add_argument("--output-dir", default=None)
    run.set_defaults(func=command_run)

    memory = sub.add_parser("memory", help="show what the system has learned")
    memory.add_argument("--memory-path", default=None)
    memory.set_defaults(func=command_memory)

    feedback = sub.add_parser("feedback", help="teach the system from human feedback")
    feedback.add_argument("text")
    feedback.add_argument("--check", default=None)
    feedback.add_argument("--memory-path", default=None)
    feedback.set_defaults(func=command_feedback)

    reset = sub.add_parser("reset-memory", help="clear learned memory")
    reset.add_argument("--memory-path", default=None)
    reset.set_defaults(func=command_reset)

    rubric = sub.add_parser("rubric", help="print the pass/fail rubric")
    rubric.set_defaults(func=command_rubric)
    return parser


def main(argv=None):
    args = make_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
