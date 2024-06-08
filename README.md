# MegaParser

## Description
Extensible parser for HTML pages, XLSX tables, PDF documents. Extracts data in the format known to [Satu.kz](https://satu.kz) and optionally uploads it to the website.

## Deployment
1. Install docker and `compose` plugin
2. Clone the repository
3. Run `docker compose up -d`

## Development
1. Install `poetry`: `pip install poetry -U`
2. Install packages: `poetry install`
3. Run `pre-commit install -f --install-hooks`
4. Activate the virtual environment: `poetry shell`

## Conventions
- Use `ruff` and `eslint` for code formatting (included in pre-commit hooks)
- Do not push the code, that does not pass CI
- Use [gitmoji.dev](https://gitmoji.dev/) for commit messages

## Credits
- [Daniil Gazizullin](https://github.com/hikariatama)
- [Igor Kuzmenkov](https://github.com/IgorDuino)
- [Almaz Andukov](https://github.com/andiazdi)
- [Timur Struchkov](https://github.com/AlfyK1s)
- Ksenia Korchagina
