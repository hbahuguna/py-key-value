import time
import pytest
from src.key_value.aio.stores.memory.store import MemoryCacheEntry


def test_memory_cache_entry_initialization():
    """Tests that MemoryCacheEntry initializes correctly with content and expiration."""
    content = b"serialized_data"
    expires_at = time.time() + 3600  # 1 hour from now
    entry = MemoryCacheEntry(content=content, expires_at=expires_at)

    assert entry.content == content
    assert entry.expires_at == expires_at


def test_memory_cache_entry_is_not_expired():
    """Tests that is_expired returns False for an unexpired entry."""
    content = b"some_data"
    expires_at = time.time() + 100  # Expires in 100 seconds
    entry = MemoryCacheEntry(content=content, expires_at=expires_at)

    # Simulate current time before expiration
    assert not entry.is_expired(current_time=expires_at - 1)
    assert not entry.is_expired(current_time=time.time() - 1) # Using actual time, should be false if expires_at is in future


def test_memory_cache_entry_is_expired():
    """Tests that is_expired returns True for an expired entry."""
    content = b"old_data"
    expires_at = time.time() - 100  # Expired 100 seconds ago
    entry = MemoryCacheEntry(content=content, expires_at=expires_at)

    # Simulate current time after expiration
    assert entry.is_expired(current_time=expires_at + 1)
    assert entry.is_expired(current_time=time.time() + 1) # Using actual time, should be true if expires_at is in past


def test_memory_cache_entry_is_expired_at_exact_time():
    """Tests that is_expired returns True at the exact expiration timestamp."""
    content = b"data_at_edge"
    expires_at = time.time() + 50 # Expires in 50 seconds
    entry = MemoryCacheEntry(content=content, expires_at=expires_at)

    # Simulate current time exactly at expiration
    assert entry.is_expired(current_time=expires_at)


def test_memory_cache_entry_with_different_content_types():
    """Tests MemoryCacheEntry with various content types (assuming serialization handles them)."""
    test_cases = [
        ("string_content", time.time() + 100),
        (12345, time.time() + 200),
        ({"key": "value"}, time.time() + 300),
        ([1, 2, 3], time.time() + 400),
        (None, time.time() + 500) # Assuming None is a valid content
    ]

    for content, expires_at in test_cases:
        entry = MemoryCacheEntry(content=content, expires_at=expires_at)
        assert entry.content == content
        assert entry.expires_at == expires_at
        assert not entry.is_expired(current_time=expires_at - 1)


def test_memory_cache_entry_equality():
    """Tests the equality (==) operator for MemoryCacheEntry instances."""
    t = time.time()
    entry1 = MemoryCacheEntry(content=b"data1", expires_at=t + 100)
    entry2 = MemoryCacheEntry(content=b"data1", expires_at=t + 100)
    entry3 = MemoryCacheEntry(content=b"data2", expires_at=t + 100)
    entry4 = MemoryCacheEntry(content=b"data1", expires_at=t + 200)

    assert entry1 == entry2
    assert entry1 != entry3
    assert entry1 != entry4
    assert entry2 != entry3
    assert entry2 != entry4

    # Test with non-MemoryCacheEntry object
    assert entry1 != "not_an_entry"


def test_memory_cache_entry_repr():
    """Tests the string representation (__repr__) of MemoryCacheEntry."""
    content = b"repr_test_data"
    expires_at = 1678886400.0  # A fixed timestamp for consistent testing
    entry = MemoryCacheEntry(content=content, expires_at=expires_at)

    expected_repr = f"MemoryCacheEntry(content={content!r}, expires_at={expires_at})"
    assert repr(entry) == expected_repr


def test_memory_cache_entry_immutability_of_attributes():
    """Tests that attributes are read-only after initialization (if implemented as dataclass/frozen)."""
    content = b"initial_data"
    expires_at = time.time() + 100
    entry = MemoryCacheEntry(content=content, expires_at=expires_at)

    # Attempt to modify attributes directly
    with pytest.raises(AttributeError): # Expecting AttributeError if it's a frozen dataclass or has __slots__
        entry.content = b"new_data"
    with pytest.raises(AttributeError): # Expecting AttributeError if it's a frozen dataclass or has __slots__
        entry.expires_at = time.time() + 200

    # If it's a regular class without __slots__ or frozen=True, this test might fail or need adjustment.
    # For a simple class, direct assignment would work, but for a cache entry, immutability is often desired.
    # If the above raises AttributeError, it means the class is designed to be immutable for these fields.
    # If it doesn't, it means the fields are mutable, which might be an acceptable design choice.
    # For this test, we assume a desire for immutability based on typical cache entry patterns.
