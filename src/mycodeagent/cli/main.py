"""CLI入口模块"""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..core import Orchestrator, WorkflowStage
from ..infrastructure import OpenAIClient, UnifiedLLMClient

app = typer.Typer(name="mycodeagent", help="轻量级多Agent代码开发平台", no_args_is_help=True)
console = Console()


def create_llm_client(provider: str = "openai") -> UnifiedLLMClient:
    client = UnifiedLLMClient(default_provider=provider)
    if provider == "openai":
        try:
            client.register_provider("openai", OpenAIClient())
        except Exception as e:
            console.print(f"[yellow]Warning: OpenAI客户端初始化失败: {e}[/yellow]")
    return client


@app.command()
def init(name: str = typer.Argument(..., help="项目名称")):
    """初始化新项目"""
    console.print(Panel(f"[bold green]初始化项目: {name}[/bold green]"))
    project_path = Path(name)
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "src").mkdir(exist_ok=True)
    (project_path / "tests").mkdir(exist_ok=True)
    console.print(f"[green]项目已创建: {project_path}[/green]")


@app.command()
def run(
    description: str = typer.Option(..., "--desc", "-d", help="项目描述"),
    project_name: str = typer.Option("myproject", "--name", "-n", help="项目名称"),
    provider: str = typer.Option("openai", "--provider", "-p", help="LLM Provider"),
    output: Path = typer.Option("./output", "--output", "-o", help="输出目录"),
):
    """运行完整工作流"""
    console.print(Panel("[bold cyan]MyCodeAgent 工作流[/bold cyan]"))

    orchestrator = Orchestrator()
    llm_client = create_llm_client(provider)
    orchestrator.set_llm_client(llm_client)

    async def execute():
        await orchestrator.initialize()
        return await orchestrator.run_workflow({
            "project_name": project_name,
            "description": description,
            "project_path": str(output),
            "language": "python",
        })

    result = asyncio.run(execute())

    table = Table(show_header=True)
    table.add_column("阶段")
    table.add_column("状态")
    for stage_name, stage_result in result.get("stages", {}).items():
        status = "[green]成功[/green]" if stage_result.success else "[red]失败[/red]"
        table.add_row(stage_name, status)
    console.print(table)

    if result.get("success"):
        console.print("\n[bold green]工作流执行完成![/bold green]")
    else:
        console.print(f"\n[bold red]工作流执行失败: {result.get('error')}[/bold red]")


@app.command()
def list_agents():
    """列出所有可用的Agent"""
    table = Table(title="可用Agent")
    table.add_column("名称", style="cyan")
    table.add_column("描述", style="green")
    agents = [("requirement", "需求分析Agent"), ("coder", "代码开发Agent"), ("reviewer", "代码审查Agent")]
    for name, desc in agents:
        table.add_row(name, desc)
    console.print(table)


@app.command()
def version():
    """显示版本信息"""
    from .. import __version__
    console.print(f"[bold]MyCodeAgent[/bold] v{__version__}")


if __name__ == "__main__":
    app()
