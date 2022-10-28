import uvicorn

from .main import app


def main() -> None:
    # to play with API run the script and visit http://127.0.0.1:8000/docs
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
