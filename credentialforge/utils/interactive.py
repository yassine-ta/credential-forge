"""Interactive terminal utilities for CredentialForge."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.shortcuts import confirm, radiolist_dialog, checkboxlist_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.formatted_text import HTML, FormattedText
from prompt_toolkit.widgets import RadioList
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.prompt import Prompt, Confirm

from .validators import Validators
from .exceptions import ValidationError as CFValidationError
from .logger import Logger


class InteractiveTerminal:
    """Interactive terminal for guided CredentialForge configuration."""
    
    def __init__(self):
        """Initialize interactive terminal."""
        self.console = Console()
        self.session = PromptSession()
        self.logger = Logger('interactive')
        self.config = {}
        
        # Setup enhanced style with selection indicators
        self.style = Style.from_dict({
            'prompt': '#00aa00',
            'error': '#ff0000',
            'success': '#00aa00',
            'warning': '#ffaa00',
            'selected': 'bg:#0066cc #ffffff',  # Blue background with white text
            'unselected': '#cccccc',           # Gray text for unselected
            'arrow': '#00ff00',                # Green arrows
            'marker': '#ff6600',               # Orange markers
        })
    
    def run(self):
        """Run the interactive terminal."""
        self._show_welcome()
        
        try:
            # Collect parameters
            self._collect_basic_parameters()
            self._collect_advanced_parameters()
            
            # Preview configuration
            self._preview_configuration()
            
            # Confirm and generate
            if self._confirm_generation():
                self._execute_generation()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            self.logger.error(f"Interactive mode error: {e}")
    
    def _simple_selection(self, title: str, options: List[tuple], default: str = None) -> str:
        """Simple selection interface that works reliably across all terminals."""
        if not options:
            return None
        
        # Find default index
        default_index = 0
        if default:
            for i, (value, _) in enumerate(options):
                if value == default:
                    default_index = i
                    break
        
        current_index = default_index
        
        while True:
            # Clear screen and show options
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            self.console.print(f"\n[bold cyan]{title}[/bold cyan]")
            self.console.print("[dim]Use number keys (1-{}) or Enter to confirm current selection[/dim]\n".format(len(options)))
            
            # Show options with current selection highlighted
            for i, (value, description) in enumerate(options):
                if i == current_index:
                    self.console.print(f"[bold green]→ {i+1}. {description}[/bold green]")
                else:
                    self.console.print(f"  {i+1}. {description}")
            
            self.console.print()
            
            # Get user input
            try:
                choice = input("Enter number (1-{}) or press Enter for current selection: ".format(len(options)))
                
                if choice.strip() == "":
                    # Enter pressed - use current selection
                    return options[current_index][0]
                else:
                    try:
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(options):
                            return options[choice_num - 1][0]
                        else:
                            self.console.print("[red]Invalid number. Please try again.[/red]")
                            input("Press Enter to continue...")
                    except ValueError:
                        self.console.print("[red]Please enter a valid number.[/red]")
                        input("Press Enter to continue...")
            except KeyboardInterrupt:
                return None

    def _enhanced_selection(self, title: str, options: List[tuple], default: str = None) -> str:
        """Enhanced selection with visual indicators, background colors, and arrows.
        
        Args:
            title: Selection title
            options: List of (value, description) tuples
            default: Default selected value
            
        Returns:
            Selected value
        """
        if not options:
            return None
        
        # Find default index
        default_index = 0
        if default:
            for i, (value, _) in enumerate(options):
                if value == default:
                    default_index = i
                    break
        
        current_index = default_index
        
        def _redraw_selection():
            """Redraw the selection interface with proper visual indicators."""
            # Use os.system('cls') for Windows or 'clear' for Unix-like systems for better clearing
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Print title and instructions
            self.console.print(f"\n[bold cyan]{title}[/bold cyan]")
            self.console.print("[dim]Use ↑↓ arrows (or W/S keys) to navigate, [*] indicates selection, Enter to confirm[/dim]\n")
            
            # Print options with proper highlighting
            for i, (value, description) in enumerate(options):
                if i == current_index:
                    # Selected option with bright background and markers
                    self.console.print(f"[bold green][*][/bold green] [bold blue]↑↓[/bold blue] [bold white on bright_blue]{description}[/bold white on bright_blue]")
                else:
                    # Unselected option with dim text
                    self.console.print(f"[dim]    {description}[/dim]")
            
            # Add some spacing
            self.console.print()
        
        # Initial draw
        _redraw_selection()
        
        while True:
            # Get user input with improved key detection
            try:
                import msvcrt
                import sys
                
                while True:
                    key = msvcrt.getch()
                    
                    # Handle arrow keys more robustly
                    if key == b'\xe0':  # Arrow key prefix on Windows
                        key2 = msvcrt.getch()
                        if key2 == b'H':  # Up arrow
                            current_index = max(0, current_index - 1)
                            _redraw_selection()
                            break
                        elif key2 == b'P':  # Down arrow
                            current_index = min(len(options) - 1, current_index + 1)
                            _redraw_selection()
                            break
                        elif key2 == b'M':  # Right arrow (alternative)
                            current_index = min(len(options) - 1, current_index + 1)
                            _redraw_selection()
                            break
                        elif key2 == b'K':  # Left arrow (alternative)
                            current_index = max(0, current_index - 1)
                            _redraw_selection()
                            break
                    elif key == b'\x1b':  # ESC sequence (Unix-like systems)
                        key2 = msvcrt.getch()
                        if key2 == b'[':
                            key3 = msvcrt.getch()
                            if key3 == b'A':  # Up arrow
                                current_index = max(0, current_index - 1)
                                _redraw_selection()
                                break
                            elif key3 == b'B':  # Down arrow
                                current_index = min(len(options) - 1, current_index + 1)
                                _redraw_selection()
                                break
                    elif key == b'\r':  # Enter
                        return options[current_index][0]
                    elif key == b'\x03':  # Ctrl+C
                        return None
                    elif key == b'w':  # 'w' key as alternative for up
                        current_index = max(0, current_index - 1)
                        _redraw_selection()
                        break
                    elif key == b's':  # 's' key as alternative for down
                        current_index = min(len(options) - 1, current_index + 1)
                        _redraw_selection()
                        break
            except ImportError:
                # Fallback for non-Windows systems
                try:
                    import tty
                    import termios
                    import select
                    import sys
                    
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    
                    try:
                        tty.setraw(sys.stdin.fileno())
                        ch = sys.stdin.read(1)
                        
                        if ch == '\x1b':  # ESC sequence
                            ch = sys.stdin.read(2)
                            if ch == '[A':  # Up arrow
                                current_index = max(0, current_index - 1)
                                _redraw_selection()
                            elif ch == '[B':  # Down arrow
                                current_index = min(len(options) - 1, current_index + 1)
                                _redraw_selection()
                        elif ch == '\r':  # Enter
                            return options[current_index][0]
                        elif ch == '\x03':  # Ctrl+C
                            return None
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except ImportError:
                    # Ultimate fallback - use simple input
                    self.console.print(f"\n[yellow]Enhanced selection not available, using simple mode[/yellow]")
                    for i, (value, description) in enumerate(options, 1):
                        self.console.print(f"  {i}. {description}")
                    
                    while True:
                        try:
                            choice = int(Prompt.ask("Select option (number)", console=self.console))
                            if 1 <= choice <= len(options):
                                return options[choice-1][0]
                            else:
                                self.console.print("[red]Invalid selection.[/red]")
                        except ValueError:
                            self.console.print("[red]Please enter a number.[/red]")
                        except KeyboardInterrupt:
                            return None
    
    def _enhanced_multi_selection(self, title: str, options: List[tuple], default_values: List[str] = None) -> List[str]:
        """Enhanced multi-selection with visual indicators, background colors, and arrows.
        
        Args:
            title: Selection title
            options: List of (value, description) tuples
            default_values: List of default selected values
            
        Returns:
            List of selected values
        """
        if not options:
            return []
        
        # Initialize selected items
        selected_values = set(default_values or [])
        current_index = 0
        
        def _redraw_multi_selection():
            """Redraw the multi-selection interface with proper visual indicators."""
            # Use os.system('cls') for Windows or 'clear' for Unix-like systems for better clearing
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Print title and instructions
            self.console.print(f"\n[bold cyan]{title}[/bold cyan]")
            self.console.print("[dim]Use ↑↓ arrows (or W/S keys) to navigate, Space (or T) to toggle, [*] indicates selection, Enter to confirm[/dim]\n")
            
            # Print options with proper highlighting
            for i, (value, description) in enumerate(options):
                if i == current_index:
                    if value in selected_values:
                        # Selected and current option with bright background and markers
                        self.console.print(f"[bold green][*][/bold green] [bold blue]↑↓[/bold blue] [bold white on bright_blue]{description}[/bold white on bright_blue]")
                    else:
                        # Current but not selected option with bright background
                        self.console.print(f"[bold blue][ ][/bold blue] [bold blue]↑↓[/bold blue] [bold white on bright_blue]{description}[/bold white on bright_blue]")
                else:
                    if value in selected_values:
                        # Selected but not current option
                        self.console.print(f"[bold green][*][/bold green] [dim]    {description}[/dim]")
                    else:
                        # Unselected option
                        self.console.print(f"[dim][ ]    {description}[/dim]")
            
            # Add some spacing
            self.console.print()
        
        # Initial draw
        _redraw_multi_selection()
        
        while True:
            # Get user input with improved key detection
            try:
                import msvcrt
                import sys
                
                while True:
                    key = msvcrt.getch()
                    
                    # Handle arrow keys more robustly
                    if key == b'\xe0':  # Arrow key prefix on Windows
                        key2 = msvcrt.getch()
                        if key2 == b'H':  # Up arrow
                            current_index = max(0, current_index - 1)
                            _redraw_multi_selection()
                            break
                        elif key2 == b'P':  # Down arrow
                            current_index = min(len(options) - 1, current_index + 1)
                            _redraw_multi_selection()
                            break
                        elif key2 == b'M':  # Right arrow (alternative)
                            current_index = min(len(options) - 1, current_index + 1)
                            _redraw_multi_selection()
                            break
                        elif key2 == b'K':  # Left arrow (alternative)
                            current_index = max(0, current_index - 1)
                            _redraw_multi_selection()
                            break
                    elif key == b'\x1b':  # ESC sequence (Unix-like systems)
                        key2 = msvcrt.getch()
                        if key2 == b'[':
                            key3 = msvcrt.getch()
                            if key3 == b'A':  # Up arrow
                                current_index = max(0, current_index - 1)
                                _redraw_multi_selection()
                                break
                            elif key3 == b'B':  # Down arrow
                                current_index = min(len(options) - 1, current_index + 1)
                                _redraw_multi_selection()
                                break
                    elif key == b' ':  # Space to toggle
                        value = options[current_index][0]
                        if value in selected_values:
                            selected_values.remove(value)
                        else:
                            selected_values.add(value)
                        _redraw_multi_selection()
                        break
                    elif key == b'\r':  # Enter
                        return list(selected_values)
                    elif key == b'\x03':  # Ctrl+C
                        return []
                    elif key == b'w':  # 'w' key as alternative for up
                        current_index = max(0, current_index - 1)
                        _redraw_multi_selection()
                        break
                    elif key == b's':  # 's' key as alternative for down
                        current_index = min(len(options) - 1, current_index + 1)
                        _redraw_multi_selection()
                        break
                    elif key == b't':  # 't' key as alternative for toggle
                        value = options[current_index][0]
                        if value in selected_values:
                            selected_values.remove(value)
                        else:
                            selected_values.add(value)
                        _redraw_multi_selection()
                        break
            except ImportError:
                # Fallback for non-Windows systems
                try:
                    import tty
                    import termios
                    import select
                    import sys
                    
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    
                    try:
                        tty.setraw(sys.stdin.fileno())
                        ch = sys.stdin.read(1)
                        
                        if ch == '\x1b':  # ESC sequence
                            ch = sys.stdin.read(2)
                            if ch == '[A':  # Up arrow
                                current_index = max(0, current_index - 1)
                                _redraw_multi_selection()
                            elif ch == '[B':  # Down arrow
                                current_index = min(len(options) - 1, current_index + 1)
                                _redraw_multi_selection()
                        elif ch == ' ':  # Space to toggle
                            value = options[current_index][0]
                            if value in selected_values:
                                selected_values.remove(value)
                            else:
                                selected_values.add(value)
                            _redraw_multi_selection()
                        elif ch == '\r':  # Enter
                            return list(selected_values)
                        elif ch == '\x03':  # Ctrl+C
                            return []
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except ImportError:
                    # Ultimate fallback - use simple input
                    self.console.print(f"\n[yellow]Enhanced multi-selection not available, using simple mode[/yellow]")
                    for i, (value, description) in enumerate(options, 1):
                        marker = "[*]" if value in selected_values else "[ ]"
                        self.console.print(f"  {marker} {i}. {description}")
                    
                    while True:
                        try:
                            choice = Prompt.ask("Select formats (comma-separated, e.g., 1,3,5) or 'done' to finish", console=self.console)
                            if choice.lower() == 'done':
                                break
                            
                            choices = [int(x.strip()) for x in choice.split(',')]
                            for c in choices:
                                if 1 <= c <= len(options):
                                    selected_values.add(options[c-1][0])
                                else:
                                    self.console.print(f"[red]Invalid selection: {c}[/red]")
                        except ValueError:
                            self.console.print("[red]Please enter valid numbers.[/red]")
                        except KeyboardInterrupt:
                            return []
                    
                    return list(selected_values)
    
    def _show_welcome(self):
        """Show welcome message."""
        welcome_text = """
