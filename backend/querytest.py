from app.core.query_executor import query_executor

# Check if queries loaded
queries = query_executor.list_queries()
print(f"Loaded queries: {queries}")
print(f"Total: {len(queries)}")

# Check specific query
config = query_executor.get_query_config("revenue_by_region")
if config:
    print("✅ revenue_by_region found")
    print(f"SQL preview: {config.get('sql', '')[:100]}...")
else:
    print("❌ revenue_by_region NOT found")

exit()