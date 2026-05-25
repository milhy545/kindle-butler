# Tech Stack: Kindle Butler

## Language & Runtime
- **Python 3.12+**: Core logic.
- **uv**: Dependency management and environment isolation.

## Libraries
- **Typer**: CLI interface.
- **Rich**: Terminal UI, progress bars, and panels.
- **pyudev**: USB device detection on Linux.
- **google-genai**: Gemini AI integration for metadata normalization.
- **BeautifulSoup4 / EbookLib**: Metadata extraction for EPUB.
- **PyPDF2**: Metadata extraction for PDF.
- **mobi-python**: Metadata extraction for MOBI/AZW3.
- **pytest**: Test suite.
- **pytest-cov**: Coverage reporting.

## Infrastructure & Tools
- **udev**: Host-side auto-start trigger.
- **shutil / pathlib**: Filesystem operations.
- **logging**: Activity tracking on Kindle.

## Security
- **Local Askpass**: Secure credential handling (no keys in chat).
- **Environment Variables**: API keys managed via `.env` or system environment.
