#!/usr/bin/env python3
"""
Test script to verify the dynamic system is working correctly
Run: python test_dynamic_system.py
"""

def test_imports():
    """Test that all new modules can be imported"""
    print("Testing imports...")

    try:
        from config import get_all_sources, get_source_config, SOURCES
        print("✅ Config imports successful")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False

    try:
        from orchestrator import SourceFactory, PipelineRunner
        print("✅ Orchestrator imports successful")
    except ImportError as e:
        print(f"❌ Orchestrator import failed: {e}")
        return False

    return True


def test_config_loading():
    """Test that all sources can be loaded from config"""
    print("\nTesting config loading...")

    from config import get_all_sources, get_source_config

    sources = get_all_sources()
    print(f"✅ Found {len(sources)} sources: {sources}")

    for source_name in sources:
        try:
            config = get_source_config(source_name)
            print(f"✅ {source_name}: supplier_id={config.supplier_id}, type={config.scraping_type}")
        except Exception as e:
            print(f"❌ {source_name}: Failed to load config - {e}")
            return False

    return True


def test_factory():
    """Test that the factory can load modules"""
    print("\nTesting source factory...")

    from config import get_source_config
    from orchestrator import SourceFactory

    # Test loading Alta modules
    try:
        alta_config = get_source_config('alta')
        factory = SourceFactory()

        # Test loading process function
        process_func = factory.get_process_function(alta_config)
        print(f"✅ Loaded process function: {process_func.__name__}")

        # Test loading data parser
        data_parser = factory.get_data_parser(alta_config)
        print(f"✅ Loaded data parser: {data_parser.__name__}")

        # Test loading spec handler
        spec_handler = factory.get_spec_handler(alta_config)
        print(f"✅ Loaded spec handler: {spec_handler.__name__}")

        return True
    except Exception as e:
        print(f"❌ Factory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_runner_initialization():
    """Test that PipelineRunner can be initialized"""
    print("\nTesting pipeline runner initialization...")

    from orchestrator import PipelineRunner

    try:
        runner = PipelineRunner('alta')
        print(f"✅ Created runner for 'alta'")
        print(f"   - Source: {runner.source_name}")
        print(f"   - Scraping type: {runner.config.scraping_type}")
        print(f"   - Supplier ID: {runner.config.supplier_id}")
        return True
    except Exception as e:
        print(f"❌ Runner initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_sources():
    """Test that all sources can be initialized"""
    print("\nTesting all source initializations...")

    from config import get_all_sources
    from orchestrator import PipelineRunner

    sources = get_all_sources()
    for source_name in sources:
        try:
            runner = PipelineRunner(source_name)
            print(f"✅ {source_name}: Runner initialized successfully")
        except Exception as e:
            print(f"❌ {source_name}: Failed to initialize - {e}")
            return False

    return True


def main():
    print("=" * 60)
    print("Dynamic System Test Suite")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Config Loading", test_config_loading),
        ("Source Factory", test_factory),
        ("Runner Initialization", test_runner_initialization),
        ("All Sources", test_all_sources),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result for _, result in results)

    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! Dynamic system is working correctly.")
        print("\nYou can now run:")
        print("  python main.py --sources alta")
        print("  python main.py --sources koncept biblusi")
        print("  python main.py --all")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
