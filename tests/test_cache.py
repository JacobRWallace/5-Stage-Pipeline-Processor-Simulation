"""Extension 2: cache hierarchy. Unlocks when pipeline_sim/cache.py exists.

Convention: Cache(size, block, assoc, miss_penalty) in bytes. access() returns
EXTRA cycles beyond the normal MEM stage: hit = 0, miss = miss_penalty.
LRU replacement, write-allocate. Sizes must be powers of two.
"""
import pytest

cache = pytest.importorskip("pipeline_sim.cache", reason="extension 2 not started")
Cache = cache.Cache


def test_compulsory_miss_then_hits():
    c = Cache(size=64, block=16, assoc=1, miss_penalty=10)
    assert c.access(0) == 10
    assert c.access(0) == 0
    assert c.access(12) == 0, "same 16-byte block"
    assert (c.hits, c.misses) == (2, 1)
    assert c.hit_rate == pytest.approx(2 / 3)


def test_direct_mapped_conflict():
    c = Cache(size=64, block=16, assoc=1, miss_penalty=10)   # 4 sets: 0 and 64 collide
    for _ in range(3):
        c.access(0)
        c.access(64)
    assert (c.hits, c.misses) == (0, 6)


def test_two_way_removes_that_conflict():
    c = Cache(size=64, block=16, assoc=2, miss_penalty=10)
    for _ in range(3):
        c.access(0)
        c.access(64)
    assert (c.hits, c.misses) == (4, 2)


def test_lru_eviction():
    c = Cache(size=64, block=16, assoc=2, miss_penalty=10)   # 2 sets: 0, 32, 64 all in set 0
    pattern = [0, 32, 0, 64, 0, 32]
    got = ["H" if c.access(a) == 0 else "M" for a in pattern]
    assert got == ["M", "M", "H", "M", "H", "M"], "64 should evict 32 (LRU), not 0"


def test_write_allocate():
    c = Cache(size=64, block=16, assoc=1, miss_penalty=10)
    assert c.access(0, is_write=True) == 10
    assert c.access(4) == 0


def test_rejects_bad_geometry():
    with pytest.raises(ValueError):
        Cache(size=60, block=16, assoc=1, miss_penalty=10)


def test_dcache_miss_stalls_pipeline(sim):
    pytest.importorskip("pipeline_sim.functional", reason="needs extension 5 for addresses")
    src = "LW R1, 0(R0)\nLW R2, 4(R0)"   # same block: one miss, one hit
    dcache = Cache(size=64, block=16, assoc=1, miss_penalty=10)
    cold = sim(src, dcache=dcache)
    perfect = sim(src)
    assert cold.cycles - perfect.cycles == 10
    assert (dcache.hits, dcache.misses) == (1, 1)
