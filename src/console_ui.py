
"""
Console UI module for ONYX - Advanced AI Assistant.
Provides styled panels, spinners, and Markdown rendering with a modern security-tool aesthetic.
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
from rich.align import Align
from rich.console import Group
import re
import random

# Custom theme for ONYX - Modern Security Vibe
custom_theme = Theme({
    "info": "bold cyan",
    "warning": "bold yellow", 
    "error": "bold red",
    "success": "bold green",
    "tool": "bold magenta",
    "user_prompt": "bold green",
    "system": "dim white",
    "hacker_green": "bold #00ff00",
    "hacker_red": "bold #ff0000",
})

console = Console(theme=custom_theme)

# NYV AI Banner
NYV_BANNER = r"""
                                _   _  __     __ __      __       _    ___ 
                                | \ | | \ \   / / \ \    / /      / \  |_ _|
                                |  \| |  \ \_/ /   \ \  / /      / _ \  | | 
                                | |\  |    | |      \ \/ /      / ___ \ | | 
                                |_| \_|    |_|       \__/      /_/   \_\___|
                                
                                                AGENT AI SYSTEM                              
                                                [bold red]SYSTEM: ONLINE[/bold red] ⚡
"""

def display_welcome():
    """Display the welcome panel with ONYX banner and author info."""
    # Banner (left-aligned by default, but we'll use Text for consistency)
    banner_text = Text.from_markup(NYV_BANNER, style="bold green")
    
    # Subtitle left-aligned
    subtitle_text = Text("  Advanced AI System 🔒\n", style="bold red", justify="left")
    
    # Author info in a table
    info_table = Table.grid(padding=(0, 1))
    info_table.add_column(justify="right", style="dim")
    info_table.add_column(justify="left")
    
    info_table.add_row("  Author:", "[bold cyan]Pentesting-28 🕷️[/bold cyan]")
    info_table.add_row("  GitHub:", "[underline blue]https://github.com/Pentesting-28[/underline blue]")
    
    # Exit instruction left-aligned
    exit_text = Text()
    exit_text.append("\n  Type ", style="dim")
    exit_text.append("exit", style="bold red")
    exit_text.append(" to terminate session\n", style="dim")
    
    # Group all elements
    welcome_group = Group(
        banner_text,
        subtitle_text,
        Text("  --------------------------------", style="dim green"),
        info_table,
        Text("  --------------------------------", style="dim green"),
        exit_text
    )
    
    panel = Panel(
        welcome_group,
        border_style="bold green",
        title="[bold red]☠️  NYV TERMINAL ☠️  [/bold red]",
        subtitle="[dim]v1.0.0[/dim]",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()


def display_thinking():
    """Return a Live context manager with a thinking spinner."""
    spinner_text = Text()
    spinner_text.append(" Analyzing", style="bold green")
    spinner_text.append("...", style="dim green")
    
    return Live(
        Panel(
            spinner_text,
            border_style="green",
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
        self._frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    
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
        text.append(f" {frame} ", style="bold red")
        text.append("Processing Data...", style="bold green")
        return Panel(text, border_style="dim green", padding=(0, 1))
    
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
            title="[bold green]🤖 NYV AI[/bold green]",
            title_align="left",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)
    except Exception:
        # Fallback to plain text if Markdown parsing fails
        console.print(Panel(
            display_content,
            title="[bold green]🤖 NYV AI[/bold green]",
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
        text.append(f"Initializing Module: ", style="dim green")
        text.append(tool_name, style="bold magenta")
        
        panel = Panel(
            text,
            border_style="yellow",
            padding=(0, 1)
        )
        console.print(panel)


def display_tool_result(tool_name: str, result: str):
    """Display tool execution result."""
    # Truncate long results for display (show more for better visibility)
    max_display = 2000
    display_result = result[:max_display] + "..." if len(result) > max_display else result
    
    content = Text()
    content.append(f"Module: ", style="dim green")
    content.append(tool_name, style="bold magenta")
    content.append(f"\n\n{display_result}", style="dim white")
    
    panel = Panel(
        content,
        title="[bold blue]💾 SYSTEM OUTPUT[/bold blue]",
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
        title="[bold red]SYSTEM ERROR[/bold red]",
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
    text.append("\n💀 ", style="bold red")
    text.append("Session Terminated. Stay safe.", style="bold green")
    console.print(text)
    console.print()


def prompt_user() -> str:
    """Display styled user prompt and get input."""
    try:
        # Kali/Parrot style prompt
        prompt_text = Text()
        prompt_text.append("┌──(", style="bold blue")
        prompt_text.append("nyv㉿ai", style="bold red")
        prompt_text.append(")-[", style="bold blue")
        prompt_text.append("~", style="bold white")
        prompt_text.append("]\n└─", style="bold blue")
        prompt_text.append("$ ", style="bold white")
        
        console.print(prompt_text, end="")
        user_input = input()
        # console.print()  # Add spacing after input
        return user_input.strip()
    except (EOFError, KeyboardInterrupt):
        return "exit"


def display_user_message(message: str):
    """Display the user's message in a styled format."""
    text = Text()
    text.append("root@NYV: ", style="bold red")
    text.append(message, style="bold white")
    console.print(text)
    console.print()


def display_debug(title: str, data: dict):
    """Display debug information in a styled panel."""
    from rich.syntax import Syntax
    
    content = Text()
    content.append(f"🐛 {title}\n\n", style="bold yellow")
    
    for key, value in data.items():
        content.append(f"{key}: ", style="bold dim")
        
        # Handle multiline values like tracebacks
        value_str = str(value)
        if "\n" in value_str:
            content.append("\n", style="dim")
            # Indent multiline content
            for line in value_str.split("\n"):
                content.append(f"    {line}\n", style="dim red")
        else:
            content.append(f"{value_str}\n", style="dim white")
    
    panel = Panel(
        content,
        title="[bold yellow]DEBUG TRACE[/bold yellow]",
        title_align="left",
        border_style="yellow",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()
