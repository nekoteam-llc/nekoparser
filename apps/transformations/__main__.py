"""Entrypoint"""

if __package__ != "transformations":
    import sys

    print(
        "\033[91m\033[1mPlease run this module with `python3 -m transformations`\033[0m",
        file=sys.stderr,
    )
    exit(1)


if __name__ == "__main__":
    from .serve import serve_all

    serve_all()
