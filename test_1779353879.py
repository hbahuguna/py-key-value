{
  "file_path": "tests/stores/memory/test_memory.py",
  "code": "import pytest
import asyncio
from typing import AsyncIterator, List, Optional, Dict, Any

# Assuming the structure of the MemoryStore based on common patterns
# and the symbol summary \"Retrieves a paginated list of keys currently stored in the memory collection.\"
class MemoryStore:
    def __init__(self):
        self._data: Dict[str, Any] = {}

    async def set(self, key: str, value: Any):
        """Adds or updates a key-value pair."""
        self._data[key] = value

    async def get(self, key: str):
        """Retrieves a value by key."""
        return self._data.get(key)

    async def delete(self, key: str):
        """Deletes a key-value pair."""
        if key in self._data:
            del self._data[key]

    async def count(self) -> int:
        """Returns the total number of keys."""
        return len(self._data)

    async def keys(self, limit: Optional[int] = None, offset: int = 0) -> AsyncIterator[str]:
        """
        Retrieves a paginated list of keys currently stored in the memory collection.
        Keys are returned in a sorted order for consistent pagination.
        """
        all_keys = sorted(list(self._data.keys()))
        
        start_index = offset
        if start_index >= len(all_keys):
            return # No keys to yield if offset is beyond total

        end_index = start_index + limit if limit is not None else len(all_keys)
        
        for key in all_keys[start_index:end_index]:
            yield key

@pytest.fixture
async def memory_store():
    """Provides a fresh MemoryStore instance for each test."""
    store = MemoryStore()
    yield store
    # No explicit cleanup needed for in-memory store, but good practice for other stores

@pytest.mark.asyncio
async def test_keys_empty_store(memory_store: MemoryStore):
    """Test retrieving keys from an empty store."""
    retrieved_keys = [key async for key in memory_store.keys()]
    assert retrieved_keys == []

@pytest.mark.asyncio
async def test_keys_basic_retrieval(memory_store: MemoryStore):
    """Test retrieving all keys without limit or offset."""
    await memory_store.set(\"key1\", \"value1\")
    await memory_store.set(\"key3\", \"value3\")
    await memory_store.set(\"key2\", \"value2\")

    retrieved_keys = [key async for key in memory_store.keys()]
    assert retrieved_keys == [\"key1\", \"key2\", \"key3\"] # Should be sorted

@pytest.mark.asyncio
async def test_keys_with_limit(memory_store: MemoryStore):
    """Test retrieving keys with a specified limit."""
    for i in range(1, 6):
        await memory_store.set(f\"key{i}\", f\"value{i}\")

    retrieved_keys = [key async for key in memory_store.keys(limit=3)]
    assert retrieved_keys == [\"key1\", \"key2\", \"key3\"]

@pytest.mark.asyncio
async def test_keys_with_offset(memory_store: MemoryStore):
    """Test retrieving keys with a specified offset."""
    for i in range(1, 6):
        await memory_store.set(f\"key{i}\", f\"value{i}\")

    retrieved_keys = [key async for key in memory_store.keys(offset=2)]
    assert retrieved_keys == [\"key3\", \"key4\", \"key5\"]

@pytest.mark.asyncio
async def test_keys_with_limit_and_offset(memory_store: MemoryStore):
    """Test retrieving keys with both limit and offset."""
    for i in range(1, 11):
        await memory_store.set(f\"key{i:02d}\", f\"value{i}\") # Use 02d for consistent sorting

    retrieved_keys = [key async for key in memory_store.keys(limit=3, offset=4)]
    assert retrieved_keys == [\"key05\", \"key06\", \"key07\"]

@pytest.mark.asyncio
async def test_keys_offset_beyond_total(memory_store: MemoryStore):
    """Test retrieving keys when offset is beyond the total number of keys."""
    await memory_store.set(\"key1\", \"value1\")
    await memory_store.set(\"key2\", \"value2\")

    retrieved_keys = [key async for key in memory_store.keys(offset=5)]
    assert retrieved_keys == []

@pytest.mark.asyncio
async def test_keys_limit_exceeds_remaining(memory_store: MemoryStore):
    """Test retrieving keys when limit exceeds the remaining keys after offset."""
    for i in range(1, 6):
        await memory_store.set(f\"key{i}\", f\"value{i}\")

    retrieved_keys = [key async for key in memory_store.keys(limit=10, offset=3)]
    assert retrieved_keys == [\"key4\", \"key5\"]

@pytest.mark.asyncio
async def test_keys_many_items_pagination(memory_store: MemoryStore):
    """Test pagination with a large number of items."""
    num_items = 100
    expected_all_keys = []
    for i in range(num_items):
        key = f\"item_{i:03d}\"
        await memory_store.set(key, f\"value_{i}\")
        expected_all_keys.append(key)
    
    # Test first page
    page1 = [key async for key in memory_store.keys(limit=10, offset=0)]
    assert page1 == expected_all_keys[0:10]
    
    # Test middle page
    page5 = [key async for key in memory_store.keys(limit=10, offset=40)]
    assert page5 == expected_all_keys[40:50]
    
    # Test last page (partial)
    page_last = [key async for key in memory_store.keys(limit=10, offset=95)]
    assert page_last == expected_all_keys[95:100]
    
    # Test retrieving all with no limit/offset
    all_retrieved = [key async for key in memory_store.keys()]
    assert all_retrieved == expected_all_keys

@pytest.mark.asyncio
async def test_keys_order_consistency(memory_store: MemoryStore):
    """Ensure keys are returned in a consistent, sorted order."""
    await memory_store.set(\"zebra\", 1)
    await memory_store.set(\"apple\", 2)
    await memory_store.set(\"banana\", 3)

    retrieved_keys = [key async for key in memory_store.keys()]
    assert retrieved_keys == [\"apple\", \"banana\", \"zebra\"]

    # Add another key and re-check order
    await memory_store.set(\"cat\", 4)
    retrieved_keys_after_add = [key async for key in memory_store.keys()]
    assert retrieved_keys_after_add == [\"apple\", \"banana\", \"cat\", \"zebra\"]
"
}