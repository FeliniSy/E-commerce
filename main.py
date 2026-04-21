import asyncio
import argparse
from datetime import datetime

from orchestrator.pipeline_runner import run_pipeline, run_multiple_sources
from config import get_all_sources
from utils.logger import logger


async def main(sources: list[str], parallel: bool = False):
    """
    Main entry point for running scraping pipelines

    Args:
        sources: List of source names to scrape (e.g., ['alta', 'koncept'])
        parallel: If True, run sources in parallel; if False, run sequentially
    """
    try:
        if len(sources) == 1:
            await run_pipeline(sources[0])
        else:
            await run_multiple_sources(sources, sequential=not parallel)

    except Exception as e:
        logger.critical(f"Pipeline crashed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run e-commerce scraping pipelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --sources alta              # Run Alta only
  python main.py --sources koncept biblusi   # Run Koncept then Biblusi sequentially
  python main.py --sources alta koncept --parallel  # Run Alta and Koncept in parallel
  python main.py --all                       # Run all sources sequentially
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--sources', '-s',
        nargs='+',
        choices=get_all_sources(),
        help='Source(s) to scrape'
    )
    group.add_argument(
        '--all',
        action='store_true',
        help='Run all available sources'
    )

    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='Run sources in parallel (default: sequential)'
    )

    args = parser.parse_args()

    # Determine which sources to run
    sources_to_run = get_all_sources() if args.all else args.sources

    logger.info(f"Starting scraper for sources: {', '.join(sources_to_run)}")
    logger.info(f"Mode: {'parallel' if args.parallel else 'sequential'}")

    start = datetime.now()
    print(f"Started at: {start}")

    asyncio.run(main(sources_to_run, parallel=args.parallel))

    end = datetime.now()
    print(f"Completed at: {end}")
    print(f"Duration: {end - start}")