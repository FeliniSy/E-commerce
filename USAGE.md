# Dynamic Multi-Source Scraper Usage Guide

## Overview

This project now supports dynamic scraping from multiple sources without code duplication. All sources share the same pipeline logic and can be run individually or in combination.

## Available Sources

- **alta** - Technics/electronics from alta.ge (category-based)
- **koncept** - Furniture from koncept.ge (collection-based)
- **biblusi** - Books from biblusi.ge (ID-based)
- **sportlines** - Sports equipment from sportlines.ge (paginated)

## Running the Scraper

### Basic Usage

```bash
# Run a single source
python main.py --sources alta

# Run multiple sources sequentially
python main.py --sources koncept biblusi

# Run all sources sequentially
python main.py --all

# Run sources in parallel
python main.py --sources alta koncept --parallel
```

### Short Flags

```bash
# -s for --sources
python main.py -s alta

# -p for --parallel
python main.py -s alta koncept -p
```

## Architecture

### Directory Structure

```
vipo_e-commerce/
├── config/                          # Source configurations
│   └── sources.py                   # All source definitions
│
├── orchestrator/                    # Dynamic pipeline system
│   ├── source_factory.py           # Dynamically loads source modules
│   └── pipeline_runner.py          # Unified pipeline orchestrator
│
├── pipeline/                        # Shared pipeline components
│   ├── extractor/                   # Scraping logic
│   ├── loader/                      # Database insertion
│   └── *_transformer/               # Source-specific transformers
│
├── processes/                       # Source-specific process logic
│   ├── alta_process.py
│   ├── koncept_process.py
│   ├── biblusi_process.py
│   └── sportlines_process.py
│
└── main.py                          # Unified entry point
```

### How It Works

1. **Configuration** (`config/sources.py`): Defines each source's modules, URLs, and scraping pattern
2. **Factory** (`orchestrator/source_factory.py`): Dynamically imports the right modules at runtime
3. **Runner** (`orchestrator/pipeline_runner.py`): Orchestrates the pipeline based on scraping pattern
4. **Main** (`main.py`): CLI interface to select and run sources

## Adding a New Source

To add a new source, you only need to:

1. **Create transformer modules** (copy existing pattern):
   ```
   pipeline/newsource_transformer/
   ├── __init__.py
   ├── data_parser.py
   ├── spec_handler.py
   ├── image_handler.py
   └── category_handler.py
   ```

2. **Create process file**:
   ```
   processes/newsource_process.py
   ```

3. **Add configuration** in `config/sources.py`:
   ```python
   'newsource': SourceConfig(
       name='newsource',
       supplier_id=5,
       process_module='processes.newsource_process',
       process_function='process_newsource',
       transformer_module='pipeline.newsource_transformer',
       data_parser_function='data_parser.parse_newsource_product',
       spec_handler_function='spec_handler.parse_newsource_specifications',
       image_handler_function='image_handler.parse_newsource_images',
       scraping_type='category',  # or 'collection', 'id_based', 'paginated'
       urls={...},
       extra_config={...}
   )
   ```

4. **Run it**:
   ```bash
   python main.py --sources newsource
   ```

## Scraping Patterns

### Category-based (Alta)
Iterates through category IDs, fetches products per category page by page.

### Collection-based (Koncept)
Fetches collections first, then iterates through products in each collection.

### ID-based (Biblusi)
Fetches all product IDs first, then processes each product individually.

### Paginated (Sportlines)
Iterates through paginated API endpoints until no more products.

## Configuration Details

Each source in `config/sources.py` has:

- `supplier_id`: Database supplier identifier
- `process_module`: Python module containing the processing logic
- `transformer_module`: Base module for transformers
- `scraping_type`: Pattern to use (category/collection/id_based/paginated)
- `urls`: API endpoints
- `extra_config`: Source-specific settings (semaphores, ranges, etc.)

## Examples

```bash
# Scrape only Alta technics
python main.py -s alta

# Scrape furniture and books
python main.py -s koncept biblusi

# Scrape all sources at once (sequential)
python main.py --all

# Scrape Alta and Sportlines in parallel (faster)
python main.py -s alta sportlines --parallel
```

## Notes

- **Sequential mode** (default): Runs one source at a time, safer for shared resources
- **Parallel mode**: Runs sources concurrently, faster but uses more resources
- All existing logic remains unchanged, just organized dynamically
- Logs are centralized in `logs/app.log` and `logs/errors.log`
