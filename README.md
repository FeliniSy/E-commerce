# VIPO E-Commerce Multi-Source Scraper

A dynamic, scalable web scraping system for e-commerce product data from multiple Georgian websites.

## 🚀 Quick Start

```bash
# Run a single source
python main.py --sources alta

# Run multiple sources
python main.py --sources koncept biblusi sportlines

# Run all sources
python main.py --all

#Run all sources in parallel
python main.py --all --parallel

# Run in parallel (faster)
python main.py --sources alta koncept --parallel
```

## 📦 Current Sources

| Source | Type | Products | Supplier ID |
|--------|------|----------|-------------|
| **Alta** | Technics/Electronics | Category-based | 1 |
| **Koncept** | Furniture | Collection-based | 2 |
| **Biblusi** | Books | ID-based | 3 |
| **Sportlines** | Sports Equipment | Paginated | 4 |

## ✨ Features

- **Dynamic Source Loading**: Add new sources without modifying core code
- **Multiple Scraping Patterns**: Category, Collection, ID-based, Paginated
- **Flexible Execution**: Run sources individually, sequentially, or in parallel
- **Preserved Logic**: All existing scraping logic remains unchanged
- **CLI Interface**: Simple command-line arguments
- **Centralized Config**: All source settings in one place

## 🏗️ Architecture

```
┌─────────────┐
│   main.py   │ ← CLI Entry Point
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ PipelineRunner   │ ← Orchestrator
└────┬─────────────┘
     │
     ├─→ SourceFactory ─→ Dynamic Module Loading
     │
     └─→ Scraping Patterns:
         • Category-based (Alta)
         • Collection-based (Koncept)
         • ID-based (Biblusi)
         • Paginated (Sportlines)
```

**Key Components**:
- `config/sources.py` - Source definitions
- `orchestrator/source_factory.py` - Dynamic module loader
- `orchestrator/pipeline_runner.py` - Unified pipeline execution
- `main.py` - CLI interface

## 📖 Documentation

- **[USAGE.md](USAGE.md)** - Detailed usage guide and CLI examples
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Before/after comparison

## 🧪 Testing

```bash
# Verify the dynamic system
python test_dynamic_system.py

# Test a specific source (dry run - check imports)
python -c "from orchestrator import PipelineRunner; PipelineRunner('alta')"
```

## 📁 Project Structure

```
vipo_e-commerce/
├── config/                      # NEW: Source configurations
│   ├── __init__.py
│   └── sources.py               # All source definitions
│
├── orchestrator/                # NEW: Dynamic orchestration
│   ├── __init__.py
│   ├── source_factory.py        # Module loader
│   └── pipeline_runner.py       # Pipeline executor
│
├── pipeline/
│   ├── extractor/               # Shared scraping
│   ├── loader/                  # Shared database insertion
│   ├── alta_transformer/        # Alta-specific parsing
│   ├── koncept_transformer/     # Koncept-specific parsing
│   ├── biblusi_transformer/     # Biblusi-specific parsing
│   └── sportlines_transformer/  # Sportlines-specific parsing
│
├── processes/
│   ├── alta_process.py          # Alta scraping logic
│   ├── koncept_process.py       # Koncept scraping logic
│   ├── biblusi_process.py       # Biblusi scraping logic
│   └── sportlines_process.py    # Sportlines scraping logic
│
├── db_manager/                  # Database operations
├── gcs_manager/                 # Google Cloud Storage
├── utils/                       # Utilities and helpers
│
├── main.py                      # UPDATED: Dynamic CLI entry point
└── test_dynamic_system.py       # NEW: System verification tests
```

## 🔧 Adding a New Source

1. **Create transformer** in `pipeline/newsource_transformer/`:
   ```
   ├── __init__.py
   ├── data_parser.py
   ├── spec_handler.py
   └── image_handler.py
   ```

2. **Create process** in `processes/newsource_process.py`

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
       scraping_type='category',  # or collection/id_based/paginated
       urls={...},
       extra_config={...}
   )
   ```

4. **Run it**:
   ```bash
   python main.py --sources newsource
   ```

## 🎯 Common Commands

```bash
# Alta electronics only
python main.py -s alta

# Books and furniture
python main.py -s biblusi koncept

# Everything sequentially
python main.py --all

# Multiple sources in parallel (faster, more resources)
python main.py -s alta sportlines --parallel

# Get help
python main.py --help
```

## 🔍 Environment

- **Python**: 3.12+
- **Database**: PostgreSQL
- **Storage**: Google Cloud Storage
- **Browser**: Playwright (Chromium)

## 📊 What Changed?

### Before
- ❌ Hardcoded to one source per script
- ❌ Manual editing to switch sources
- ❌ No easy way to run multiple sources
- ❌ Code duplication in orchestration

### After
- ✅ Dynamic source selection via CLI
- ✅ Zero code changes to switch sources
- ✅ Run any combination of sources
- ✅ Shared orchestration logic
- ✅ Easy to add new sources

**All existing logic preserved** - transformers, processes, and data flows unchanged!

## 🎉 Success Indicators

All tests pass:
```bash
$ python test_dynamic_system.py
✅ PASS: Imports
✅ PASS: Config Loading
✅ PASS: Source Factory
✅ PASS: Runner Initialization
✅ PASS: All Sources
🎉 All tests passed!
```

## 📝 Notes

- **Sequential mode** (default): Runs sources one at a time, safer
- **Parallel mode** (`--parallel`): Runs simultaneously, faster but uses more resources
- Logs: `logs/app.log` and `logs/errors.log`
- All transformers and processes remain unchanged
- No refactoring needed for existing code

## 🚦 Next Steps

1. ✅ Run `python test_dynamic_system.py` to verify installation
2. ✅ Try `python main.py --sources alta` for your first run
3. ✅ Read USAGE.md for more examples
4. 🔮 Add new sources using the simple 3-file pattern

---

**System Status**: ✅ Dynamic structure in place, all tests passing, ready to use!
