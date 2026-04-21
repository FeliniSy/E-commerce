# Migration Guide: Before vs After

## What Changed?

Your existing scraping logic is **100% preserved**. We added a dynamic layer on top to eliminate code duplication and make it easy to run any source.

## Before (Old Way)

### Running Different Sources

```python
# main.py was hardcoded to Alta only
from processes.alta_process import process_category
from pipeline.alta_transformer.brand_handler import clear_brand_cache

async def main():
    clear_brand_cache()
    # ... hardcoded Alta logic
```

To run other sources, you had to:
1. Edit main.py manually
2. Change imports
3. Change function calls
4. Remember each source's specific parameters

### Adding a New Source

Required changing:
- ❌ main.py (add new imports and logic)
- ❌ Manual coordination of which source runs when
- ❌ Copy-paste similar orchestration code

## After (New Way)

### Running Different Sources

```bash
# Run Alta
python main.py --sources alta

# Run Koncept
python main.py --sources koncept

# Run multiple
python main.py --sources alta koncept biblusi

# Run all
python main.py --all
```

**No code changes needed!** Just pass different arguments.

### Adding a New Source

Only need to:
1. ✅ Create `processes/newsource_process.py` (your logic)
2. ✅ Create `pipeline/newsource_transformer/` (your parsers)
3. ✅ Add config to `config/sources.py` (one entry)

**That's it!** The orchestrator handles the rest.

## Side-by-Side Comparison

### Before: main.py
```python
# Hardcoded to Alta
import asyncio
from processes.alta_process import process_category
from pipeline.alta_transformer.brand_handler import clear_brand_cache

async def main():
    clear_brand_cache()
    product_semaphore = asyncio.Semaphore(30)
    category_semaphore = asyncio.Semaphore(10)
    
    async def process_category_with_semaphore(category_id):
        async with category_semaphore:
            await process_category(category_id, product_semaphore)
    
    await asyncio.gather(*[
        process_category_with_semaphore(i) for i in range(1, 295)
    ])

if __name__ == "__main__":
    asyncio.run(main())
```

### After: main.py
```python
# Works for all sources
import asyncio
import argparse
from orchestrator.pipeline_runner import run_pipeline
from config import get_all_sources

async def main(sources: list[str], parallel: bool = False):
    if len(sources) == 1:
        await run_pipeline(sources[0])
    else:
        await run_multiple_sources(sources, sequential=not parallel)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', nargs='+', choices=get_all_sources())
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()
    
    sources_to_run = get_all_sources() if args.all else args.sources
    asyncio.run(main(sources_to_run))
```

## What Stayed the Same?

### ✅ All Process Logic
```
processes/
├── alta_process.py        # Unchanged
├── koncept_process.py     # Unchanged
├── biblusi_process.py     # Unchanged
└── sportlines_process.py  # Unchanged
```

### ✅ All Transformers
```
pipeline/
├── alta_transformer/      # Unchanged
├── koncept_transformer/   # Unchanged
├── biblusi_transformer/   # Unchanged
└── sportlines_transformer/# Unchanged
```

### ✅ All Shared Components
```
pipeline/
├── extractor/scrapper.py      # Unchanged
└── loader/product_loader.py   # Unchanged
```

### ✅ Database, Utils, Settings
```
db_manager/    # Unchanged
gcs_manager/   # Unchanged
utils/         # Unchanged
```

## What's New?

### ✨ Configuration System
```
config/
└── sources.py    # NEW: Centralized source definitions
```

### ✨ Orchestration Layer
```
orchestrator/
├── source_factory.py      # NEW: Dynamic module loader
└── pipeline_runner.py     # NEW: Unified pipeline runner
```

### ✨ CLI Interface
```bash
python main.py --sources alta koncept --parallel
```

## Usage Examples

### Old Way vs New Way

| Task | Before | After |
|------|--------|-------|
| Run Alta | Edit main.py, hardcode Alta | `python main.py -s alta` |
| Run Koncept | Edit main.py, change imports | `python main.py -s koncept` |
| Run Both | Create separate scripts | `python main.py -s alta koncept` |
| Run All | Manual orchestration | `python main.py --all` |
| Add Source | Edit main.py + orchestration | Add config entry only |

## Benefits Summary

### Before
- ❌ One source per run (hardcoded)
- ❌ Manual editing for each source
- ❌ Code duplication in orchestration
- ❌ No easy way to run multiple sources
- ❌ Adding sources requires multiple file changes

### After
- ✅ Any source via CLI argument
- ✅ No code editing needed
- ✅ Shared orchestration logic
- ✅ Run sources sequentially or in parallel
- ✅ Adding sources = config + transformer + process

## Testing the New System

### Verify It Works
```bash
# Test config loading
python -c "from config import get_all_sources; print(get_all_sources())"

# Test help
python main.py --help

# Test dry run (check imports work)
python -c "from orchestrator.pipeline_runner import PipelineRunner; print('OK')"
```

### Run Your First Dynamic Pipeline
```bash
# Start with a single source
python main.py --sources alta

# Try multiple sources
python main.py --sources koncept biblusi
```

## Rollback Plan

If you need to revert:
1. The old logic is preserved in `temporary_files/main_*.py`
2. All transformers and processes are unchanged
3. Simply restore old main.py from git:
   ```bash
   git checkout main.py
   ```

## Questions?

**Q: Will my existing code break?**
A: No! All transformers, processes, and shared components are unchanged.

**Q: Do I need to refactor my transformers?**
A: No! They work as-is. The factory loads them dynamically.

**Q: Can I still manually import and run processes?**
A: Yes! The old way still works if needed for debugging.

**Q: What if I add a source with a new pattern?**
A: Extend `PipelineRunner` with a new method (e.g., `_run_new_pattern()`), then set `scraping_type='new_pattern'` in config.

## Next Steps

1. ✅ Try running: `python main.py --sources alta`
2. ✅ Read `USAGE.md` for CLI examples
3. ✅ Read `ARCHITECTURE.md` for system design
4. ✅ Start using CLI for all scraping tasks
5. 🔮 Future: Add new sources using the simple 3-file pattern
