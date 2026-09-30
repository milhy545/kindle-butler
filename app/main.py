import typer
import os
import datetime
import logging
import subprocess  # nosec B404
import re
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from app.usb_detector import KindleDetector
from app.organizer import KindleOrganizer
from app.metadata import MetadataExtractor
from app.ai_client import AIClient
from app.config import ButlerConfig
from app.content_processor import ContentProcessor

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = typer.Typer(help="Kindle Butler: Your smart Kindle manager.")
console = Console()
__version__ = "1.0.0"
DEFAULT_SYNC_STAGE = Path("sync_stage")
_SAFE_REMOTE_HOST = re.compile(r"^[A-Za-z0-9.-]+$")


def get_log_path(kindle_root: str) -> Path:
    return Path(kindle_root) / "butler_run.log"


def log_to_kindle(kindle_root: str, message: str):
    log_path = get_log_path(kindle_root)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def version_callback(value: bool):
    if value:
        console.print(f"Kindle Butler version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show version and exit."
    ),
):
    pass


@app.command()
def check():
    """
    Check system health and Kindle connection.
    """
    console.print("\n🔍 [bold]Kontrola systému...[/bold]")
    config = ButlerConfig()

    cfg_key = config.get_env("LLM_API_KEY")
    env_key = os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if cfg_key or env_key:
        source = "konfiguraci" if cfg_key else "prostředí"
        console.print(f"✅ LLM API Key nalezen (v {source}).")
    else:
        console.print("⚠️ [yellow]LLM API Key nebyl nalezen. AI funkce nebudou dostupné.[/yellow]")

    detector = KindleDetector()
    kindle_path = detector.find_kindle_path()
    if kindle_path:
        console.print(f"✅ Kindle nalezen v: {kindle_path}")
    else:
        console.print("❌ [red]Kindle nebyl nalezen.[/red]")


@app.command()
def start():
    """
    Main interactive entry point for Kindle Butler.
    """
    console.print(Panel.fit("🚀 [bold blue]Kindle Butler v1.0.0[/bold blue]\n[italic]Your smart librarian is ready.[/italic]", title="Welcome"))

    config = ButlerConfig()
    current_cfg = config.load()

    env_key = os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not current_cfg.get("provider") or (not config.get_env("LLM_API_KEY") and not env_key):
        console.print("\n[yellow]Looks like it's your first time or config is missing.[/yellow]")
        provider = Prompt.ask("Kterého LLM providera chcete použít?", choices=["Gemini"], default="Gemini")

        auth_method = "API Key"
        api_key = Prompt.ask(f"Vložte svůj {provider} API Key", password=True)

        console.print(f"🔄 Testování spojení s {provider}...")
        client = AIClient(api_key=api_key)

        if not client.client:
            console.print("❌ [red]Chyba: AI klient nebyl inicializován. Zkontrolujte API klíč.[/red]")
            raise typer.Exit(code=1)

        try:
            client.client.models.generate_content(
                model=client.model_name,
                contents="test"
            )
            console.print("✅ [green]LLM ověření proběhlo úspěšně![/green]")
            config.save({"provider": provider, "auth_method": auth_method})
            config.set_env("LLM_API_KEY", api_key)
            config.set_env("GEMINI_API_KEY", api_key)
        except Exception as e:
            console.print(f"❌ [red]Chyba při ověřování LLM:[/red] {e}")
            raise typer.Exit(code=1)

    action = Prompt.ask(
        "\nCo budeme dnes dělat?",
        choices=["uklidit", "importovat", "odeslat emailem", "konec"],
        default="uklidit"
    )

    if action == "uklidit":
        sync(auto=False, use_ai=True, backup=True)
    elif action == "importovat":
        import_docs()
    elif action == "odeslat emailem":
        email_docs()
    else:
        console.print("👋 Měj se, Milhy!")


