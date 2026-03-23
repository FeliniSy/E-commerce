"""
Test script to verify select_fields_by_category query
"""
from db_manager.queries import select_fields_by_category
from pipeline.loader.loader import loader


def test_query(category_id: int):
    print(f"\n{'='*80}")
    print(f"Testing query for category_id = {category_id}")
    print(f"{'='*80}\n")

    results = loader.fetch(select_fields_by_category, params=(category_id,))

    if not results:
        print(f"❌ No results found for category_id={category_id}")
        return

    print(f"✅ Found {len(results)} fields\n")

    # Group by field_groups
    grouped = {}
    for row in results:
        group_id, group_name, field_id, field_name, is_required = row

        if group_name not in grouped:
            grouped[group_name] = {
                'group_id': group_id,
                'fields': []
            }

        grouped[group_name]['fields'].append({
            'field_id': field_id,
            'field_name': field_name,
            'is_required': is_required
        })

    # Display results
    for group_name, group_data in grouped.items():
        print(f"\n📁 {group_name} (group_id: {group_data['group_id']})")
        print(f"   {len(group_data['fields'])} fields:")
        for field in group_data['fields']:
            required = "✓ REQUIRED" if field['is_required'] else ""
            print(f"   - [{field['field_id']}] {field['field_name']} {required}")

    print(f"\n{'='*80}")
    print(f"Total: {len(grouped)} field groups, {len(results)} fields")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Test with category_id = 16 (Hair Dryer)
    test_query(16)

    # You can test other categories too:
    # test_query(1)
    # test_query(15)
