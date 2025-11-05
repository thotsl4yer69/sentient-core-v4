"""
Command-line interface for Sentient Core.
"""

import sys
import argparse
import logging
from pathlib import Path

from .core.agent import SentientAgent
from .core.config import Config


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Sentient Core v4 - Advanced AI Cognitive Architecture',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config/default.yaml',
        help='Path to configuration file'
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['interactive', 'server', 'single'],
        default='interactive',
        help='Operation mode'
    )

    parser.add_argument(
        '--input',
        type=str,
        help='Input text for single mode'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Sentient Core v4.0.0'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    logger = logging.getLogger(__name__)
    logger.info("Starting Sentient Core v4...")

    try:
        # Load configuration
        config = Config.from_yaml(args.config)
        logger.info(f"Loaded configuration from: {args.config}")

        # Create agent
        agent = SentientAgent(config=config)
        agent.initialize()

        logger.info("Sentient Core initialized successfully")

        # Run based on mode
        if args.mode == 'interactive':
            run_interactive(agent)
        elif args.mode == 'server':
            run_server(agent)
        elif args.mode == 'single':
            run_single(agent, args.input)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


def run_interactive(agent: SentientAgent):
    """Run in interactive mode."""
    print("\n" + "="*60)
    print("  Sentient Core v4 - Interactive Mode")
    print("="*60)
    print("\nType 'help' for commands, 'exit' to quit\n")

    while True:
        try:
            user_input = input(">>> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Shutting down...")
                agent.shutdown()
                break

            if user_input.lower() == 'help':
                print_help()
                continue

            if user_input.lower() == 'status':
                status = agent.get_status()
                print(f"\nStatus: {status}\n")
                continue

            if user_input.lower().startswith('team '):
                # Multi-agent task
                task = user_input[5:]
                result = agent.create_team_task(task)
                print(f"\nTeam Result: {result}\n")
                continue

            # Process input
            response = agent.process(user_input)
            print(f"\n{response}\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Shutting down...")
            agent.shutdown()
            break
        except Exception as e:
            print(f"Error: {e}")


def run_server(agent: SentientAgent):
    """Run in server mode."""
    from .api.server import start_server

    print("\n" + "="*60)
    print("  Sentient Core v4 - Server Mode")
    print("="*60)

    try:
        start_server(agent)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        agent.shutdown()


def run_single(agent: SentientAgent, input_text: str):
    """Run single command and exit."""
    if not input_text:
        print("Error: --input required for single mode")
        sys.exit(1)

    response = agent.process(input_text)
    print(response)

    agent.shutdown()


def print_help():
    """Print help information."""
    help_text = """
Available Commands:
  help              - Show this help message
  status            - Show agent status
  team <task>       - Execute task with agent team
  exit/quit/q       - Exit the program

Examples:
  >>> Analyze this data and provide insights
  >>> team Research the latest AI developments
  >>> status
"""
    print(help_text)


if __name__ == '__main__':
    main()
