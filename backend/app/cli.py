import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint

from app.config.settings import get_settings
from app.core.analyzer import CodeQualityAnalyzer
from app.services.analysis_service import AnalysisService
from app.services.qa_service import QAService
from app.database.mongodb import init_db, close_db
from app.database.vector_db import init_vector_db, close_vector_db

console = Console()
settings = get_settings()

class CLIContext:
    """Context for CLI operations"""
    def __init__(self):
        self.analyzer = None
        self.analysis_service = None
        self.qa_service = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize services"""
        if not self.initialized:
            await init_db()
            await init_vector_db()
            self.analyzer = CodeQualityAnalyzer()
            self.analysis_service = AnalysisService()
            self.qa_service = QAService()
            self.initialized = True
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.initialized:
            await close_db()
            await close_vector_db()

# Global CLI context
cli_context = CLIContext()

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', '-c', help='Configuration file path')
def cli(verbose: bool, config: Optional[str]):
    """Code Quality Intelligence Agent CLI"""
    if verbose:
        console.print("[bold blue]Code Quality Intelligence Agent CLI[/bold blue]")
        console.print(f"Version: 1.0.0")
        console.print(f"Python: {sys.version}")
        console.print()

@cli.command()
@click.argument('source', required=True)
@click.option('--languages', '-l', help='Comma-separated list of languages to analyze')
@click.option('--exclude', '-e', help='Comma-separated exclude patterns')
@click.option('--include-tests/--no-tests', default=True, help='Include test files')
@click.option('--output-format', '-f', type=click.Choice(['json', 'table', 'summary']), default='summary')
@click.option('--output-file', '-o', help='Output file path')
@click.option('--wait/--no-wait', default=True, help='Wait for analysis completion')
@click.option('--severity-filter', type=click.Choice(['critical', 'high', 'medium', 'low', 'info']), help='Filter issues by minimum severity')
def analyze(source: str, languages: Optional[str], exclude: Optional[str], 
           include_tests: bool, output_format: str, output_file: Optional[str],
           wait: bool, severity_filter: Optional[str]):
    """Analyze code repository or directory"""
    asyncio.run(_analyze_impl(
        source, languages, exclude, include_tests, 
        output_format, output_file, wait, severity_filter
    ))

@cli.command()
@click.option('--pr-url', required=True, help='GitHub pull request URL')
@click.option('--github-token', required=True, help='GitHub personal access token')
def pr_review(pr_url: str, github_token: str):
    """Review a GitHub pull request"""
    asyncio.run(_pr_review_impl(pr_url, github_token))

async def _pr_review_impl(pr_url: str, github_token: str):
    try:
        await cli_context.initialize()
        from app.api.v1.pr_review import review_pull_request
        # Call the review_pull_request function directly
        # Construct request object
        from app.api.v1.pr_review import PRReviewRequest
        request = PRReviewRequest(pr_url=pr_url, github_token=github_token)
        response = await review_pull_request(request)
        console.print(f"[green]PR Review Completed:[/green] {response.message}")
    except Exception as e:
        import traceback
        console.print(f"[red]Error during PR review: {str(e)}[/red]")
        console.print(f"[red]Traceback:[/red]\n{traceback.format_exc()}")
    finally:
        await cli_context.cleanup()

async def _analyze_impl(source: str, languages: Optional[str], exclude: Optional[str],
                       include_tests: bool, output_format: str, output_file: Optional[str],
                       wait: bool, severity_filter: Optional[str]):
    """Implementation of analyze command"""
    try:
        await cli_context.initialize()
        
        # Validate source
        if source.startswith('http'):
            if not source.startswith('https://github.com/'):
                console.print("[red]Error: Only GitHub URLs are supported[/red]")
                sys.exit(1)
            source_type = 'github'
        else:
            if not os.path.exists(source):
                console.print(f"[red]Error: Path '{source}' does not exist[/red]")
                sys.exit(1)
            source_type = 'local'
        
        # Parse languages
        language_list = None
        if languages:
            language_list = [lang.strip() for lang in languages.split(',')]
        
        # Parse exclude patterns
        exclude_list = []
        if exclude:
            exclude_list = [pattern.strip() for pattern in exclude.split(',')]
        
        console.print(f"[bold green]Starting analysis of:[/bold green] {source}")
        console.print(f"Source type: {source_type}")
        if language_list:
            console.print(f"Languages: {', '.join(language_list)}")
        if exclude_list:
            console.print(f"Excluding: {', '.join(exclude_list)}")
        console.print()
        
        # Start analysis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing analysis...", total=None)
            
            report_id = await cli_context.analysis_service.start_analysis(
                source_type=source_type,
                source_path=source,
                languages=language_list,
                include_tests=include_tests,
                exclude_patterns=exclude_list
            )
            
            progress.update(task, description=f"Analysis started (ID: {report_id[:8]})")
            
            if wait:
                # Poll for completion
                while True:
                    result = await cli_context.analysis_service.get_analysis_status(report_id)
                    
                    if result.status.value == 'completed':
                        progress.update(task, description="Analysis completed!")
                        break
                    elif result.status.value == 'failed':
                        progress.update(task, description="Analysis failed!")
                        console.print(f"[red]Error: {result.error_message}[/red]")
                        sys.exit(1)
                    elif result.status.value == 'cancelled':
                        progress.update(task, description="Analysis cancelled!")
                        sys.exit(1)
                    else:
                        progress.update(task, description=f"Analyzing... ({result.status.value})")
                    
                    await asyncio.sleep(2)
        
        # Get final result
        result = await cli_context.analysis_service.get_analysis_status(report_id)
        
        # Filter issues by severity if specified
        issues = result.issues
        if severity_filter:
            severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'info': 0}
            min_severity = severity_order[severity_filter]
            issues = [issue for issue in issues if severity_order.get(issue.severity.value, 0) >= min_severity]
        
        # Output results
        if output_format == 'json':
            output_data = {
                'report_id': report_id,
                'status': result.status.value,
                'metrics': result.metrics.model_dump() if result.metrics else None,
                'issues': [issue.model_dump() for issue in issues],
                'file_metrics': [fm.model_dump() for fm in result.file_metrics],
                'summary': {
                    'total_issues': len(issues),
                    'critical_issues': len([i for i in issues if i.severity.value == 'critical']),
                    'high_issues': len([i for i in issues if i.severity.value == 'high']),
                    'files_analyzed': len(result.file_metrics),
                }
            }
            
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(output_data, f, indent=2)
                console.print(f"[green]Results saved to {output_file}[/green]")
            else:
                print(json.dumps(output_data, indent=2))
        
        elif output_format == 'table':
            _display_issues_table(issues)
        
        else:  # summary format
            _display_summary(result, issues)
        
        if not wait:
            console.print(f"[green]Analysis started with ID: {report_id}[/green]")
            console.print("Use 'python -m app.cli status <report_id>' to check progress")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
    finally:
        await cli_context.cleanup()

def _display_summary(result, issues):
    """Display analysis summary"""
    console.print("\n[bold blue]Analysis Summary[/bold blue]")
    console.print("=" * 50)
    
    if result.metrics:
        # Repository metrics
        metrics_table = Table(title="Repository Metrics")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="magenta")
        
        metrics_table.add_row("Total Files", str(result.metrics.total_files))
        metrics_table.add_row("Total Lines", f"{result.metrics.total_lines:,}")
        metrics_table.add_row("Average Complexity", f"{result.metrics.complexity_average:.2f}")
        metrics_table.add_row("Maintainability Index", f"{result.metrics.maintainability_average:.2f}")
        metrics_table.add_row("Technical Debt", f"{result.metrics.technical_debt_hours:.1f} hours")
        
        console.print(metrics_table)
        console.print()
        
        # Languages
        if result.metrics.languages:
            console.print("[bold]Languages:[/bold]")
            for lang, count in result.metrics.languages.items():
                console.print(f"  • {lang}: {count} files")
            console.print()
    
    # Issues summary
    if issues:
        severity_counts = {}
        category_counts = {}
        
        for issue in issues:
            severity_counts[issue.severity.value] = severity_counts.get(issue.severity.value, 0) + 1
            category_counts[issue.category.value] = category_counts.get(issue.category.value, 0) + 1
        
        issues_table = Table(title="Issues Summary")
        issues_table.add_column("Severity", style="red")
        issues_table.add_column("Count", style="bold")
        
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                issues_table.add_row(severity.title(), str(count))
        
        console.print(issues_table)
        console.print()
        
        # Top issues
        console.print("[bold]Top 5 Issues:[/bold]")
        for i, issue in enumerate(issues[:5], 1):
            severity_color = {
                'critical': 'red',
                'high': 'yellow',
                'medium': 'blue',
                'low': 'green',
                'info': 'cyan'
            }.get(issue.severity.value, 'white')
            
            console.print(f"{i}. [{severity_color}][{issue.severity.value.upper()}][/{severity_color}] {issue.title}")
            console.print(f"   📁 {issue.file_path}" + (f" (line {issue.line_number})" if issue.line_number else ""))
            console.print(f"   💡 {issue.suggestion}")
            console.print()
    else:
        console.print("[green]🎉 No issues found! Your code quality is excellent.[/green]")

def _display_issues_table(issues):
    """Display issues in table format"""
    if not issues:
        console.print("[green]No issues found![/green]")
        return
    
    table = Table(title="Code Quality Issues")
    table.add_column("Severity", style="red", width=10)
    table.add_column("Category", style="blue", width=12)
    table.add_column("File", style="cyan", width=30)
    table.add_column("Line", style="magenta", width=6)
    table.add_column("Issue", style="yellow", width=40)
    
    for issue in issues:
        table.add_row(
            issue.severity.value,
            issue.category.value,
            issue.file_path,
            str(issue.line_number) if issue.line_number else "-",
            issue.title
        )
    
    console.print(table)

@cli.command()
@click.option('--report-id', '-r', help='Report ID for context-aware questions')
@click.option('--question', '-q', help='Single question to ask')
def qa(report_id: Optional[str], question: Optional[str]):
    """Interactive Q&A about code analysis"""
    asyncio.run(_qa_impl(report_id, question))

async def _qa_impl(report_id: Optional[str], question: Optional[str]):
    """Implementation of Q&A command"""
    try:
        await cli_context.initialize()
        
        if question:
            # Single question mode
            console.print(f"[bold blue]Question:[/bold blue] {question}")
            console.print()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("Thinking..."),
                console=console,
            ) as progress:
                task = progress.add_task("Processing question...", total=None)
                response = await cli_context.qa_service.ask_question(question, report_id)
            
            console.print(f"[bold green]Answer:[/bold green]")
            console.print(Panel(response['answer'], title="AI Response", border_style="green"))
            
            if response.get('sources'):
                console.print(f"[dim]Sources: {', '.join(response['sources'])}[/dim]")
            
            if response.get('confidence'):
                console.print(f"[dim]Confidence: {response['confidence']*100:.1f}%[/dim]")
        
        else:
            # Interactive mode
            console.print("[bold blue]Interactive Q&A Mode[/bold blue]")
            console.print("Ask questions about your code analysis. Type 'exit' to quit.\n")
            
            if report_id:
                console.print(f"[dim]Context: Report {report_id}[/dim]\n")
            
            while True:
                try:
                    user_question = console.input("[bold cyan]❓ Your question: [/bold cyan]")
                    
                    if user_question.lower() in ['exit', 'quit', 'q']:
                        break
                    
                    if not user_question.strip():
                        continue
                    
                    console.print()
                    
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("Thinking..."),
                        console=console,
                    ) as progress:
                        task = progress.add_task("Processing...", total=None)
                        response = await cli_context.qa_service.ask_question(user_question, report_id)
                    
                    console.print(f"[bold green]🤖 AI Assistant:[/bold green]")
                    console.print(Panel(response['answer'], border_style="green"))
                    
                    if response.get('sources'):
                        console.print(f"[dim]📚 Sources: {', '.join(response['sources'])}[/dim]")
                    
                    console.print()
                
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
            
            console.print("[yellow]Goodbye! 👋[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
    finally:
        await cli_context.cleanup()

@cli.command()
@click.argument('report_id')
def status(report_id: str):
    """Check analysis status"""
    asyncio.run(_status_impl(report_id))

async def _status_impl(report_id: str):
    """Implementation of status command"""
    try:
        await cli_context.initialize()
        
        result = await cli_context.analysis_service.get_analysis_status(report_id)
        
        if not result:
            console.print(f"[red]Report {report_id} not found[/red]")
            sys.exit(1)
        
        status_color = {
            'completed': 'green',
            'in_progress': 'yellow',
            'failed': 'red',
            'cancelled': 'orange',
            'pending': 'blue'
        }.get(result.status.value, 'white')
        
        console.print(f"[bold]Report ID:[/bold] {report_id}")
        console.print(f"[bold]Status:[/bold] [{status_color}]{result.status.value}[/{status_color}]")
        console.print(f"[bold]Created:[/bold] {result.created_at}")
        
        if result.completed_at:
            console.print(f"[bold]Completed:[/bold] {result.completed_at}")
        
        if result.error_message:
            console.print(f"[bold red]Error:[/bold red] {result.error_message}")
        
        if result.issues:
            console.print(f"[bold]Issues Found:[/bold] {len(result.issues)}")
        
        if result.metrics:
            console.print(f"[bold]Files Analyzed:[/bold] {result.metrics.total_files}")
            console.print(f"[bold]Lines of Code:[/bold] {result.metrics.total_lines:,}")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
    finally:
        await cli_context.cleanup()

@cli.command()
def health():
    """Check system health"""
    asyncio.run(_health_impl())

async def _health_impl():
    """Implementation of health command"""
    try:
        await cli_context.initialize()
        
        console.print("[bold blue]System Health Check[/bold blue]")
        console.print("=" * 30)
        
        # Check MongoDB
        try:
            from app.database.mongodb import get_database
            db = await get_database()
            # A simple query to check the connection
            await db.command('ping')
            console.print("✅ MongoDB: [green]Connected[/green]")
        except Exception as e:
            console.print(f"❌ MongoDB: [red]Error - {str(e)}[/red]")
        
        # Check Vector DB
        try:
            from app.database.vector_db import get_vector_engine
            engine = await get_vector_engine()
            if engine.initialized:
                console.print("✅ Vector DB: [green]Initialized[/green]")
            else:
                console.print("⚠️  Vector DB: [yellow]Not initialized[/yellow]")
        except Exception as e:
            console.print(f"❌ Vector DB: [red]Error - {str(e)}[/red]")
        
        # Check Gemini API
        if settings.GEMINI_API_KEY:
            console.print("✅ Gemini API: [green]Configured[/green]")
        else:
            console.print("⚠️  Gemini API: [yellow]Not configured[/yellow]")
        
        # Check GitHub Token
        if settings.GITHUB_TOKEN:
            console.print("✅ GitHub Token: [green]Configured[/green]")
        else:
            console.print("ℹ️  GittHub Token: [dim]Not configured (public repos only)[/dim]")
    finally:
        await cli_context.cleanup()

if __name__ == '__main__':
    cli()