[bold blue]CredentialForge Interactive Mode[/bold blue]

Welcome to the interactive configuration wizard!
This will guide you through setting up synthetic document generation.

[dim]Press Ctrl+C at any time to exit.[/dim]
        """
        
        self.console.print(Panel(welcome_text, title="Welcome", border_style="blue"))
    
    def _collect_basic_parameters(self):
        """Collect basic generation parameters."""
        self.console.print("\n[bold]Basic Configuration[/bold]")
        
        # Output directory
        while True:
            output_dir = Prompt.ask(
                "Output directory",
                default="./output",
                console=self.console
            )
            try:
                Validators.validate_output_directory(output_dir)
                self.config['output_dir'] = output_dir
                break
            except CFValidationError as e:
                self.console.print(f"[red]Error: {e}[/red]")
        
        # Number of files
        while True:
            try:
                num_files = int(Prompt.ask(
                    "Number of files to generate",
                    default="10",
                    console=self.console
                ))
                Validators.validate_num_files(num_files)
                self.config['num_files'] = num_files
                break
            except (ValueError, CFValidationError) as e:
                self.console.print(f"[red]Error: {e}[/red]")
        
        # File formats
        format_options = [
            # Email formats
            ("eml", "Email files (.eml)"),
            ("msg", "Outlook message files (.msg)"),
            
            # Microsoft Office Excel formats
            ("xlsm", "Excel macro-enabled workbooks (.xlsm)"),
            ("xlsx", "Excel spreadsheets (.xlsx)"),
            ("xltm", "Excel macro-enabled templates (.xltm)"),
            ("xls", "Excel 97-2003 workbooks (.xls)"),
            ("xlsb", "Excel binary workbooks (.xlsb)"),
            
            # Microsoft Office Word formats
            ("docx", "Word documents (.docx)"),
            ("doc", "Word 97-2003 documents (.doc)"),
            ("docm", "Word macro-enabled documents (.docm)"),
            ("rtf", "Rich Text Format (.rtf)"),
            
            # Microsoft Office PowerPoint formats
            ("pptx", "PowerPoint presentations (.pptx)"),
            ("ppt", "PowerPoint 97-2003 presentations (.ppt)"),
            
            # OpenDocument formats
            ("odf", "OpenDocument text (.odf)"),
            ("ods", "OpenDocument spreadsheets (.ods)"),
            ("odp", "OpenDocument presentations (.odp)"),
            
            # PDF format
            ("pdf", "PDF documents (.pdf)"),
            
            # Image formats
            ("png", "PNG images (.png)"),
            ("jpg", "JPEG images (.jpg)"),
            ("jpeg", "JPEG images (.jpeg)"),
            ("bmp", "Bitmap images (.bmp)"),
            
            # Visio formats
            ("vsd", "Visio 2003-2010 drawings (.vsd)"),
            ("vsdx", "Visio drawings (.vsdx)"),
            ("vsdm", "Visio macro-enabled drawings (.vsdm)"),
            ("vssx", "Visio stencils (.vssx)"),
            ("vssm", "Visio macro-enabled stencils (.vssm)"),
            ("vstx", "Visio templates (.vstx)"),
            ("vstm", "Visio macro-enabled templates (.vstm)"),
        ]
        
        try:
            # Use simple multi-selection as primary method (more reliable)
            selected_formats = []
            self.console.print("\n[bold cyan]📄 Select File Formats to Generate[/bold cyan]")
            self.console.print("[dim]Enter numbers separated by commas (e.g., 1,3,5) or press Enter for default[/dim]\n")
            
            for i, (key, desc) in enumerate(format_options, 1):
                self.console.print(f"  {i}. {desc}")
            
            # Add special options
            self.console.print(f"  {len(format_options) + 1}. [bold green]Select All Formats[/bold green]")
            self.console.print(f"  {len(format_options) + 2}. [bold blue]Select Common Formats (eml, xlsx, docx, pdf)[/bold blue]")
            
            while True:
                try:
                    choice = Prompt.ask("Select formats (comma-separated, e.g., 1,3,5) or press Enter for default (eml)", console=self.console)
                    if choice.strip() == "":
                        # Use default
                        selected_formats = ["eml"]
                        break
                    
                    choices = [int(x.strip()) for x in choice.split(',')]
                    
                    # Check for special options
                    if len(format_options) + 1 in choices:
                        # Select all formats
                        selected_formats = [key for key, desc in format_options]
                        self.console.print(f"[green]Selected all formats: {', '.join(selected_formats)}[/green]")
                        break
                    elif len(format_options) + 2 in choices:
                        # Select common formats
                        selected_formats = ["eml", "xlsx", "docx", "pdf"]
                        self.console.print(f"[green]Selected common formats: {', '.join(selected_formats)}[/green]")
                        break
                    else:
                        # Regular selection
                        for c in choices:
                            if 1 <= c <= len(format_options):
                                selected_formats.append(format_options[c-1][0])
                        
                        if selected_formats:
                            self.console.print(f"[green]Selected: {', '.join(selected_formats)}[/green]")
                            break
                        else:
                            self.console.print("[red]No valid formats selected.[/red]")
                except ValueError:
                    self.console.print("[red]Please enter numbers separated by commas.[/red]")
            
            if not selected_formats:
                self.console.print("[yellow]No formats selected, using default: eml[/yellow]")
                selected_formats = ["eml"]
        except Exception as e:
            # Fallback to simple selection if dialog fails
            self.console.print("\n[yellow]File format selection (fallback mode):[/yellow]")
            for i, (key, desc) in enumerate(format_options, 1):
                self.console.print(f"  {i}. {desc}")
            
            # Add special options to fallback
            self.console.print(f"  {len(format_options) + 1}. [bold green]Select All Formats[/bold green]")
            self.console.print(f"  {len(format_options) + 2}. [bold blue]Select Common Formats (eml, xlsx, docx, pdf)[/bold blue]")
            
            selected_formats = []
            while True:
                try:
                    choice = Prompt.ask("Select formats (comma-separated, e.g., 1,3,5) or 'done' to finish", console=self.console)
                    if choice.lower() == 'done':
                        break
                    
                    choices = [int(x.strip()) for x in choice.split(',')]
                    
                    # Check for special options
                    if len(format_options) + 1 in choices:
                        # Select all formats
                        selected_formats = [key for key, desc in format_options]
                        self.console.print(f"[green]Selected all formats: {', '.join(selected_formats)}[/green]")
                        break
                    elif len(format_options) + 2 in choices:
                        # Select common formats
                        selected_formats = ["eml", "xlsx", "docx", "pdf"]
                        self.console.print(f"[green]Selected common formats: {', '.join(selected_formats)}[/green]")
                        break
                    else:
                        # Regular selection
                        for c in choices:
                            if 1 <= c <= len(format_options):
                                selected_formats.append(format_options[c-1][0])
                        
                        if selected_formats:
                            self.console.print(f"[green]Selected: {', '.join(selected_formats)}[/green]")
                            break
                        else:
                            self.console.print("[red]No valid formats selected.[/red]")
                except ValueError:
                    self.console.print("[red]Please enter numbers separated by commas.[/red]")
        
        if not selected_formats:
            self.console.print("[red]At least one format must be selected![/red]")
            return self._collect_basic_parameters()
        
        self.config['formats'] = selected_formats
        
        # Topic selection
        self._collect_topic_parameters()
        
        # Language selection
        self._collect_language_parameters()
    
    def _collect_language_parameters(self):
        """Collect language configuration parameters."""
        self.console.print("\n[bold]🌍 Language Configuration[/bold]")
        
        # Import language mapper
        try:
            from ..utils.language_mapper import LanguageMapper
            language_mapper = LanguageMapper()
            
            # Get available languages
            available_languages = language_mapper.get_supported_languages()
            language_options = []
            
            for lang_code in available_languages:
                lang_name = language_mapper.get_language_name(lang_code)
                # Get company count for this language
                companies = language_mapper.get_companies_by_language(lang_code)
                company_count = len(companies)
                language_options.append((lang_code, f"{lang_name} ({lang_code}) - {company_count} companies"))
            
            # Add option for all languages
            language_options.insert(0, ("all", "All Languages (Random Selection)"))
            
            self.console.print("\n[cyan]Available languages with company counts:[/cyan]")
            for lang_code, desc in language_options:
                self.console.print(f"• {desc}")
            
            try:
                # Use multi-selection for languages (more flexible)
                selected_languages = []
                self.console.print("\n[bold cyan]🌍 Select Languages for Content Generation[/bold cyan]")
                self.console.print("[dim]Enter numbers separated by commas (e.g., 1,3,5) or press Enter for default[/dim]\n")
                
                for i, (key, desc) in enumerate(language_options, 1):
                    self.console.print(f"  {i}. {desc}")
                
                # Add special options
                self.console.print(f"  {len(language_options) + 1}. [bold green]Select All Languages[/bold green]")
                self.console.print(f"  {len(language_options) + 2}. [bold blue]Select Common Languages (en, fr, de, es)[/bold blue]")
                
                while True:
                    try:
                        choice = Prompt.ask("Select languages (comma-separated, e.g., 1,3,5) or press Enter for default (all)", console=self.console)
                        if choice.strip() == "":
                            # Use default
                            selected_languages = ["all"]
                            break
                        
                        choices = [int(x.strip()) for x in choice.split(',')]
                        
                        # Check for special options
                        if len(language_options) + 1 in choices:
                            # Select all languages (excluding "all" option)
                            selected_languages = [key for key, desc in language_options if key != "all"]
                            self.console.print(f"[green]Selected all languages: {', '.join(selected_languages)}[/green]")
                            break
                        elif len(language_options) + 2 in choices:
                            # Select common languages
                            selected_languages = ["en", "fr", "de", "es"]
                            self.console.print(f"[green]Selected common languages: {', '.join(selected_languages)}[/green]")
                            break
                        else:
                            # Regular selection
                            for c in choices:
                                if 1 <= c <= len(language_options):
                                    selected_languages.append(language_options[c-1][0])
                            
                            if selected_languages:
                                self.console.print(f"[green]Selected languages: {', '.join(selected_languages)}[/green]")
                                break
                            else:
                                self.console.print("[red]No valid languages selected.[/red]")
                    except ValueError:
                        self.console.print("[red]Please enter numbers separated by commas.[/red]")
                
                if not selected_languages:
                    self.console.print("[yellow]No languages selected, using default: all[/yellow]")
                    selected_languages = ["all"]
                    
            except Exception as e:
                # Fallback to simple selection if enhanced selection fails
                self.console.print(f"\n[yellow]Language selection (fallback mode): {e}[/yellow]")
                selected_languages = ["all"]
            
            # Handle language configuration
            if "all" in selected_languages and len(selected_languages) == 1:
                # Single "all" selection - use random selection
                self.config['language'] = None  # Will use random selection
                self.console.print("[green]✓ Will use random language selection based on company locations[/green]")
            elif len(selected_languages) == 1:
                # Single specific language
                selected_language = selected_languages[0]
                self.config['language'] = selected_language
                lang_name = language_mapper.get_language_name(selected_language)
                companies = language_mapper.get_companies_by_language(selected_language)
                self.console.print(f"[green]✓ Selected {lang_name} - {len(companies)} companies available[/green]")
                
                # Show some example companies
                if companies:
                    example_companies = companies[:5]
                    self.console.print(f"[cyan]Example companies: {', '.join(example_companies)}[/cyan]")
            else:
                # Multiple languages selected
                self.config['language'] = selected_languages
                total_companies = 0
                for lang_code in selected_languages:
                    companies = language_mapper.get_companies_by_language(lang_code)
                    total_companies += len(companies)
                
                self.console.print(f"[green]✓ Selected {len(selected_languages)} languages - {total_companies} total companies available[/green]")
                
                # Show language breakdown
                for lang_code in selected_languages:
                    lang_name = language_mapper.get_language_name(lang_code)
                    companies = language_mapper.get_companies_by_language(lang_code)
                    self.console.print(f"[cyan]  • {lang_name} ({lang_code}): {len(companies)} companies[/cyan]")
            
        except ImportError:
            self.console.print("[yellow]Language mapping not available, using default English[/yellow]")
            self.config['language'] = 'en'
        except Exception as e:
            self.console.print(f"[yellow]Language selection failed: {e}, using default English[/yellow]")
            self.config['language'] = 'en'
    
    def _collect_topic_parameters(self):
        """Collect topic configuration parameters."""
        self.console.print("\n[bold]📝 Topic Configuration[/bold]")
        
        # Topic options
        topic_options = [
            ("AWS Security Implementation", "Cloud security best practices and implementation"),
            ("Database Migration Guide", "Database migration strategies and procedures"),
            ("API Integration Tutorial", "REST API integration and authentication"),
            ("Network Security Assessment", "Network security evaluation and hardening"),
            ("DevOps Pipeline Setup", "CI/CD pipeline configuration and deployment"),
            ("Microservices Architecture", "Microservices design patterns and implementation"),
            ("Data Privacy Compliance", "GDPR, CCPA compliance and data protection"),
            ("Cybersecurity Incident Response", "Security incident handling and recovery"),
            ("Cloud Infrastructure Design", "Cloud architecture and infrastructure planning"),
            ("Application Security Testing", "Security testing methodologies and tools"),
            ("Custom Topic", "Enter your own custom topic")
        ]
        
        try:
            selected_topics = []
            self.console.print("\n[bold cyan]📝 Select Document Topics[/bold cyan]")
            self.console.print("[dim]Enter numbers separated by commas (e.g., 1,3,5) or press Enter for default[/dim]\n")
            
            for i, (key, desc) in enumerate(topic_options, 1):
                self.console.print(f"  {i}. {desc}")
            
            # Add special options
            self.console.print(f"  {len(topic_options) + 1}. [bold green]Select All Topics[/bold green]")
            self.console.print(f"  {len(topic_options) + 2}. [bold blue]Add Custom Topics[/bold blue]")
            
            while True:
                try:
                    choice = Prompt.ask("Select topics (comma-separated, e.g., 1,3,5) or press Enter for default (AWS Security)", console=self.console)
                    if choice.strip() == "":
                        # Use default
                        selected_topics = ["AWS Security Implementation"]
                        break
                    
                    choices = [int(x.strip()) for x in choice.split(',')]
                    
                    # Check for special options
                    if len(topic_options) + 1 in choices:
                        # Select all predefined topics (excluding Custom Topic)
                        selected_topics = [key for key, desc in topic_options if key != "Custom Topic"]
                        self.console.print(f"[green]Selected all topics: {', '.join(selected_topics)}[/green]")
                        break
                    elif len(topic_options) + 2 in choices:
                        # Add custom topics
                        self._add_custom_topics(selected_topics)
                        if selected_topics:
                            self.console.print(f"[green]Selected topics: {', '.join(selected_topics)}[/green]")
                            break
                        else:
                            self.console.print("[red]No topics selected.[/red]")
                    else:
                        # Regular selection
                        for c in choices:
                            if 1 <= c <= len(topic_options):
                                topic_key = topic_options[c-1][0]
                                if topic_key == "Custom Topic":
                                    # Allow user to enter custom topic
                                    custom_topic = Prompt.ask("Enter your custom topic", console=self.console)
                                    if custom_topic.strip():
                                        selected_topics.append(custom_topic.strip())
                                else:
                                    selected_topics.append(topic_key)
                        
                        if selected_topics:
                            self.console.print(f"[green]Selected topics: {', '.join(selected_topics)}[/green]")
                            break
                        else:
                            self.console.print("[red]No valid topics selected.[/red]")
                except ValueError:
                    self.console.print("[red]Please enter numbers separated by commas.[/red]")
            
            if not selected_topics:
                self.console.print("[yellow]No topics selected, using default: AWS Security Implementation[/yellow]")
                selected_topics = ["AWS Security Implementation"]
                
        except Exception as e:
            # Fallback to simple selection
            self.console.print(f"\n[yellow]Topic selection (fallback mode): {e}[/yellow]")
            selected_topics = ["AWS Security Implementation"]
        
        self.config['topics'] = selected_topics
    
    def _add_custom_topics(self, selected_topics: List[str]):
        """Add custom topics to the selection."""
        self.console.print("\n[bold cyan]📝 Add Custom Topics[/bold cyan]")
        self.console.print("[dim]Enter custom topics one by one, or 'done' to finish[/dim]\n")
        
        while True:
            try:
                custom_topic = Prompt.ask("Enter custom topic (or 'done' to finish)", console=self.console)
                if custom_topic.lower().strip() == 'done':
                    break
                elif custom_topic.strip():
                    selected_topics.append(custom_topic.strip())
                    self.console.print(f"[green]Added: {custom_topic.strip()}[/green]")
                else:
                    self.console.print("[red]Please enter a valid topic.[/red]")
            except KeyboardInterrupt:
                break
        
        if selected_topics:
            self.console.print(f"\n[green]Custom topics added: {', '.join(selected_topics)}[/green]")
        else:
            self.console.print("\n[yellow]No custom topics added.[/yellow]")
    
    def _collect_advanced_parameters(self):
        """Collect advanced parameters."""
        self.console.print("\n[bold]🤖 Agentic AI Configuration[/bold]")
        
        # Show agentic AI explanation
        self.console.print("\n[cyan]The Agentic AI will automatically:[/cyan]")
        self.console.print("• Analyze your topics and generate appropriate content")
        self.console.print("• Select optimal credential types based on your use case")
        self.console.print("• Determine the best embedding strategy for each file format")
        self.console.print("• Coordinate all agents to create realistic documents")
        
        # Regex database
        while True:
            regex_db = Prompt.ask(
                "Path to regex database file",
                default="./data/regex_db.json",
                console=self.console
            )
            if Path(regex_db).exists():
                self.config['regex_db_path'] = regex_db
                break
            else:
                self.console.print(f"[red]File not found: {regex_db}[/red]")
                if Confirm.ask("Create sample database?", console=self.console):
                    self._create_sample_database(regex_db)
                    self.config['regex_db_path'] = regex_db
                    break
        
        # Let AI suggest credential types based on use case
        self._ai_suggest_credential_types()
        
        # Topics are now selected by user in _collect_topic_parameters()
        # No need for AI topic suggestions
        
        # Let AI determine embedding strategy
        self.console.print("\n[cyan]🧠 AI will determine optimal embedding strategy based on your selections[/cyan]")
        self.config['embed_strategy'] = 'ai_determined'
        
        # Batch size
        while True:
            try:
                batch_size = int(Prompt.ask(
                    "Batch size for parallel processing",
                    default="5",
                    console=self.console
                ))
                Validators.validate_batch_size(batch_size)
                self.config['batch_size'] = batch_size
                break
            except (ValueError, CFValidationError) as e:
                self.console.print(f"[red]Error: {e}[/red]")
        
        # LLM model (mandatory for credential generation)
        self.console.print("\n[bold cyan]🤖 LLM Configuration (Required)[/bold cyan]")
        self.console.print("[dim]LLM is required for realistic credential generation based on regex patterns.[/dim]")
        self._select_llm_model()
    
    def _ai_suggest_credential_types(self):
        """Let AI suggest credential types based on use case."""
        self.console.print("\n[bold]🎯 Use Case Selection[/bold]")
        
        use_cases = [
            ("security_audit", "Security Audit & Penetration Testing"),
            ("api_testing", "API Testing & Documentation"),
            ("database_testing", "Database Security Testing"),
            ("cloud_testing", "Cloud Infrastructure Testing"),
            ("general_testing", "General Security Testing"),
            ("custom", "Custom Selection")
        ]
        
        try:
            # Use simple selection (more reliable)
            self.console.print("\n[bold cyan]Select Your Use Case[/bold cyan]")
            self.console.print("[dim]The AI will suggest appropriate credential types based on your use case:[/dim]\n")
            
            for i, (key, desc) in enumerate(use_cases, 1):
                self.console.print(f"  {i}. {desc}")
            
            while True:
                try:
                    choice = Prompt.ask("Select use case (1-6) or press Enter for default (security_audit)", console=self.console)
                    if choice.strip() == "":
                        selected_use_case = "security_audit"
                        break
                    
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(use_cases):
                        selected_use_case = use_cases[choice_num-1][0]
                        break
                    else:
                        self.console.print("[red]Invalid choice. Please select 1-6.[/red]")
                except ValueError:
                    self.console.print("[red]Please enter a number.[/red]")
        except Exception as e:
            self.console.print(f"[yellow]Use case selection failed: {e}, using default security_audit[/yellow]")
            selected_use_case = "security_audit"
        
        if selected_use_case == "custom":
            self._select_credential_types()
            # Configure credential count per file after credential types are set
            self._collect_credential_count_parameters()
        else:
            # AI suggestions based on use case
            suggestions = self._get_ai_credential_suggestions(selected_use_case)
            self.console.print(f"\n[green]🤖 AI suggests these credential types for {selected_use_case}:[/green]")
            for cred_type, description in suggestions.items():
                self.console.print(f"  • {cred_type}: {description}")
            
            if Confirm.ask("Use AI suggestions?", console=self.console):
                self.config['credential_types'] = list(suggestions.keys())
            else:
                self._select_credential_types()
        
        # Configure credential count per file after credential types are set
        self._collect_credential_count_parameters()
    
    def _get_ai_credential_suggestions(self, use_case: str) -> dict:
        """Get AI suggestions for credential types based on use case."""
        suggestions = {
            "security_audit": {
                "aws_access_key": "AWS credentials for cloud security testing",
                "jwt_token": "JWT tokens for authentication testing",
                "api_key": "API keys for endpoint security testing",
                "password": "Passwords for authentication testing"
            },
            "api_testing": {
                "api_key": "API keys for endpoint testing",
                "jwt_token": "JWT tokens for authentication",
                "aws_access_key": "AWS credentials for API services"
            },
            "database_testing": {
                "db_connection": "Database connection strings",
                "mongodb_uri": "MongoDB connection URIs",
                "password": "Database passwords"
            },
            "cloud_testing": {
                "aws_access_key": "AWS access keys",
                "aws_secret_key": "AWS secret keys",
                "api_key": "Cloud API keys"
            },
            "general_testing": {
                "aws_access_key": "AWS credentials",
                "jwt_token": "JWT tokens",
                "api_key": "API keys",
                "db_connection": "Database connections"
            }
        }
        return suggestions.get(use_case, suggestions["general_testing"])
    
    # Removed _ai_suggest_topics method - topics are now selected by user in _collect_topic_parameters()
    
    def _collect_credential_count_parameters(self):
        """Collect credential count configuration parameters."""
        self.console.print("\n[bold]🔢 Credential Count Configuration[/bold]")
        self.console.print("[dim]Configure how many credentials to include in each file[/dim]")
        
        # Get available credential types count
        available_credential_types = len(self.config.get('credential_types', []))
        if available_credential_types == 0:
            self.console.print("[yellow]Warning: No credential types selected yet[/yellow]")
            available_credential_types = 5  # Default assumption
        
        # Minimum credentials per file
        while True:
            try:
                min_creds = int(Prompt.ask(
                    f"Minimum credentials per file (1-{available_credential_types})",
                    default="1",
                    console=self.console
                ))
                if 1 <= min_creds <= available_credential_types:
                    break
                else:
                    self.console.print(f"[red]Please enter a number between 1 and {available_credential_types}[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/red]")
        
        # Maximum credentials per file
        while True:
            try:
                max_creds = int(Prompt.ask(
                    f"Maximum credentials per file ({min_creds}-{available_credential_types})",
                    default=str(min(available_credential_types, min_creds + 2)),
                    console=self.console
                ))
                if min_creds <= max_creds <= available_credential_types:
                    break
                else:
                    self.console.print(f"[red]Please enter a number between {min_creds} and {available_credential_types}[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/red]")
        
        # Store configuration
        self.config['min_credentials_per_file'] = min_creds
        self.config['max_credentials_per_file'] = max_creds
        
        self.console.print(f"[green]✅ Credential count configured: {min_creds}-{max_creds} credentials per file[/green]")
    
    def _select_credential_types(self):
        """Select credential types."""
        # Load available credential types from database
        try:
            from ..db.regex_db import RegexDatabase
            regex_db = RegexDatabase(self.config['regex_db_path'])
            available_types = regex_db.list_credential_types()
            
            if not available_types:
                self.console.print("[red]No credential types found in database![/red]")
                return
            
            # Create options for dialog
            type_options = [(k, f"{k} - {v['description']}") for k, v in available_types.items()]
            
            try:
                # Use simple multi-selection (more reliable)
                selected_types = []
                self.console.print("\n[bold cyan]🔑 Select Credential Types to Generate[/bold cyan]")
                self.console.print("[dim]Enter numbers separated by commas (e.g., 1,3,5), 'all' for all types, or press Enter for default[/dim]\n")
                
                for i, (key, desc) in enumerate(type_options, 1):
                    self.console.print(f"  {i}. {desc}")
                
                while True:
                    try:
                        choice = Prompt.ask("Select credential types (comma-separated, e.g., 1,3,5) or 'all' for all types", console=self.console)
                        if choice.strip() == "":
                            # Use default (first 3)
                            selected_types = list(available_types.keys())[:3]
                            break
                        elif choice.strip().lower() == "all":
                            # Select all available types
                            selected_types = list(available_types.keys())
                            self.console.print(f"[green]Selected ALL credential types: {', '.join(selected_types)}[/green]")
                            break
                        
                        choices = [int(x.strip()) for x in choice.split(',')]
                        for c in choices:
                            if 1 <= c <= len(type_options):
                                selected_types.append(type_options[c-1][0])
                        
                        if selected_types:
                            self.console.print(f"[green]Selected: {', '.join(selected_types)}[/green]")
                            break
                        else:
                            self.console.print("[red]No valid types selected.[/red]")
                    except ValueError:
                        self.console.print("[red]Please enter numbers separated by commas, 'all' for all types, or press Enter for default.[/red]")
                
                if not selected_types:
                    self.console.print("[yellow]No credential types selected, using default: password[/yellow]")
                    selected_types = ["password"]
            except Exception as e:
                # Fallback to simple selection if dialog fails
                self.console.print("\n[yellow]Credential type selection (fallback mode):[/yellow]")
                for i, (key, desc) in enumerate(type_options, 1):
                    self.console.print(f"  {i}. {desc}")
                
                selected_types = []
                while True:
                    try:
                        choice = Prompt.ask("Select credential types (comma-separated, e.g., 1,3,5), 'all' for all types, or 'done' to finish", console=self.console)
                        if choice.lower() == 'done':
                            break
                        elif choice.strip().lower() == "all":
                            # Select all available types
                            selected_types = list(available_types.keys())
                            self.console.print(f"[green]Selected ALL credential types: {', '.join(selected_types)}[/green]")
                            break
                        
                        choices = [int(x.strip()) for x in choice.split(',')]
                        for c in choices:
                            if 1 <= c <= len(type_options):
                                selected_types.append(type_options[c-1][0])
                        
                        if selected_types:
                            self.console.print(f"[green]Selected: {', '.join(selected_types)}[/green]")
                            break
                        else:
                            self.console.print("[red]No valid types selected.[/red]")
                    except ValueError:
                        self.console.print("[red]Please enter numbers separated by commas, 'all' for all types, or 'done' to finish.[/red]")
            
            if not selected_types:
                self.console.print("[red]At least one credential type must be selected![/red]")
                return self._select_credential_types()
            
            self.config['credential_types'] = selected_types
            
        except Exception as e:
            self.console.print(f"[red]Error loading credential types: {e}[/red]")
            # Fallback to manual input
            cred_types = Prompt.ask(
                "Credential types (comma-separated)",
                default="aws_access_key, jwt_token, db_connection",
                console=self.console
            )
            self.config['credential_types'] = [t.strip() for t in cred_types.split(',')]
    
    def _select_llm_model(self):
        """Select LLM model."""
        # Look for common model locations
        model_paths = []
        
        # Check common directories
        common_dirs = [
            "./models",
            "~/models",
            "~/Downloads",
            "./",
        ]
        
        for dir_path in common_dirs:
            expanded_path = Path(dir_path).expanduser()
            if expanded_path.exists():
                for file_path in expanded_path.glob("*.gguf"):
                    model_paths.append(str(file_path))
        
        # Use local model selection with download capability
        from ..llm.llama_interface import LlamaInterface
        
        # Check for available local models
        available_models = LlamaInterface.list_available_models()
        
        models = [
            ("tinyllama", "TinyLlama 1.1B (Fast, ~1GB)"),
            ("phi3-mini", "Phi-3 Mini 4K (Balanced, ~2GB)"),
            ("qwen2-0.5b", "Qwen2 0.5B (Very Fast, ~500MB)"),
            ("gemma-2b", "Gemma 2B (Good Quality, ~1.5GB)"),
        ]
        
        # Mark available models
        model_options = []
        for model_id, description in models:
            if model_id in available_models:
                model_options.append((model_id, f"✅ {description} (Local)"))
            else:
                model_options.append((model_id, f"⬇️  {description} (Download)"))
        
        try:
            # Use simple selection (more reliable)
            self.console.print("\n[bold cyan]Select LLM Model (Required)[/bold cyan]")
            self.console.print("[dim]Choose a lightweight model for realistic credential generation:[/dim]\n")
            
            for i, (key, desc) in enumerate(model_options, 1):
                self.console.print(f"  {i}. {desc}")
            
            while True:
                try:
                    choice = Prompt.ask("Select model (1-4) or press Enter for default (tinyllama) - Required for credential generation", console=self.console)
                    if choice.strip() == "":
                        selected_model = "tinyllama"
                        break
                    
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(model_options):
                        selected_model = model_options[choice_num-1][0]
                        break
                    else:
                        self.console.print("[red]Invalid choice. Please select 1-4.[/red]")
                except ValueError:
                    self.console.print("[red]Please enter a number.[/red]")
        except Exception as e:
            self.console.print(f"[yellow]Model selection failed: {e}, using default tinyllama[/yellow]")
            selected_model = "tinyllama"
        
        # Download model if not available locally
        if selected_model not in available_models:
            self.console.print(f"\n[cyan]Downloading {selected_model} to local models directory...[/cyan]")
            try:
                model_path = LlamaInterface.download_model(selected_model)
                self.console.print(f"[green]✅ Model downloaded to: {model_path}[/green]")
            except Exception as e:
                self.console.print(f"[red]❌ Failed to download model: {e}[/red]")
                return
        
        self.config['llm_model'] = selected_model
    
    def _create_sample_database(self, db_path: str):
        """Create sample regex database."""
        sample_db = {
            "credentials": [
                {
                    "type": "aws_access_key",
                    "regex": "^AKIA[0-9A-Z]{16}$",
                    "description": "AWS Access Key ID",
                    "generator": "random_string(20, 'A-Z0-9')"
                },
                {
                    "type": "jwt_token",
                    "regex": "^eyJ[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+$",
                    "description": "JWT Token",
                    "generator": "base64_encode(header.payload.signature)"
                },
                {
                    "type": "db_connection",
                    "regex": "^(mysql|postgres)://[a-zA-Z0-9]+:[a-zA-Z0-9]+@[a-zA-Z0-9.]+:[0-9]+/[a-zA-Z0-9]+$",
                    "description": "Database Connection String",
                    "generator": "construct_db_string()"
                }
            ]
        }
        
        import json
        with open(db_path, 'w') as f:
            json.dump(sample_db, f, indent=2)
        
        self.console.print(f"[green]Created sample database: {db_path}[/green]")
    
    def _preview_configuration(self):
        """Preview the configuration."""
        self.console.print("\n[bold]Configuration Preview[/bold]")
        
        table = Table(title="Generation Configuration")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Output Directory", self.config['output_dir'])
        table.add_row("Number of Files", str(self.config['num_files']))
        table.add_row("File Formats", ", ".join(self.config['formats']))
        table.add_row("Credential Types", ", ".join(self.config['credential_types']))
        table.add_row("Credentials per File", f"{self.config.get('min_credentials_per_file', 1)}-{self.config.get('max_credentials_per_file', 3)}")
        table.add_row("Topics", ", ".join(self.config['topics']))
        table.add_row("Embedding Strategy", self.config['embed_strategy'])
        table.add_row("Batch Size", str(self.config['batch_size']))
        
        if 'llm_model' in self.config:
            table.add_row("LLM Model", Path(self.config['llm_model']).name)
        
        self.console.print(table)
    
    def _confirm_generation(self) -> bool:
        """Confirm generation."""
        return Confirm.ask("\nProceed with generation?", console=self.console)
    
    def _execute_generation(self):
        """Execute the generation process with agentic AI."""
        self.console.print("\n[bold]🤖 Agentic AI Generation Process[/bold]")
        
        try:
            from ..agents.orchestrator import OrchestratorAgent
            from ..llm.llama_interface import LlamaInterface
            
            # Show AI coordination steps
            self.console.print("\n[cyan]🧠 AI Agent Coordination:[/cyan]")
            self.console.print("1. 📋 Orchestrator Agent: Coordinating all agents")
            self.console.print("2. 🎯 Topic Agent: Analyzing topics and generating content")
            self.console.print("3. 🔑 Credential Agent: Creating realistic credentials")
            self.console.print("4. 📍 Embedding Agent: Determining optimal placement")
            self.console.print("5. 📄 Synthesizer Agents: Creating final documents")
            
            # Initialize LLM if specified
            llm_interface = None
            if 'llm_model' in self.config:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("🤖 Loading AI model...", total=None)
                    # Ensure model path includes .gguf extension
                    model_name = self.config['llm_model']
                    if not model_name.endswith('.gguf'):
                        model_name = f"{model_name}.gguf"
                    llm_interface = LlamaInterface(model_name)
                    progress.update(task, description="✅ AI model loaded")
            
            # Create orchestrator with config
            orchestrator = OrchestratorAgent(config=self.config, llm_interface=llm_interface)
            
            # Execute generation with detailed progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("🤖 AI agents working...", total=None)
                
                # Show what AI is doing
                progress.update(task, description="🎯 Topic Agent: Generating content...")
                
                results = orchestrator.orchestrate_generation(self.config)
                
                progress.update(task, description="✅ AI generation complete")
            
            # Show detailed results
            self._show_ai_results(results)
            
        except Exception as e:
            self.console.print(f"[red]❌ AI generation failed: {e}[/red]")
            self.logger.error(f"Generation error: {e}")
    
    def _show_ai_results(self, results: Dict[str, Any]):
        """Show AI generation results with detailed breakdown."""
        self.console.print("\n[bold green]🎉 Agentic AI Generation Complete![/bold green]")
        
        # Main results table
        table = Table(title="🤖 AI Generation Results", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("AI Agent", style="yellow")
        
        table.add_row("Files Generated", str(len(results['files'])), "📄 Synthesizer Agents")
        table.add_row("Total Credentials", str(results['metadata']['total_credentials']), "🔑 Credential Agent")
        table.add_row("Generation Time", f"{results['metadata']['generation_time']:.2f}s", "📋 Orchestrator Agent")
        
        if results['errors']:
            table.add_row("Errors", str(len(results['errors'])), "⚠️  System")
        
        self.console.print(table)
        
        # Show files by format
        if results['metadata']['files_by_format']:
            self.console.print("\n[bold]📊 Files by Format:[/bold]")
            format_table = Table(show_header=True, header_style="bold blue")
            format_table.add_column("Format", style="cyan")
            format_table.add_column("Count", style="green")
            format_table.add_column("AI Strategy", style="yellow")
            
            for format_name, count in results['metadata']['files_by_format'].items():
                strategy = self._get_ai_strategy_for_format(format_name)
                format_table.add_row(format_name.upper(), str(count), strategy)
            
            self.console.print(format_table)
        
        # Show credentials by type
        if results['metadata']['credentials_by_type']:
            self.console.print("\n[bold]🔑 Credentials by Type:[/bold]")
            cred_table = Table(show_header=True, header_style="bold blue")
            cred_table.add_column("Credential Type", style="cyan")
            cred_table.add_column("Count", style="green")
            cred_table.add_column("AI Generated", style="yellow")
            
            for cred_type, count in results['metadata']['credentials_by_type'].items():
                cred_table.add_row(cred_type.replace('_', ' ').title(), str(count), "✅")
            
            self.console.print(cred_table)
        
        # Show generated files
        if results['files']:
            self.console.print("\n[bold]📁 Generated Files:[/bold]")
            for i, file_path in enumerate(results['files'], 1):
                filename = Path(file_path).name
                file_size = Path(file_path).stat().st_size
                self.console.print(f"  {i}. [green]{filename}[/green] ({file_size} bytes)")
        
        if results['errors']:
            self.console.print("\n[yellow]⚠️  Errors encountered:[/yellow]")
            for error in results['errors']:
                self.console.print(f"  - {error}")
        
        self.console.print(f"\n[green]📂 Files saved to: {self.config['output_dir']}[/green]")
        self.console.print("\n[bold cyan]🤖 The Agentic AI successfully coordinated all agents to create realistic synthetic documents![/bold cyan]")
    
    def _get_ai_strategy_for_format(self, format_name: str) -> str:
        """Get AI strategy description for file format."""
        strategies = {
            'eml': 'Email body + attachments',
            'xlsx': 'Cells + formulas + metadata',
            'pptx': 'Slides + notes + shapes',
            'vsdx': 'Shapes + data fields + labels'
        }
        return strategies.get(format_name, 'AI determined')
    
    def _show_results(self, results: Dict[str, Any]):
        """Show generation results (legacy method)."""
        self._show_ai_results(results)
