"""
Console UI module for Claude Code-like styling using Rich library.
Provides styled panels, spinners, and Markdown rendering for the AI agent interface.
"""
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text
from rich.style import Style
from rich.theme import Theme
from rich.syntax import Syntax
from rich.table import Table
import re

# Custom theme for Claude Code-like appearance
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow", 
    "error": "bold red",
    "success": "bold green",
    "tool": "bold magenta",
    "user_prompt": "bold cyan",
})

console = Console(theme=custom_theme)

# ASCII art banner
WELCOME_BANNER = """
╭─────────────────────────────────────────────────────────╮
│                                                         │
│       █████╗ ██╗      █████╗  ██████╗ ███████╗███╗   ██╗████████╗     │
│      ██╔══██╗██║     ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝     │
│      ███████║██║     ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║        │
│      ██╔══██║██║     ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║        │
│      ██║  ██║██║     ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║        │
│      ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝        │
│                                                         │
╰─────────────────────────────────────────────────────────╯
"""

SIMPLE_BANNER = r"""
   _   ___      _                  _   
  /_\ |_ _|    /_\  __ _ ___ _ __ | |_ 
 / _ \ | |    / _ \/ _` / -_) '  \|  _|
/_/ \_\___| |/_/ \_\__, \___|_|_|_|\__|
                    |___/               
"""


def display_welcome():
    """Display the welcome panel with ASCII art and agent info."""
    welcome_text = Text()
    welcome_text.append(SIMPLE_BANNER, style="bold cyan")
    welcome_text.append("\n\nYour AI Assistant with Tool Capabilities\n", style="dim")
    welcome_text.append("Type ", style="dim")
    welcome_text.append("exit", style="bold red")
    welcome_text.append(" to quit\n", style="dim")
    
    panel = Panel(
        welcome_text,
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()


def display_thinking():
    """Return a Live context manager with a thinking spinner."""
    spinner_text = Text()
    spinner_text.append(" Thinking", style="bold cyan")
    spinner_text.append("...", style="dim cyan")
    
    return Live(
        Panel(
            spinner_text,
            border_style="cyan",
            padding=(0, 1)
        ),
        console=console,
        refresh_per_second=10,
        transient=True
    )


class ThinkingSpinner:
    """Context manager for showing a thinking spinner."""
    
    def __init__(self):
        self.live = None
        self._frame = 0
        self._frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def __enter__(self):
        self.live = Live(
            self._create_panel(),
            console=console,
            refresh_per_second=12,
            transient=True
        )
        self.live.__enter__()
        return self
    
    def __exit__(self, *args):
        if self.live:
            self.live.__exit__(*args)
    
    def _create_panel(self):
        frame = self._frames[self._frame % len(self._frames)]
        text = Text()
        text.append(f" {frame} ", style="bold cyan")
        text.append("Thinking...", style="cyan")
        return Panel(text, border_style="dim cyan", padding=(0, 1))
    
    def update(self):
        self._frame += 1
        if self.live:
            self.live.update(self._create_panel())


def display_response(content: str):
    """Display AI response with Markdown rendering."""
    if not content:
        return
    
    # Clean up the content - remove tool JSON blocks for display
    display_content = re.sub(r'```json\s*\{.*?\}\s*```', '', content, flags=re.DOTALL).strip()
    
    if not display_content:
        return
    
    try:
        md = Markdown(display_content)
        panel = Panel(
            md,
            title="[bold green]✨ Assistant[/bold green]",
            title_align="left",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)
    except Exception:
        # Fallback to plain text if Markdown parsing fails
        console.print(Panel(
            display_content,
            title="[bold green]✨ Assistant[/bold green]",
            title_align="left",
            border_style="green",
            padding=(1, 2)
        ))
    console.print()


def display_tool_execution(tool_name: str, status: str = "executing"):
    """Display tool execution status."""
    if status == "executing":
        text = Text()
        text.append("⚡ ", style="bold yellow")
        text.append(f"Executing tool: ", style="dim")
        text.append(tool_name, style="bold magenta")
        
        panel = Panel(
            text,
            border_style="yellow",
            padding=(0, 1)
        )
        console.print(panel)


def display_tool_result(tool_name: str, result: str):
    """Display tool execution result."""
    # Truncate long results for display
    display_result = result[:500] + "..." if len(result) > 500 else result
    
    content = Text()
    content.append(f"Tool: ", style="dim")
    content.append(tool_name, style="bold magenta")
    content.append(f"\n\n{display_result}", style="dim")
    
    panel = Panel(
        content,
        title="[bold blue]🔧 Tool Result[/bold blue]",
        title_align="left",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()


def display_error(message: str):
    """Display error message in a styled panel."""
    text = Text()
    text.append("✖ ", style="bold red")
    text.append(message, style="red")
    
    panel = Panel(
        text,
        title="[bold red]Error[/bold red]",
        title_align="left",
        border_style="red",
        padding=(0, 1)
    )
    console.print(panel)
    console.print()


def display_info(message: str):
    """Display info message."""
    text = Text()
    text.append("ℹ ", style="bold cyan")
    text.append(message, style="cyan")
    console.print(text)


def display_goodbye():
    """Display goodbye message."""
    text = Text()
    text.append("\n👋 ", style="bold")
    text.append("Goodbye! See you next time.", style="bold cyan")
    console.print(text)
    console.print()


def prompt_user() -> str:
    """Display styled user prompt and get input."""
    try:
        prompt_text = Text()
        prompt_text.append("❯ ", style="bold cyan")
        console.print(prompt_text, end="")
        user_input = input()
        console.print()  # Add spacing after input
        return user_input.strip()
    except (EOFError, KeyboardInterrupt):
        return "exit"


def display_user_message(message: str):
    """Display the user's message in a styled format."""
    text = Text()
    text.append("You: ", style="bold blue")
    text.append(message, style="white")
    console.print(text)
    console.print()