def _perform_sync(auto: bool, use_ai: bool, backup: bool):
    """
    Internal helper to perform the actual sync logic with clean boolean types.
    """
    console.print("🔍 [bold]Sync Start[/bold]")
    kindle_path = os.environ.get("KINDLE_BUTLER_MOCK_PATH")
    if not kindle_path:
        detector = KindleDetector()
        kindle_path = detector.find_kindle_path()

    if not kindle_path:
        console.print("❌ [red]Kindle nebyl nalezen.[/red]")
        if auto:
            raise typer.Exit(code=1)
        return

    console.print(f"📍 [blue]Kindle nalezen v:[/blue] {kindle_path}")
    log_to_kindle(kindle_path, f"Butler Smart Sync Start (auto={auto}, use_ai={use_ai}, backup={backup})")

    extractor = MetadataExtractor()
    cfg = ButlerConfig()

    ai_client = None
    if use_ai:
        api_key = cfg.get_env("LLM_API_KEY") or os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if api_key:
            ai_client = AIClient(api_key=api_key)
        else:
            console.print("⚠️ [yellow]AI klíč nenalezen (zkuste nastavit LLM_API_KEY v prostředí), pokračuji bez AI.[/yellow]")
            use_ai = False

    organizer = KindleOrganizer(kindle_path)

    files = organizer.scan_documents()
    if not files:
        console.print("📭 [yellow]Žádné nové dokumenty k uklizení.[/yellow]")
        return

    console.print(f"📦 Found {len(files)} documents. Starting organization...")
    log_to_kindle(kindle_path, f"Found {len(files)} documents. Starting organization...")

    with console.status(f"[bold green]Uklízím {len(files)} dokumentů..."):
        for file_path in files:
            meta = extractor.extract(file_path)

            author = meta["author"]
            title = meta["title"]

            if author == "Unknown":
                current_parent = file_path.parent
                if current_parent != Path(kindle_path) / "documents":
                    author = current_parent.name

            if use_ai and ai_client:
                normalized = ai_client.normalize_metadata(author, title)
                author = normalized.get("author", author)
                title = normalized.get("title", title)

            target_path = organizer.get_target_path(file_path, author)

            if file_path.resolve() != target_path.resolve():
                if backup:
                    organizer.create_backup(file_path)

                organizer.organize_file(file_path, author)
                console.print(f"  ✅ [green]Uklizeno:[/green] {author} - {title}")

    console.print("\n✨ [bold]Vše je uklizeno![/bold]")
    log_to_kindle(kindle_path, "Organization complete! Your Kindle is now tidy.")


@app.command()
def sync(
    auto: bool = typer.Option(False, "--auto", help="Automatický režim bez dotazů."),
    use_ai: bool = typer.Option(True, "--use-ai/--no-use-ai", help="Použít AI pro metadata."),
    backup: bool = typer.Option(True, help="Vytvořit zálohu před přesunem.")
):
    """
    Sync and organise Kindle documents.
    """
    _perform_sync(auto, use_ai, backup)


def email_docs():
    """
    Send documents via email to Kindle.
    """
    console.print("\n📧 [bold]Odeslat dokumenty emailem na Kindle[/bold]")
    config = ButlerConfig()
    current_cfg = config.load()

    kindle_email = current_cfg.get("kindle_email")
    if not kindle_email:
        kindle_email = Prompt.ask("Zadejte svůj cílový Kindle email (např. user@kindle.com)")
        current_cfg["kindle_email"] = kindle_email
        config.save(current_cfg)

    smtp_user = current_cfg.get("smtp_user") or config.get_env("SMTP_USER")
    smtp_pass = current_cfg.get("smtp_pass") or config.get_env("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        console.print("[yellow]Je potřeba nastavit SMTP přihlašovací údaje (odesílatel).[/yellow]")
        smtp_user = Prompt.ask("Zadejte svůj odesílací email (např. user@gmail.com)")
        smtp_pass = Prompt.ask("Zadejte své heslo (nebo aplikační heslo)", password=True)
        current_cfg["smtp_user"] = smtp_user
        current_cfg["smtp_pass"] = smtp_pass
        config.save(current_cfg)
        config.set_env("SMTP_USER", smtp_user)
        config.set_env("SMTP_PASS", smtp_pass)

    source_dir = Path.home() / "Downloads"
    if not source_dir.exists():
        console.print(f"⚠️ [yellow]Složka {source_dir} nebyla nalezena.[/yellow]")
        return

    console.print(f"Skenuji složku [blue]{source_dir}[/blue]...")
    valid_exts = {'.pdf', '.mobi', '.azw3', '.epub', '.kfx'}
    files_to_email = [f for f in source_dir.iterdir() if f.suffix.lower() in valid_exts]

    if not files_to_email:
        console.print("📭 Žádné kompatibilní dokumenty v Downloads k odeslání.")
        return

    for i, f in enumerate(files_to_email):
        console.print(f" [{i}] {f.name}")

    choice = Prompt.ask("Které soubory chcete odeslat? (např. 0,1,3 nebo 'vse')")

    to_send = []
    if choice.lower() == 'vse':
        to_send = files_to_email
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(",")]
            to_send = [files_to_email[i] for i in indices]
        except Exception:
            console.print("❌ Neplatná volba.")
            return

    import smtplib
    from email.message import EmailMessage
    import mimetypes

    smtp_server = current_cfg.get("smtp_server", "smtp.gmail.com")
    smtp_port = current_cfg.get("smtp_port", 587)

    successfully_sent = []
    with console.status(f"[bold green]Odesílám {len(to_send)} dokumentů na {kindle_email}..."):
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)

                for f in to_send:
                    try:
                        msg = EmailMessage()
                        msg['Subject'] = 'Kindle Butler Delivery'
                        msg['From'] = smtp_user
                        msg['To'] = kindle_email
                        msg.set_content("Sent via Kindle Butler.")

                        ctype, encoding = mimetypes.guess_type(str(f))
                        if ctype is None or encoding is not None:
                            ctype = 'application/octet-stream'
                        maintype, subtype = ctype.split('/', 1)

                        with open(f, 'rb') as fp:
                            msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=f.name)

                        server.send_message(msg)
                        console.print(f"  ➡️ [green]Odesláno:[/green] {f.name}")
                        successfully_sent.append(f)
                    except Exception as e:
                        console.print(f"  ❌ [red]Chyba při odesílání {f.name}:[/red] {e}")
        except Exception as e:
            console.print(f"❌ [red]Chyba při spojení se SMTP serverem:[/red] {e}")
            return

    if successfully_sent:
        if Confirm.ask(f"\nSmazat {len(successfully_sent)} odeslaných souborů z Downloads?"):
            for f in successfully_sent:
                f.unlink()
            console.print("✅ Původní soubory smazány.")


