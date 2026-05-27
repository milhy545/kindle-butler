# Kindle Butler

**Kindle Butler** je Python CLI nastroj pro organizaci dokumentu na Kindle. Detekuje pripojeny Kindle, cte dostupna metadata, volitelne je normalizuje pres Gemini a presouva knihy do struktury \`documents/Author/Book.ext\`.

## Funkce

- Automaticka detekce Kindle pres USB.
- Volitelna AI normalizace metadat pres Gemini.
- Organizace dokumentu podle autora.
- EPUB enhancement pro technicke dokumenty pres AI zpracovani obsahu.
- Backup-first workflow pred presuny nebo prepisem souboru.
- Linux host instalace pres \`udev\` pravidlo.

## Rychly start

Pozadavky:

- Linux
- Python 3.12+
- \`uv\`
- Gemini API key pro AI funkce

Instalace:

\`\`\`bash
git clone https://github.com/milhy777/kindle-butler.git
cd kindle-butler
bash scripts/install_host.sh
\`\`\`

Interaktivni spusteni:

\`\`\`bash
uv run python main.py start
\`\`\`

## Příkazy

- `start`: spusti interaktivni menu.
- `sync`: jednorazove zorganizuje dokumenty na zarizeni.
- `check`: overi konfiguraci, API key a dostupnost Kindle.
- `email`: odesle dokumenty emailem rovnou do Kindle.
- `enhance`: zpracuje EPUB dokument pomoci AI (preklad, formatovani).
- `process`: prevede Markdown dokument do AZW3 (s volitelnym prekladem).
- `sync-wifi`: posle pripravene soubory na Kindle pres SSH/rsync a vyvola sken knihovny.

## Bezpecnost a soukromi

Standardni `sync` posila do AI jen autora a nazev pro normalizaci metadat. Prikazy `enhance` a `process` posilaji obsah dokumentu do Gemini, protoze jejich ucelem je obsahove prepracovani textu.

Tajemstvi ukladej pres host config/env flow, ne do repozitare. API klice a SMTP udaje patri do `~/.config/kindle-butler/env` nebo prostredi. Lokalni Kindle backupy, staging artefakty a osobni ebooky se nemaji commitovat.

## Vyvoj

Projekt pouziva `uv`, `pytest`, Typer a Python 3.12.

```bash
uv sync
uv run pytest -q
uv run pytest --cov=app -q
uv run bandit -r app -q
uv run pip-audit
```

Aktualni auditovana baseline je 49 passing testu s celkovym coverage priblizne 72 %. Coverage CLI a konfigurace je nad 65 %. Dulezite jsou hlavne testy backup-first chovani, EPUB roundtripu a bezpecneho zachazeni se secrets.
