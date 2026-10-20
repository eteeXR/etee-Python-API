# Documentation

The Sphinx source was migrated from the Bitbucket `tangi0/etee_python_api_docs`
repository's `main-OSS-API` branch. The API reference imports the `etee` package
in this repository, so it documents the code shipped alongside it.

## Preview locally

From the repository root, using Python 3.10:

```powershell
python -m venv .venv-docs
.venv-docs\Scripts\python -m pip install -r docs/requirements.txt
.venv-docs\Scripts\python -m sphinx -b html --fail-on-warning --keep-going docs/source docs/build/html
```

Open `docs/build/html/index.html` in a browser. On Linux or macOS, use
`.venv-docs/bin/python` instead of `.venv-docs\Scripts\python`.

Edit the `.rst` files and images under `docs/source` to update the site.
Generated HTML and the local environment are ignored by Git.

## Publish to GitHub Pages

1. In the repository's **Settings > Pages**, set **Source** to **GitHub Actions**.
2. Merge these files into `main`. The Documentation workflow checks pull
   requests and builds and deploys the site when `main` changes. It can also
   be started manually from the Actions tab.
3. Check the deployment at <https://eteexr.github.io/etee-Python-API/>.
4. Update any company website redirects or external links pointing to Read
   the Docs after verifying the new site. Those redirects are managed outside
   this repository; the old Read the Docs hostname is not controlled here.

The GitHub README links use the new Pages address and will work once the
first deployment succeeds. No Read the Docs account is needed to build or
host this documentation. The open source Read the Docs theme is retained.
