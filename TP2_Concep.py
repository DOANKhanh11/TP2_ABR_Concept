"""
L3 MIAGE - CAA - TP2: Binary Search Trees (ABR) and Binary Heaps (TB)

Implements the three exercises:
  - Exercise 2.1: Creation of complete vs filiform BSTs, timing comparison.
  - Exercise 2.2: Search after a delete-insert cycle on a complete BST.
  - Exercise 2.3: Max-heap construction and search timing, random arrays.

All tree operations are ITERATIVE to avoid Python recursion-limit issues
on filiform BSTs (depth ~ n).

Run:
    python tp2_abr_tb.py

This produces:
    - results.csv          (all measurements)
    - fig_ex21.png         (Exercise 2.1 graph)
    - fig_ex22.png         (Exercise 2.2 graph)
    - fig_ex23_create.png  (Exercise 2.3 creation graph)
    - fig_ex23_search.png  (Exercise 2.3 search graph)
"""

import csv
import random
import time
from typing import List, Optional, Tuple

import matplotlib

matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Binary Search Tree (BST / ABR)
# ---------------------------------------------------------------------------


class BSTNode:
    __slots__ = ("key", "left", "right", "parent")

    def __init__(self, key: int):
        self.key = key
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None
        self.parent: Optional["BSTNode"] = None


class BST:
    """Iterative BST supporting insert, search, delete (CLRS-style)."""

    def __init__(self):
        self.root: Optional[BSTNode] = None

    # -- Insertion ----------------------------------------------------------
    def insert(self, key: int) -> None:
        z = BSTNode(key)
        y: Optional[BSTNode] = None
        x = self.root
        while x is not None:
            y = x
            if z.key < x.key:
                x = x.left
            else:
                x = x.right
        z.parent = y
        if y is None:
            self.root = z
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z

    # -- Search -------------------------------------------------------------
    def search(self, key: int) -> Optional[BSTNode]:
        x = self.root
        while x is not None and x.key != key:
            if key < x.key:
                x = x.left
            else:
                x = x.right
        return x

    # -- Delete -------------------------------------------------------------
    def _transplant(self, u: BSTNode, v: Optional[BSTNode]) -> None:
        if u.parent is None:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        if v is not None:
            v.parent = u.parent

    def _minimum(self, x: BSTNode) -> BSTNode:
        while x.left is not None:
            x = x.left
        return x

    def delete_key(self, key: int) -> bool:
        z = self.search(key)
        if z is None:
            return False
        if z.left is None:
            self._transplant(z, z.right)
        elif z.right is None:
            self._transplant(z, z.left)
        else:
            y = self._minimum(z.right)
            if y.parent is not z:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
        return True

    # -- Traversals ---------------------------------------------------------
    def postorder(self) -> List[int]:
        """Iterative postfix (suffixe) traversal."""
        if self.root is None:
            return []
        out: List[int] = []
        stack: List[Tuple[BSTNode, bool]] = [(self.root, False)]
        while stack:
            node, visited = stack.pop()
            if visited:
                out.append(node.key)
            else:
                stack.append((node, True))
                if node.right is not None:
                    stack.append((node.right, False))
                if node.left is not None:
                    stack.append((node.left, False))
        return out

    def depth(self) -> int:
        """Returns the depth (height) of the tree iteratively."""
        if self.root is None:
            return -1
        # BFS-style depth computation, iterative to avoid recursion limit
        stack = [(self.root, 0)]
        best = 0
        while stack:
            node, d = stack.pop()
            if d > best:
                best = d
            if node.left is not None:
                stack.append((node.left, d + 1))
            if node.right is not None:
                stack.append((node.right, d + 1))
        return best


# ---------------------------------------------------------------------------
# Helpers to build the "T" insertion-order arrays
# ---------------------------------------------------------------------------


def build_complete_order(p: int) -> List[int]:
    """
    Build the insertion-order array T described in Exercise 2.1, question 2.

    For p = 3 it returns:
        [8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15]
    """
    n = (1 << (p + 1)) - 1  # 2^(p+1) - 1
    T = [0] * n
    T[0] = 1 << p  # 2^p (1-indexed T[1] in the handout)
    k = 1          # next free 0-indexed slot
    for i in range(p - 1, -1, -1):
        T[k] = 1 << i
        k += 1
        # write (2^(p-i) - 1) further entries: each one is the previous + 2^(i+1)
        for _ in range(1, 1 << (p - i)):
            T[k] = T[k - 1] + (1 << (i + 1))
            k += 1
    return T


