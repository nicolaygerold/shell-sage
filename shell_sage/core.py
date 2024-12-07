from dataclasses import dataclass
from typing import Optional, List
import typer
import sys
from functools import partial
from rich.console import Console
from rich.markdown import Markdown
import logging
import os
import subprocess
from .models.claude import Client, MODEL_TYPES, contents
from .pane import get_history
from .prompts import sp, ssp

@dataclass
class ShellSageConfig:
    """Configuration for ShellSage CLI"""
    code_theme: str = "monokai"
    code_lexer: str = "python"
    default_history_lines: int = 200
    log_level: str = "INFO"
    model: str = "claude-3-5-sonnet-20241022"  # Default to Sonnet
    log_usage: bool = False

class ShellSage:
    def __init__(self, config: ShellSageConfig):
        """Initialize ShellSage with configuration and dependencies

        Raises:
            ImportError: If required dependencies are missing
            ConnectionError: If Claude API connection fails
            ValueError: If invalid model specified
        """
        if config.model not in MODEL_TYPES:
            raise ValueError(f"Invalid model: {config.model}")

        self.config = config
        self.console = Console()
        self.setup_logging()
        self.setup_client()

    def setup_logging(self) -> None:
        """Configure logging with specified level"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_client(self) -> None:
        """Initialize Claude client with appropriate prompt templates

        Raises:
            ImportError: If prompt templates are not found
            ConnectionError: If Claude API connection fails
        """
        try:
            self.client = Client(
                model=self.config.model,
                log_usage=self.config.log_usage
            )
            try:
                self.ss = partial(self._get_completion, system=sp)
                self.sss = partial(self._get_completion, system=ssp)
            except NameError as e:
                raise ImportError(f"Failed to load prompt templates: {e}")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Claude client: {e}")

    def _get_completion(self, query: str, system: str) -> str:
        """Get completion from Claude with proper message formatting"""
        messages = [{"role": "user", "content": query}]
        response = self.client.get_completion(
            messages=messages,
            system=system,
            temperature=0.7
        )
        return response.content[0].text

    def get_tmux_context(self, pid: str, n: int) -> Optional[str]:
        """Get tmux context safely with proper error handling"""
        try:
            if not os.environ.get('TMUX'):
                return None
            return get_history(n, pid)
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Failed to get tmux history: {e}")
            return None

app = typer.Typer(help="ShellSage - Your CLI Teaching Assistant")

@app.command()
def main(
    query: List[str] = typer.Argument(..., help="The query to send to ShellSage"),
    pid: str = typer.Option("current", help="Tmux pane ID ('current', 'all', or specific ID)"),
    history_lines: int = typer.Option(200, "--lines", "-n", help="Number of history lines"),
    sassy: bool = typer.Option(False, "--sassy", "-s", help="Enable sassy mode"),
    theme: str = typer.Option("monokai", help="Code theme for responses"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """ShellSage CLI - Get help with shell commands and system administration"""
    try:
        config = ShellSageConfig(
            code_theme=theme,
            log_level="DEBUG" if verbose else "INFO"
        )
        sage = ShellSage(config)

        # Build context
        query_text = " ".join(query)
        context_parts = []

        # Get tmux context
        if tmux_context := sage.get_tmux_context(pid, history_lines):
            context_parts.append(f"<terminal_history>\n{tmux_context}\n</terminal_history>")

        # Get stdin if available
        if not sys.stdin.isatty():
            context_parts.append(f"<context>\n{sys.stdin.read()}</context>")

        # Construct final query
        full_query = "\n".join([*context_parts, f"<query>\n{query_text}\n</query>"])

        # Get and render response
        response = sage.sss(full_query) if sassy else sage.ss(full_query)
        sage.console.print(Markdown(
            contents(response),
            code_theme=config.code_theme,
            inline_code_lexer=config.code_lexer,
            inline_code_theme=config.code_theme
        ))

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()