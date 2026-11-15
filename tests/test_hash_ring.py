import pytest

from coordinator.hash_ring import ConsistentHashRing


def test_virtual_nodes():
    ring = ConsistentHashRing(100)

    ring.add_shard("shard-1")
    ring.add_shard("shard-2")

    assert ring.position_count == 200


def test_deterministic_routing():
    ring = ConsistentHashRing(100)

    ring.add_shard("shard-1")
    ring.add_shard("shard-2")

    first = ring.get_shard("students", "101")
    second = ring.get_shard("students", "101")

    assert first == second


def test_distribution_across_shards():
    ring = ConsistentHashRing(100)

    ring.add_shard("shard-1")
    ring.add_shard("shard-2")

    selected = {
        ring.get_shard("students", str(key))
        for key in range(100)
    }

    assert selected == {"shard-1", "shard-2"}


def test_adding_shard_changes_only_its_keys():
    ring = ConsistentHashRing(100)

    ring.add_shard("shard-1")
    ring.add_shard("shard-2")

    keys = [str(key) for key in range(300)]

    before = {
        key: ring.get_shard("students", key)
        for key in keys
    }

    ring.add_shard("shard-3")

    after = {
        key: ring.get_shard("students", key)
        for key in keys
    }

    changed = [
        key for key in keys
        if before[key] != after[key]
    ]

    assert len(changed) > 0
    assert len(changed) < len(keys)

    assert all(
        after[key] == "shard-3"
        for key in changed
    )


def test_no_shards_registered():
    ring = ConsistentHashRing(100)

    with pytest.raises(RuntimeError):
        ring.get_shard("students", "101")
