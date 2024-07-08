# MegaParser

## Description
Extensible parser for HTML pages, XLSX tables, PDF documents. Extracts data in the format known to [Satu.kz](https://satu.kz) and optionally uploads it to the website.

![изображение](https://github.com/nekoteam-llc/nekoparser/assets/157527321/75a827ea-23ba-4ff5-8204-fd4ad2b80055)
![изображение](https://github.com/nekoteam-llc/nekoparser/assets/157527321/6e1dbed4-59f9-4b20-ac0c-9a3d5191e8b2)

## How to use
1. Install [chrome plugin](https://github.com/nekoteam-llc/nekoparser/tree/master/chrome-plugin)
2. log onto https://nekoparser.dan.tatar/
3. Add source
4. Select prompted elements
5. Wait for parsing
6. Download data in CSV/JSON format

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
