
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

# ONYX Banner
ONYX_BANNER = r"""
   ____  _   _ __   ____  __
  / __ \| \ | |\ \ / /\ \/ /
 | |  | |  \| | \ V /  \  / 
 | |  | | . ` |  > <    > <  
 | |__| | |\  | / . \  / . \ 
  \____/|_| \_|/_/ \_\/_/ \_\
                             
    [bold red]SYSTEM: ONLINE[/bold red] ⚡
"""

def display_welcome():
    """Display the welcome panel with ONYX banner and author info."""
    welcome_text = Text()
    welcome_text.append(ONYX_BANNER, style="bold green")
    welcome_text.append("\n  Advanced AI System 🔒\n", style="bold red")
    welcome_text.append("  --------------------------------\n", style="dim green")
    welcome_text.append("  Author: ", style="dim")
    welcome_text.append("Pentesting-28 🕷️\n", style="bold cyan")
    welcome_text.append("  GitHub: ", style="dim")
    welcome_text.append("https://github.com/Pentesting-28\n", style="underline blue")
    welcome_text.append("  --------------------------------\n\n", style="dim green")
    welcome_text.append("  Type ", style="dim")
    welcome_text.append("exit", style="bold red")
    welcome_text.append(" to terminate session\n", style="dim")
    
    panel = Panel(
        welcome_text,
        border_style="bold green",
        title="[bold red]☠️ ONYX TERMINAL ☠️[/bold red]",
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
            title="[bold green]🤖 ONYX AI[/bold green]",
            title_align="left",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)
    except Exception:
        # Fallback to plain text if Markdown parsing fails
        console.print(Panel(
            display_content,
            title="[bold green]🤖 ONYX AI[/bold green]",
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
    # Truncate long results for display
    display_result = result[:500] + "..." if len(result) > 500 else result
    
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
        prompt_text.append("onyx㉿ai", style="bold red")
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
    text.append("root@ONYX: ", style="bold red")
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
