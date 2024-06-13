# MegaParser

## Description
Extensible parser for HTML pages, XLSX tables, PDF documents. Extracts data in the format known to [Satu.kz](https://satu.kz) and optionally uploads it to the website.

## Deployment
1. Install docker and `docker compose`
2. Clone the repository
3. Run `docker compose up -d --build`

## Development
1. Install `poetry`: `pip install poetry -U`
2. Install packages: `poetry install`
3. Run `pre-commit install -f --install-hooks`
4. Activate the virtual environment: `poetry shell`

## Conventions
- Use `ruff` for code formatting (be sure to link it to `pyproject.toml` configuration)
- Do not submit the code, that does not pass CI
- Do not commit directly to `master` branch
- Try to force all pull requests to be reviewed by at least one other person
- Use [gitmoji.dev](https://gitmoji.dev/) for commit messages

## Credits
- [Daniil Gazizullin](https://github.com/hikariatama)
- Igor Kuzmenkov
- Almaz Andukov
- Timur Struchkov
- Ksenia Korchagina
