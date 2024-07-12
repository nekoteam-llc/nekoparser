<img src="https://github.com/user-attachments/assets/fcd863c9-ee42-441e-836a-5ab709ccef52" width="200">

> Extensible parser for HTML pages, XLSX tables, PDF documents. Extracts data in the format known to [Satu.kz](https://satu.kz) and optionally uploads it to the website.

![chrome_pmYVmkxU9p](https://github.com/user-attachments/assets/62980288-6e9a-4292-8053-a37cb6d84c81)
![chrome_vzb1r5Qi1o](https://github.com/user-attachments/assets/01c9c55c-0bae-4dc1-88f7-cbd7ff2661e3)
![chrome_PuR9TZehuY](https://github.com/user-attachments/assets/808a98e3-8dba-4b43-9830-7316ba9dbd86)

## How to use
1. Install the [chrome plugin](https://github.com/nekoteam-llc/nekoparser/tree/master/chrome-plugin)
2. Log in to https://nekoparser.dan.tatar using CloudFlare Acccess
3. Add the source
4. Follow the instructions of the extension

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
