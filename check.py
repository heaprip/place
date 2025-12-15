def xy_bijection(a: int, b: int) -> int:
    a = 2 * a if a >= 0 else -2 * a - 1
    b = 2 * b if b >= 0 else -2 * b - 1
    s = a + b
    return (s * (s + 1)) // 2 + b


cache = set()
# for x in range(0, 1000):
#     for y in range(0, 1000):
cache.add(xy_bijection(1 // 100, 1 // 100))

print(cache)
