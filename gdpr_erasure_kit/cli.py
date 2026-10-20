"""Command-line entry point; all operations stay on the local filesystem."""

import argparse
import sys
from datetime import date
from pathlib import Path

from .dates import DateRangeError, deadline, parse_date
from .io import InputError, exclusive_file, prepare_output, read_identity, read_services
from .render import render_request, slug
from .tracker import draft_row, due_actions, write_tracker


class InputArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(1, f"{self.prog}: error: {message}\n")


def date_argument(value: str) -> date:
    try:
        return parse_date(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected a valid YYYY-MM-DD date.") from exc


def parser() -> argparse.ArgumentParser:
    result = InputArgumentParser(prog="gdpr-kit")
    commands = result.add_subparsers(dest="command", required=True)
    draft = commands.add_parser("draft")
    draft.add_argument("--services", required=True, type=Path)
    draft.add_argument("--identity", required=True, type=Path)
    draft.add_argument("--out", required=True, type=Path)
    draft.add_argument("--type", choices=("erasure", "access"), default="erasure")
    draft.add_argument("--lang", choices=("en", "fi"), default="en")
    draft.add_argument("--date", type=date_argument, help="Letter date (default: today).")
    draft.add_argument(
        "--mark-sent", action="store_true", help="Mark tracker rows sent on the letter date."
    )
    due = commands.add_parser("due")
    due.add_argument("--tracker", required=True, type=Path)
    due.add_argument("--today", type=date_argument, default=None)
    period = commands.add_parser("deadline")
    period.add_argument("--received", type=date_argument, required=True)
    period.add_argument("--extended", action="store_true")
    return result


def draft(args: argparse.Namespace) -> None:
    identity = read_identity(args.identity)
    services = read_services(args.services)
    request_date = args.date or date.today()
    documents = []
    rows = []
    for index, service in enumerate(services, 1):
        service["request_type"] = service.get("request_type") or args.type
        service["language"] = service.get("language") or args.lang
        filename = (
            f"{index:02d}-{slug(service['service'])}"
            f"-{service['request_type']}-{service['language']}.txt"
        )
        documents.append((filename, render_request(identity, service, request_date)))
        rows.append(draft_row(service, request_date if args.mark_sent else None))
    prepare_output(args.out)
    for filename, content in documents:
        path = args.out / filename
        try:
            with exclusive_file(path) as target:
                target.write(content)
        except OSError as exc:
            raise InputError(path, 1, "Cannot write output file.") from exc
    path = args.out / "tracker.csv"
    try:
        with exclusive_file(path) as target:
            write_tracker(target, rows)
    except OSError as exc:
        raise InputError(path, 1, "Cannot write output file.") from exc
    status = "marked sent" if args.mark_sent else "left as draft (not marked sent)"
    print(f"Created {len(documents)} drafts and 1 tracker in {str(args.out)!r}. Rows {status}.")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(errors="backslashreplace")
    args = parser().parse_args(argv)
    try:
        if args.command == "draft":
            draft(args)
        elif args.command == "deadline":
            print(deadline(args.received, extended=args.extended).isoformat())
            months = "Three calendar months" if args.extended else "One calendar month"
            print(
                f"{months} from receipt; weekends move to Monday; public holidays are not checked."
            )
        else:
            today = args.today or date.today()
            actions = due_actions(args.tracker, today)
            if not actions:
                print(f"Nothing due on {today.isoformat()}.")
            for service, status, action, when in actions:
                print(f"{service} | {status} | {action} | {when.isoformat()}")
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except DateRangeError:
        print("Error: date out of range.", file=sys.stderr)
        return 1
    return 0
