from pathlib import Path


def main() -> None:
    path = Path("/root/agent-safety-bench/artifacts/main_table/main_result_table.md")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
