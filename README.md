# DotDev

## Run

```shell
uv run python scripts/generate_mirror_days.py
uv run mkdocs serve --livereload
```

The deployed site regenerates the current year's mirror-day table every day via
GitHub Actions. Pass a year to preview a different year locally:

```shell
uv run python scripts/generate_mirror_days.py 2027
```