def import_docs():
    """
    Import documents from Host to Kindle.
    """
    console.print("\n📂 [bold]Import dokumentů[/bold]")
    source_dir = Path.home() / "Downloads"
    if not source_dir.exists():
        console.print(f"⚠️ [yellow]Složka {source_dir} nebyla nalezena.[/yellow]")
        return

    console.print(f"Skenuji složku [blue]{source_dir}[/blue]...")

    valid_exts = {'.pdf', '.mobi', '.azw3', '.epub', '.kfx'}
    files_to_import = [f for f in source_dir.iterdir() if f.suffix.lower() in valid_exts]

    if not files_to_import:
        console.print("📭 Žádné kompatibilní dokumenty v Downloads.")
        return

    for i, f in enumerate(files_to_import):
        console.print(f" [{i}] {f.name}")

    choice = Prompt.ask("Které soubory chcete importovat? (např. 0,1,3 nebo 'vse')")

    to_move = []
    if choice.lower() == 'vse':
        to_move = files_to_import
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(",")]
            to_move = [files_to_import[i] for i in indices]
        except Exception:
            console.print("❌ Neplatná volba.")
            return

    kindle_path = os.environ.get("KINDLE_BUTLER_MOCK_PATH")
    if not kindle_path:
        detector = KindleDetector()
        kindle_path = detector.find_kindle_path()

    if not kindle_path:
        console.print("❌ [red]Kindle nebyl nalezen.[/red]")
        return

    target_dir = Path(kindle_path) / "documents"
    organizer = KindleOrganizer(kindle_path)

    successfully_imported = []
    with console.status("[bold green]Importuji..."):
        import shutil
        for f in to_move:
            try:
                target_path = target_dir / f.name
                if target_path.exists():
                    organizer.create_backup(target_path)

                shutil.copy2(str(f), str(target_path))
                console.print(f"  ➡️ [green]Importováno:[/green] {f.name}")
                successfully_imported.append(f)
            except Exception as e:
                console.print(f"  ❌ [red]Chyba při importu {f.name}:[/red] {e}")

    if successfully_imported:
        if Confirm.ask(f"\nSmazat {len(successfully_imported)} původních souborů z Downloads?"):
            for f in successfully_imported:
                f.unlink()
            console.print("✅ Původní soubory smazány.")

    console.print("\n✅ Import dokončen. Spouštím automatický úklid na Kindlu...")
    _perform_sync(auto=False, use_ai=True, backup=True)


@app.command()
def email():
    """
    Spustí proces odeslání dokumentů na Kindle přes email.
    """
    email_docs()


@app.command()
def enhance(file_path: Path, target_lang: str = "cs"):
    """
    Vylepší a přeloží EPUB dokument pomocí AI (např. převod tabulek na plynulý text).
    """
    if not file_path.exists() or file_path.suffix.lower() != '.epub':
        console.print("❌ [red]Zadaný soubor neexistuje nebo není ve formátu EPUB.[/red]")
        raise typer.Exit(1)

    console.print(f"\n✨ [bold]AI Vylepšení obsahu[/bold] (Cíl: {target_lang})")

    cfg = ButlerConfig()
    api_key = cfg.get_env("LLM_API_KEY") or os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print("❌ [red]Chybí LLM_API_KEY (nebo GEMINI_API_KEY) pro AI vylepšení.[/red]")
        raise typer.Exit(1)

    from rich.progress import Progress

    ai_client = AIClient(api_key=api_key)
    processor = ContentProcessor(ai_client=ai_client)

    with Progress() as progress:
        try:
            out_path = processor.process_epub(file_path, target_lang=target_lang, progress=progress)
            console.print(f"\n✅ [bold green]Dokument úspěšně vylepšen:[/bold green] {out_path.name}")
        except Exception as e:
            console.print(f"\n❌ [red]Chyba při vylepšování:[/red] {e}")
            raise typer.Exit(1)


