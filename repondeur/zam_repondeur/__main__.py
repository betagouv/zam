from waitress import serve

from zam_repondeur import make_app


def main() -> None:
    app = make_app({})
    serve(app, host="0.0.0.0", port=6543)


if __name__ == "__main__":
    main()
