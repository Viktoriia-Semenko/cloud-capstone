import hashlib
from bisect import bisect_left


class ConsistentHashRing:
    def __init__(self, virtual_nodes: int = 100):
        if virtual_nodes < 1:
            raise ValueError("Virtual nodes must be positive")

        self.virtual_nodes = virtual_nodes
        self._ring: list[tuple[int, str]] = []
        self._shards: set[str] = set()

    @staticmethod
    def _hash(value: str) -> int:
        digest = hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

        return int(digest, 16)

    def add_shard(self, shard_id: str) -> bool:
        if not shard_id:
            raise ValueError("Shard ID cannot be empty")

        if shard_id in self._shards:
            return False

        self._shards.add(shard_id)

        for index in range(self.virtual_nodes):
            node_name = (
                f"node:{len(shard_id)}:{shard_id}:{index}"
            )
            position = self._hash(node_name)

            self._ring.append((position, shard_id))

        self._ring.sort()
        return True

    def get_shard(self, table: str, key: str) -> str:
        if not self._ring:
            raise RuntimeError("No shards registered")

        record_id = (
            f"record:{len(table)}:{table}:"
            f"{len(key)}:{key}"
        )

        position = self._hash(record_id)

        index = bisect_left(
            self._ring,
            (position, ""),
        )

        if index == len(self._ring):
            index = 0

        return self._ring[index][1]

    @property
    def position_count(self) -> int:
        return len(self._ring)

    def clear(self) -> None:
        self._ring.clear()
        self._shards.clear()