def build_filiform_order(p: int) -> List[int]:
    """
    Insertion order that produces a filiform (right-spine) BST: 1, 2, ..., n.
    """
    n = (1 << (p + 1)) - 1
    return list(range(1, n + 1))


def build_bst_from_order(order: List[int]) -> BST:
    tree = BST()
    for v in order:
        tree.insert(v)
    return tree


# ---------------------------------------------------------------------------
# Binary heap (max-heap, array-based)
# ---------------------------------------------------------------------------


def _max_heapify(A: List[int], i: int, heap_size: int) -> None:
    """CLRS MAX-HEAPIFY, iterative version (sift-down)."""
    while True:
        l = 2 * i + 1
        r = 2 * i + 2
        largest = i
        if l < heap_size and A[l] > A[largest]:
            largest = l
        if r < heap_size and A[r] > A[largest]:
            largest = r
        if largest == i:
            return
        A[i], A[largest] = A[largest], A[i]
        i = largest


def build_max_heap(A: List[int]) -> None:
    """CLRS BUILD-MAX-HEAP, in place. Theta(n) overall."""
    n = len(A)
    for i in range(n // 2 - 1, -1, -1):
        _max_heapify(A, i, n)


def heap_linear_search(A: List[int], key: int) -> int:
    """Worst-case search in a heap: linear scan. Returns index or -1."""
    for idx, v in enumerate(A):
        if v == key:
            return idx
    return -1


# ---------------------------------------------------------------------------
# Exercise 2.2: Manipuler-ABR-complet
# ---------------------------------------------------------------------------


def manipuler_abr_complet(tree: BST, p: int) -> BST:
    """
    For i from 2^p down to 1, delete i then re-insert i.
    Mutates `tree` in place (returned for convenience).
    """
    for i in range(1 << p, 0, -1):
        tree.delete_key(i)
        tree.insert(i)
    return tree


# ---------------------------------------------------------------------------
# Timing harness
# ---------------------------------------------------------------------------


THREE_MINUTES = 180.0  # seconds


def time_call(fn, *args, **kwargs) -> Tuple[float, "object"]:
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    return time.perf_counter() - t0, result


def run_exercise_21(max_p_hardcap: int = 25) -> List[dict]:
    """
    For each p starting at 1: time the BST-construction phase only.
    Stop after the iteration in which Creer-ABR-complet exceeded 3 minutes.
    """
    rows = []
    p = 1
    while p <= max_p_hardcap:
        n = (1 << (p + 1)) - 1

        order_c = build_complete_order(p)
        order_f = build_filiform_order(p)

        t_complete, _ = time_call(build_bst_from_order, order_c)
        t_filiform, _ = time_call(build_bst_from_order, order_f)

        rows.append({
            "exercise": "2.1",
            "p": p,
            "n": n,
            "t_create_complete": t_complete,
            "t_create_filiform": t_filiform,
        })
        print(f"[Ex 2.1] p={p:2d}  n={n:>10d}  "
              f"complete={t_complete:.4f}s   filiform={t_filiform:.4f}s")

        if t_complete > THREE_MINUTES:
            break
        p += 1
    return rows


def run_exercise_22(max_p: int) -> List[dict]:
    """
    For each p from 1 to max_p: build A (complete), build A' via
    Manipuler-ABR-complet, then time the search for key 1 in each.
    """
    rows = []
    for p in range(1, max_p + 1):
        n = (1 << (p + 1)) - 1
        order_c = build_complete_order(p)

        # Build A (complete)
        A_tree = build_bst_from_order(order_c)
        t_search_A, _ = time_call(A_tree.search, 1)

        # Build A' from a fresh copy of the complete BST
        Aprime_tree = build_bst_from_order(order_c)
        manipuler_abr_complet(Aprime_tree, p)
        t_search_Aprime, _ = time_call(Aprime_tree.search, 1)

        rows.append({
            "exercise": "2.2",
            "p": p,
            "n": n,
            "t_search_complete_A": t_search_A,
            "t_search_Aprime": t_search_Aprime,
            "depth_A": A_tree.depth(),
            "depth_Aprime": Aprime_tree.depth(),
        })
        print(f"[Ex 2.2] p={p:2d}  n={n:>10d}  "
              f"search(A)={t_search_A:.6f}s  depth(A)={A_tree.depth()}   "
              f"search(A')={t_search_Aprime:.6f}s  depth(A')={Aprime_tree.depth()}")
    return rows


def run_exercise_23(
    max_p: int,
    rng_seed: int = 42,
    per_p_time_budget: float = 8.0,
    sample_cap: int = 5_000,
) -> List[dict]:
    """
    For each p from 1 to max_p:
      - sample many random permutations of [1..n]
      - record the BEST (min) and WORST (max) time for build_max_heap
        over the sample
      - record the WORST (max) time for a linear search of key 1
        on those same heaps

    Stopping conditions per p (whichever comes first):
      * cumulative time of build_max_heap exceeds 3 minutes (per the handout)
      * wall-clock spent on this p exceeds `per_p_time_budget`
      * `sample_cap` samples reached

    The latter two avoid spending hours on tiny p where each call is sub-microsecond.
    """
    rng = random.Random(rng_seed)
    rows = []
    for p in range(1, max_p + 1):
        n = (1 << (p + 1)) - 1

        best_create = float("inf")
        worst_create = -float("inf")
        worst_search = -float("inf")
        cumulative = 0.0
        samples = 0
        wall_start = time.perf_counter()

        while cumulative < THREE_MINUTES:
            # Fresh random permutation of [1..n]
            arr = list(range(1, n + 1))
            rng.shuffle(arr)

            t_create, _ = time_call(build_max_heap, arr)
            t_search, _ = time_call(heap_linear_search, arr, 1)

            cumulative += t_create  # only the create time is counted per the handout
            samples += 1
            if t_create < best_create:
                best_create = t_create
            if t_create > worst_create:
                worst_create = t_create
            if t_search > worst_search:
                worst_search = t_search

            # Wall-clock budget per p (safety net for tiny n where t_create ~ 1 us).
            if (time.perf_counter() - wall_start) >= per_p_time_budget:
                break
            if samples >= sample_cap:
                break

        rows.append({
            "exercise": "2.3",
            "p": p,
            "n": n,
            "samples": samples,
            "t_create_best": best_create,
            "t_create_worst": worst_create,
            "t_search_worst": worst_search,
        })
        print(f"[Ex 2.3] p={p:2d}  n={n:>10d}  samples={samples:>7d}  "
              f"create_best={best_create:.6e}s  create_worst={worst_create:.6e}s  "
              f"search_worst={worst_search:.6e}s")
    return rows


# ---------------------------------------------------------------------------
# Graphs
# ---------------------------------------------------------------------------


def plot_ex21(rows: List[dict], outpath: str) -> None:
    ns = [r["n"] for r in rows]
    complete = [r["t_create_complete"] for r in rows]
    filiform = [r["t_create_filiform"] for r in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(ns, complete, marker="o", label="Creer-ABR-complet")
    plt.plot(ns, filiform, marker="s", label="Creer-ABR-filiforme")
    plt.xlabel("n (number of nodes)")
    plt.ylabel("Execution time (s)")
    plt.title("Exercise 2.1 - BST construction time vs n")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=140)
    plt.close()


def plot_ex22(rows: List[dict], outpath: str) -> None:
    ns = [r["n"] for r in rows]
    search_A = [r["t_search_complete_A"] for r in rows]
    search_Ap = [r["t_search_Aprime"] for r in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(ns, search_A, marker="o", label="search(1) in A (complete BST)")
    plt.plot(ns, search_Ap, marker="s", label="search(1) in A' (after delete-insert cycle)")
    plt.xlabel("n (number of nodes)")
    plt.ylabel("Execution time (s)")
    plt.title("Exercise 2.2 - Search time for key 1 vs n")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=140)
    plt.close()


def plot_ex23_create(rows: List[dict], outpath: str) -> None:
    ns = [r["n"] for r in rows]
    best = [r["t_create_best"] for r in rows]
    worst = [r["t_create_worst"] for r in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(ns, best, marker="o", label="Creer-TB (best observed)")
    plt.plot(ns, worst, marker="s", label="Creer-TB (worst observed)")
    plt.xlabel("n (number of values)")
    plt.ylabel("Execution time (s)")
    plt.title("Exercise 2.3 - Max-heap construction time vs n")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=140)
    plt.close()


def plot_ex23_search(rows: List[dict], outpath: str) -> None:
    ns = [r["n"] for r in rows]
    worst = [r["t_search_worst"] for r in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(ns, worst, marker="o", label="Worst-case search(1) in TB")
    plt.xlabel("n (number of values)")
    plt.ylabel("Execution time (s)")
    plt.title("Exercise 2.3 - Worst-case search time in max-heap vs n")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=140)
    plt.close()


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------


def write_csv(rows: List[dict], path: str) -> None:
    # Union of keys preserving a sensible order
    preferred = [
        "exercise", "p", "n",
        "t_create_complete", "t_create_filiform",
        "t_search_complete_A", "t_search_Aprime", "depth_A", "depth_Aprime",
        "samples", "t_create_best", "t_create_worst", "t_search_worst",
    ]
    keys = []
    seen = set()
    for k in preferred:
        for r in rows:
            if k in r and k not in seen:
                keys.append(k)
                seen.add(k)
                break
    # Add any leftover keys not in the preferred list
    for r in rows:
        for k in r:
            if k not in seen:
                keys.append(k)
                seen.add(k)

    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


# ---------------------------------------------------------------------------
# Bonus: theoretical answers as utilities
# ---------------------------------------------------------------------------


def parcours_suffixe_complete(p: int) -> List[int]:
    """Returns the postorder traversal of the complete BST built with p."""
    order = build_complete_order(p)
    tree = build_bst_from_order(order)
    return tree.postorder()


# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------


def _self_test() -> None:
    # Verify build_complete_order for p=3 matches the handout exactly.
    expected = [8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15]
    got = build_complete_order(3)
    assert got == expected, f"build_complete_order(3) = {got}, expected {expected}"

    # The complete BST for p=3 must have depth 3.
    t = build_bst_from_order(expected)
    assert t.depth() == 3, f"complete BST depth = {t.depth()}"

    # Postorder of complete BST for p=3 should be left-right-root recursively.
    # For p=3 root=8: post(left subtree of 4) then post(right subtree of 12) then 8
    # left subtree rooted at 4: post -> 1,3,2,5,7,6,4
    # right subtree rooted at 12: post -> 9,11,10,13,15,14,12
    # total -> 1,3,2,5,7,6,4,9,11,10,13,15,14,12,8
    expected_post = [1, 3, 2, 5, 7, 6, 4, 9, 11, 10, 13, 15, 14, 12, 8]
    assert t.postorder() == expected_post, f"postorder = {t.postorder()}"

    # Filiform: depth = n - 1.
    f = build_bst_from_order(build_filiform_order(4))
    n = (1 << 5) - 1
    assert f.depth() == n - 1, f"filiform depth = {f.depth()}, expected {n - 1}"

    # BST delete sanity: delete then reinsert preserves BST property and key set.
    keys = list(range(1, 16))
    t2 = build_bst_from_order(build_complete_order(3))
    for k in [4, 12, 8, 1, 15]:
        t2.delete_key(k)
        t2.insert(k)
    # In-order via stack should be sorted.
    def inorder_iter(tree):
        out, stack, x = [], [], tree.root
        while x is not None or stack:
            while x is not None:
                stack.append(x); x = x.left
            x = stack.pop()
            out.append(x.key)
            x = x.right
        return out
    assert inorder_iter(t2) == keys

    # Heapify sanity: after build_max_heap, parent >= children.
    arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9]
    build_max_heap(arr)
    for i in range(len(arr)):
        for c in (2 * i + 1, 2 * i + 2):
            if c < len(arr):
                assert arr[i] >= arr[c], f"heap property violated at {i}, {c}"

    print("[self-test] all checks passed.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    _self_test()

    print("\n=== Exercise 2.1 ===")
    rows21 = run_exercise_21()
    max_p = max(r["p"] for r in rows21)

    print(f"\n=== Exercise 2.2 (p in 1..{max_p}) ===")
    rows22 = run_exercise_22(max_p)

    print(f"\n=== Exercise 2.3 (p in 1..{max_p}) ===")
    rows23 = run_exercise_23(max_p)

    all_rows = rows21 + rows22 + rows23
    write_csv(all_rows, "results.csv")
    plot_ex21(rows21, "fig_ex21.png")
    plot_ex22(rows22, "fig_ex22.png")
    plot_ex23_create(rows23, "fig_ex23_create.png")
    plot_ex23_search(rows23, "fig_ex23_search.png")

    print("\n--- Bonus: parcours suffixe of complete BST for p=4 (n=31) ---")
    print(parcours_suffixe_complete(4))

    print("\nDone. Outputs: results.csv, fig_ex21.png, fig_ex22.png, "
          "fig_ex23_create.png, fig_ex23_search.png")


if __name__ == "__main__":
    main()