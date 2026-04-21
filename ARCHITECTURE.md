# Architecture Overview

## System Flow

```
┌─────────────┐
│  main.py    │  CLI Entry Point
│  (--sources)│  Accepts source names as arguments
└──────┬──────┘
       │
       ▼
┌────────────────────────┐
│  PipelineRunner        │  Orchestrator
│  (pipeline_runner.py)  │  Routes to correct scraping pattern
└───────┬────────────────┘
        │
        ├──────────────┬──────────────┬──────────────┬──────────────┐
        │              │              │              │              │
        ▼              ▼              ▼              ▼              ▼
   ┌─────────┐   ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐
   │Category │   │Collection│  │ ID-based │  │ Paginated │  │Future      │
   │Pattern  │   │Pattern   │  │ Pattern  │  │ Pattern   │  │Patterns... │
   │(Alta)   │   │(Koncept) │  │(Biblusi) │  │(Sportline)│  │            │
   └────┬────┘   └─────┬────┘  └────┬─────┘  └─────┬─────┘  └────────────┘
        │              │             │              │
        ▼              ▼             ▼              ▼
┌──────────────────────────────────────────────────────────┐
│              SourceFactory                               │
│  Dynamically loads:                                      │
│  • Process functions (from processes/*.py)               │
│  • Transformers (from pipeline/*_transformer/)           │
│  • Data parsers, spec handlers, image handlers           │
└─────────────────────┬────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌────────────┐  ┌──────────┐  ┌──────────┐
│ Extractor  │  │Transform │  │  Loader  │
│ (scrapper) │  │ (parse)  │  │ (insert) │
└────────────┘  └──────────┘  └──────────┘
        │             │             │
        └─────────────┼─────────────┘
                      ▼
              ┌───────────────┐
              │   Database    │
              │   (products)  │
              └───────────────┘
```

## Component Responsibilities

### 1. Configuration Layer (`config/`)
**Purpose**: Central source of truth for all sources

- `sources.py`: Defines each source's:
  - URLs and API endpoints
  - Module paths (process, transformer)
  - Scraping pattern type
  - Supplier ID and settings

**Benefit**: Add/modify sources without touching code

### 2. Orchestration Layer (`orchestrator/`)

#### SourceFactory (`source_factory.py`)
**Purpose**: Dynamic module loader

- Imports process functions at runtime
- Loads transformers based on source name
- Retrieves handlers (data, spec, image)
- Gets helper functions (collection fetcher, ID fetcher)

**Benefit**: No hardcoded imports, fully dynamic

#### PipelineRunner (`pipeline_runner.py`)
**Purpose**: Unified pipeline execution

- Routes to correct scraping pattern
- Manages semaphores and concurrency
- Handles browser lifecycle
- Supports sequential or parallel execution

**Benefit**: One runner for all sources

### 3. Process Layer (`processes/`)
**Purpose**: Source-specific scraping logic (UNCHANGED)

Each `*_process.py` file contains:
- Product processing function
- Category/collection/page iteration logic
- Error handling

**Benefit**: Existing logic preserved, no refactoring needed

### 4. Transformation Layer (`pipeline/`)
**Purpose**: Data transformation and parsing (UNCHANGED)

Each `*_transformer/` contains:
- `data_parser.py`: Raw data → ParsedProduct
- `spec_handler.py`: Product specifications
- `image_handler.py`: Image processing
- `category_handler.py`: Category mapping

**Benefit**: Transformer logic untouched

### 5. Shared Components (`pipeline/`)

- **Extractor** (`extractor/scrapper.py`): Shared browser automation
- **Loader** (`loader/product_loader.py`): Shared database insertion

## Scraping Pattern Types

### Category-based (Alta)
```
For each category (1-294):
  For each page (1-10000):
    Scrape products → Transform → Load
```

### Collection-based (Koncept)
```
Fetch all collections →
  For each collection:
    For each page:
      Scrape products → Transform → Load
```

### ID-based (Biblusi)
```
Fetch all product IDs →
  For each ID:
    Scrape product → Transform → Load
```

### Paginated (Sportlines)
```
For each page (1-100):
  Scrape products → Transform → Load
  Break if no products
```

## Data Flow Example (Alta)

```
1. User runs: python main.py --sources alta

2. main.py creates PipelineRunner('alta')

3. PipelineRunner loads config for 'alta':
   - scraping_type = 'category'
   - process_module = 'processes.alta_process'

4. SourceFactory dynamically imports:
   - processes.alta_process.process_category
   - pipeline.alta_transformer.data_parser.parse_data
   - pipeline.alta_transformer.spec_handler.parse_specifications

5. PipelineRunner._run_category_based() executes:
   - Iterates categories 1-294
   - Each category → process_category()
   - Each product → parse_data() → insert_product_to_db()

6. Pipeline completes, browser closes
```

## Adding a New Source

```
1. Create transformer:
   pipeline/newsource_transformer/
   ├── data_parser.py
   ├── spec_handler.py
   └── image_handler.py

2. Create process:
   processes/newsource_process.py

3. Add config:
   config/sources.py → SOURCES['newsource'] = SourceConfig(...)

4. Run:
   python main.py --sources newsource
```

**No changes needed to**:
- main.py
- orchestrator/
- Other sources

## Key Benefits

✅ **No Code Duplication**: Shared factory and runner
✅ **Easy to Extend**: Add source = config + transformer + process
✅ **Existing Logic Preserved**: All transformers/processes unchanged
✅ **Dynamic**: No hardcoded source names or imports
✅ **Flexible**: Run any combination of sources
✅ **CLI-friendly**: Simple command-line interface

## Migration Path

Current state: ✅ Dynamic system in place

**Phase 1 (Completed)**:
- ✅ Created config system
- ✅ Built source factory
- ✅ Created pipeline runner
- ✅ Updated main.py with CLI

**Phase 2 (Future - Optional)**:
- Consolidate shared handlers (brand, image) into `pipeline/shared/`
- Create base transformer class
- Move common patterns into mixins

**Phase 3 (Future - Optional)**:
- Add source-specific tests
- Create web dashboard
- Add scheduling/cron support
