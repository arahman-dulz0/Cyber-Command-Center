# Contributing

Contributions are welcome — bug reports, features, docs, and new plugins.

## Ways to contribute

- **Report a bug** — open an issue with steps to reproduce, expected vs. actual
  behaviour, and relevant logs (`docker compose logs -f discord-bot`).
- **Request a feature** — open an issue describing the problem it solves.
- **Send a pull request** — for fixes, features, or documentation.
- **Write a plugin** — a new monitor, enrichment source, or analyst tool. See
  **[plugins.md](plugins.md)**.

## Development setup

See the **[Developer Guide](developer-guide.md)** for repo layout, the repository
pattern, and how to run the stack locally. The short version:

```bash
cp .env.example .env                 # set DISCORD_TOKEN + DISCORD_GUILD_ID
docker compose --profile full up -d
```

## Pull request checklist

1. Keep changes focused — one logical change per PR.
2. Match the surrounding style (naming, comment density, idiom).
3. Reuse existing services/repositories rather than duplicating logic.
4. Byte-compile the bot before pushing: `cd services/discord-bot && python -m py_compile **/*.py`.
5. For the website: `cd website && npm run lint && npm run build` must pass.
6. **Never commit secrets.** `.env` is gitignored — scan your diff before pushing.
7. Update the docs when you change behaviour.

## Code of conduct

Be respectful and constructive. Assume good intent. Security research and
learning are the point of this project — keep it lawful and ethical.

## License

By contributing you agree that your contributions are licensed under the
project's [MIT License](../LICENSE).
