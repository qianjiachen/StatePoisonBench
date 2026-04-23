import traceback

from run_main_table import main


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
