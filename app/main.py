import typer
import os
import datetime
import logging
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

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = typer.Typer(help="Kindle Butler: Your smart Kindle manager.")
console = Console()
__version__ = "1.0.0"

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
    
    # Check LLM Key
    cfg_key = config.get_env("LLM_API_KEY")
    env_key = os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if cfg_key or env_key:
        source = "konfiguraci" if cfg_key else "prostředí"
        console.print(f"✅ LLM API Key nalezen (v {source}).")
    else:
        console.print("⚠️ [yellow]LLM API Key nebyl nalezen. AI funkce nebudou dostupné.[/yellow]")

    # Check Kindle
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
    console.print(Panel.fit("🚀 [bold blue]Kindle Butler v1.0[/bold blue]\n[italic]Your smart librarian is ready.[/italic]", title="Welcome"))
    
    config = ButlerConfig()
    current_cfg = config.load()
    
    # 1. Onboarding / Config Check
    env_key = os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not current_cfg.get("provider") or (not config.get_env("LLM_API_KEY") and not env_key):
        console.print("\n[yellow]Looks like it's your first time or config is missing.[/yellow]")
        provider = Prompt.ask("Kterého LLM providera chcete použít?", choices=["Gemini"], default="Gemini")
        
        # In a real app, we'd support OAuth here. For now, API Key.
        auth_method = "API Key"
        api_key = Prompt.ask(f"Vložte svůj {provider} API Key", password=True)
        
        # Test Connection
        console.print(f"🔄 Testování spojení s {provider}...")
        client = AIClient(api_key=api_key) 
        
        if not client.client:
            console.print("❌ [red]Chyba: AI klient nebyl inicializován. Zkontrolujte API klíč.[/red]")
            raise typer.Exit(code=1)

        try:
            # We must NOT use fallback here for validation
            from google.genai import errors
            test_res = client.client.models.generate_content(
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

    # 2. Action Choice
    action = Prompt.ask(
        "\nCo budeme dnes dělat?",
        choices=["uklidit", "importovat", "konec"],
        default="uklidit"
    )
    
    if action == "uklidit":
        sync(auto=False, use_ai=True, backup=True)
    elif action == "importovat":
        import_docs()
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
    
    # AI client is only needed if use_ai is True
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
    
    with console.status(f"[bold green]Uklízím {len(files)} dokumentů...") as status:
        for file_path in files:
            meta = extractor.extract(file_path)
            
            author = meta["author"]
            title = meta["title"]
            
            # If metadata is missing, check if it's already in an author folder
            # documents/Author/Book.ext -> parent is Author
            if author == "Unknown":
                current_parent = file_path.parent
                if current_parent != Path(kindle_path) / "documents":
                    author = current_parent.name
            
            if use_ai and ai_client:
                normalized = ai_client.normalize_metadata(author, title)
                author = normalized.get("author", author)
                title = normalized.get("title", title)
            
            target_path = organizer.get_target_path(file_path, author)
            
            # Only backup and move if it's NOT already in the right place
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
    Sync and organize Kindle documents.
    """
    _perform_sync(auto, use_ai, backup)

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
    
    # Simple scanner for host
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
        except:
            console.print("❌ Neplatná volba.")
            return

    # Find Kindle
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
                # Backup if target exists (Security Rule: Backup First)
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
        
    # Import here to avoid loading at startup if not used
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

if __name__ == "__main__":
    app()
