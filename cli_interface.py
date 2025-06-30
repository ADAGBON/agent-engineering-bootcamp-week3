import time
import sys
from typing import List, Dict, Any


class CLIInterface:
    """
    Command Line Interface for the RAG system.
    
    Provides colored output, loading animations, and formatted display.
    """
    
    # ANSI color codes
    COLORS = {
        'blue': '\033[94m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'underline': '\033[4m',
        'end': '\033[0m'
    }
    
    def __init__(self, app_name: str = "RAG Chat System"):
        """Initialize the CLI interface with app name."""
        self.app_name = app_name
        self.print_header()
    
    def color_text(self, text: str, color: str) -> str:
        """Apply color to text."""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['end']}"
    
    def print_header(self):
        """Print a welcome header."""
        header = f"""
{self.color_text('=' * 60, 'blue')}
{self.color_text(f'  {self.app_name}', 'bold')}
{self.color_text('  Agent Engineering Bootcamp - RAG Integration', 'cyan')}
{self.color_text('=' * 60, 'blue')}
        """
        print(header)
    
    def print_info(self, message: str):
        """Print informational message."""
        print(f"{self.color_text('ℹ️  INFO:', 'blue')} {message}")
    
    def print_success(self, message: str):
        """Print success message."""
        print(f"{self.color_text('✅ SUCCESS:', 'green')} {message}")
    
    def print_warning(self, message: str):
        """Print warning message."""
        print(f"{self.color_text('⚠️  WARNING:', 'yellow')} {message}")
    
    def print_error(self, message: str):
        """Print error message."""
        print(f"{self.color_text('❌ ERROR:', 'red')} {message}")
    
    def print_question(self, question: str):
        """Print user question."""
        print(f"\n{self.color_text('🤔 Question:', 'purple')} {self.color_text(question, 'bold')}")
    
    def print_documents(self, documents: List[Dict[str, Any]]):
        """Print retrieved documents in a formatted way."""
        if not documents:
            self.print_warning("No documents found.")
            return
        
        print(f"\n{self.color_text('📚 Retrieved Documents:', 'cyan')}")
        print(self.color_text('-' * 50, 'cyan'))
        
        for i, doc in enumerate(documents, 1):
            content = doc.get('content', 'No content available')
            metadata = doc.get('metadata', {})
            score = metadata.get('score', 'N/A')
            
            # Truncate content if too long
            display_content = content[:200] + "..." if len(content) > 200 else content
            
            print(f"\n{self.color_text(f'Document {i}:', 'bold')}")
            print(f"{self.color_text('Score:', 'yellow')} {score}")
            print(f"{self.color_text('Content:', 'white')} {display_content}")
    
    def print_answer(self, answer: str):
        """Print AI-generated answer."""
        print(f"\n{self.color_text('🤖 AI Answer:', 'green')}")
        print(self.color_text('-' * 50, 'green'))
        print(f"{answer}\n")
    
    def loading_animation(self, message: str, duration: float = 2.0):
        """Show a loading animation."""
        animation = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        start_time = time.time()
        i = 0
        
        while time.time() - start_time < duration:
            sys.stdout.write(f'\r{self.color_text(animation[i % len(animation)], "cyan")} {message}')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        
        sys.stdout.write('\r' + ' ' * (len(message) + 10) + '\r')
        sys.stdout.flush()
    
    def get_user_input(self, prompt: str = "Enter your question") -> str:
        """Get input from user with colored prompt."""
        try:
            return input(f"\n{self.color_text(f'💬 {prompt}:', 'bold')} ")
        except KeyboardInterrupt:
            print(f"\n{self.color_text('👋 Goodbye!', 'yellow')}")
            sys.exit(0)
    
    def print_separator(self):
        """Print a visual separator."""
        print(f"\n{self.color_text('=' * 60, 'blue')}") 