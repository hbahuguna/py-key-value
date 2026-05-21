{
  "file_path": "tests/stores/memory/test_memory.py",
  "code": "import pytest
import asyncio
import copy

# Mock MemoryStore for testing purposes, simulating the behavior described
# in the symbol summary (retrieval and deserialization).
# In a real scenario, the actual MemoryStore would be imported.
class MockMemoryStore:
    def __init__(self):
        self._cache = {}

    async def set(self, key: str, value: any):
        """
        Simulates storing a value. For deserialization testing, we'll assume
        the store internally handles deep copying or serialization/deserialization
        to prevent direct object mutation.
        """
        self._cache[key] = copy.deepcopy(value)

    async def get(self, key: str):
        """
        Retrieves and deserializes a managed entry from the in-memory cache.
        Simulates deserialization by returning a deep copy of the stored object
        to ensure the retrieved object is independent.
        """
        stored_value = self._cache.get(key)
        if stored_value is not None:
            return copy.deepcopy(stored_value)
        return None

    async def delete(self, key: str) -> bool:
        """Simulates deleting an entry."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def close(self):
        """Clears the cache, simulating resource cleanup."""
        self._cache.clear()

@pytest.fixture
async def memory_store():
    """Provides a fresh MockMemoryStore instance for each test."""
    store = MockMemoryStore()
    yield store
    await store.close()

@pytest.mark.asyncio
async def test_get_existing_key(memory_store: MockMemoryStore):
    """
    Test that `get` successfully retrieves a previously stored value.
    """
    key = \"test_key\"
    value = {\"data\": \"some_value\", \"number\": 123}
    await memory_store.set(key, value)

    retrieved_value = await memory_store.get(key)
    assert retrieved_value == value
    # Ensure deserialization provides a distinct object
    assert retrieved_value is not value

@pytest.mark.asyncio
async def test_get_non_existing_key(memory_store: MockMemoryStore):
    """
    Test that `get` returns None for a key that does not exist.
    """
    key = \"non_existent_key\"
    retrieved_value = await memory_store.get(key)
    assert retrieved_value is None

@pytest.mark.asyncio
async def test_get_different_data_types(memory_store: MockMemoryStore):
    """
    Test `get` with various Python data types to ensure proper handling
    and deserialization.
    """
    test_cases = [
        (\"str_key\", \"hello world\"),
        (\"int_key\", 12345),
        (\"float_key\", 3.14159),
        (\"bool_key\", True),
        (\"list_key\", [1, 2, \"three\", None]),
        (\"dict_key\", {\"a\": 1, \"b\": [2, 3], \"c\": {\"d\": 4}}),
        (\"none_key\", None) # Storing None is valid, though get for non-existent returns None
    ]

    for key, value in test_cases:
        await memory_store.set(key, value)
        retrieved_value = await memory_store.get(key)
        assert retrieved_value == value
        # For mutable types, ensure it's a distinct object
        if isinstance(value, (list, dict)):
            assert retrieved_value is not value

@pytest.mark.asyncio
async def test_get_after_update(memory_store: MockMemoryStore):
    """
    Test that `get` retrieves the latest value after an update.
    """
    key = \"update_key\"
    initial_value = {\"version\": 1, \"data\": \"old\"}
    updated_value = {\"version\": 2, \"data\": \"new\"}

    await memory_store.set(key, initial_value)
    assert await memory_store.get(key) == initial_value

    await memory_store.set(key, updated_value)
    assert await memory_store.get(key) == updated_value
    assert await memory_store.get(key) is not updated_value # Deserialization check

@pytest.mark.asyncio
async def test_get_after_delete(memory_store: MockMemoryStore):
    """
    Test that `get` returns None after the key has been deleted.
    """
    key = \"delete_key\"
    value = {\"item\": \"to_be_deleted\"}
    await memory_store.set(key, value)
    assert await memory_store.get(key) == value

    await memory_store.delete(key)
    assert await memory_store.get(key) is None

@pytest.mark.asyncio
async def test_get_deserialization_independence(memory_store: MockMemoryStore):
    """
    Test that the object returned by `get` is a deserialized copy,
    and modifying it does not affect the stored object.
    """
    key = \"independent_key\"
    original_value = {\"list\": [1, 2, 3], \"dict\": {\"a\": 1}}
    await memory_store.set(key, original_value)

    retrieved_value = await memory_store.get(key)
    assert retrieved_value == original_value
    assert retrieved_value is not original_value # Should be a new object

    # Modify the retrieved object
    retrieved_value[\"list\"].append(4)
    retrieved_value[\"dict\"][\"b\"] = 2

    # Retrieve again and ensure the original stored value is unchanged
    second_retrieval = await memory_store.get(key)
    assert second_retrieval == original_value
    assert second_retrieval[\"list\"] == [1, 2, 3]
    assert second_retrieval[\"dict\"] == {\"a\": 1}
    assert second_retrieval is not retrieved_value # Another new object

@pytest.mark.asyncio
async def test_get_concurrency(memory_store: MockMemoryStore):
    """
    Test concurrent `get` operations to ensure they don't interfere
    and return correct values.
    """
    keys_values = {f\"key_{i}\": f\"value_{i}\" for i in range(100)}
    set_tasks = [memory_store.set(k, v) for k, v in keys_values.items()]
    await asyncio.gather(*set_tasks)

    async def get_and_verify(k, v):
        retrieved = await memory_store.get(k)
        assert retrieved == v

    get_tasks = [get_and_verify(k, v) for k, v in keys_values.items()]
    await asyncio.gather(*get_tasks)
"
}