def _validate_remote_host(host: str) -> str:
    if not _SAFE_REMOTE_HOST.fullmatch(host):
        raise typer.BadParameter("Remote host may contain only letters, numbers, dots and hyphens.")
    if host.startswith("-") or ".." in host:
        raise typer.BadParameter("Remote host is not valid.")
    return host

@app.command()
def process(source: Path, title: str = "Unknown", author: str = "Milhy Butler", translate: bool = True):
    """Convert and optionally translate a document to AZW3."""
    if not source.exists() or source.suffix.lower() not in {".md", ".markdown"}:
        console.print("❌ [red]Zadaný soubor neexistuje nebo není ve formátu Markdown.[/red]")
        raise typer.Exit(1)

    console.print(f"🔄 Zpracovávám: [bold]{source.name}[/bold]")

    config = ButlerConfig()
    api_key = config.get_env("LLM_API_KEY") or os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")
    ai_client = AIClient(api_key=api_key) if api_key else None

    processor = ContentProcessor(ai_client=ai_client)
    output_dir = DEFAULT_SYNC_STAGE / "Manuals"
    output_dir.mkdir(parents=True, exist_ok=True)

    working_file = source
    if translate and ai_client:
        console.print("🌍 [blue]Překládám do češtiny pomocí AI...[/blue]")
        working_file = processor.translate_markdown(source, target_lang="cs")
        
        if working_file is None:
            console.print("❌ [red]Překlad selhal.[/red]")
            raise typer.Exit(1)

        # Update title if it was default
        if title == "Unknown":
            title = f"{source.stem} (CZ)"

    output_file = output_dir / f"{source.stem}.azw3"

    success = processor.convert_markdown_to_epub(working_file, output_file, title, author)
    if success:
        console.print(f"✅ Hotovo: [green]{output_file}[/green]")
        if working_file != source:
            working_file.unlink(missing_ok=True)
    else:
        console.print("❌ [red]Konverze selhala.[/red]")
        if working_file != source:
            working_file.unlink(missing_ok=True)
        raise typer.Exit(1)

@app.command()
def sync_wifi(
    ip: str = typer.Argument("192.168.0.58", help="Kindle SSH host or IP address."),
    delete: bool = typer.Option(False, "--delete", help="Delete remote files missing from the local sync stage."),
):
    """Sync staged files to Kindle and trigger library scan."""
    try:
        remote_host = _validate_remote_host(ip)
    except typer.BadParameter as e:
        console.print(f"❌ [red]Neplatný Kindle host:[/red] {e}")
        raise typer.Exit(1)

    console.print(f"🚀 Zahajuji Wi-Fi synchronizaci na [bold]{ip}[/bold]...")
    source_dir = DEFAULT_SYNC_STAGE
    ssh_key = Path.home() / ".ssh/unified_ecosystem_key_2026"

    if not source_dir.exists() or not any(path.is_file() for path in source_dir.rglob("*")):
        console.print(f"❌ [red]Sync stage je prázdný nebo neexistuje:[/red] {source_dir}")
        raise typer.Exit(1)

    remote = f"root@{remote_host}"
    ssh_base = ["ssh", "-i", str(ssh_key), "-p", "2222", remote]

    try:
        subprocess.run(  # nosec B603
            ssh_base + ["mkdir -p /mnt/us/documents/Butler/Manuals /mnt/us/documents/Butler/MyBooks"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        console.print(f"❌ [red]Nelze připravit cílové složky na Kindlu:[/red] {e}")
        raise typer.Exit(1)

    rsync_cmd = [
        "rsync", "-rtvz", "--no-p", "--no-g", "--no-o", "--delete",
        "-e", f"ssh -i {ssh_key} -p 2222",
        str(source_dir) + "/",
        f"{remote}:/mnt/us/documents/Butler/"
    ]
    if not delete:
        rsync_cmd.remove("--delete")

    try:
        subprocess.run(rsync_cmd, check=True)  # nosec B603
    except subprocess.CalledProcessError as e:
        console.print(f"❌ [red]Rsync synchronizace selhala:[/red] {e}")
        raise typer.Exit(1)

    console.print("🔄 Žádám Kindle o proskenování knihovny...")
    try:
        subprocess.run(  # nosec B603
            ssh_base + [
                'dbus-send --system --dest=com.lab126.volumd /com/lab126/volumd '
                'com.lab126.volumd.rescan_all string:"/mnt/us/documents/Butler"'
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        console.print(f"❌ [red]Automatický sken knihovny selhal:[/red] {e}")
        raise typer.Exit(1)

    console.print("\n✨ [bold green]Synchronizace dokončena![/bold green]")

if __name__ == "__main__":
    app()
