def fibonacci(n):
    """
    Generate the first n fibonacci numbers.
    
    Args:
        n: Number of fibonacci numbers to generate
    
    Returns:
        List of fibonacci numbers
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[i-1] + fib_sequence[i-2])
    
    return fib_sequence


def main():
    print("Hello, Warp!")
    print("\nFibonacci Sequence - First 20 Numbers:")
    print("=" * 40)
    
    fib_numbers = fibonacci(20)
    for i, num in enumerate(fib_numbers, 1):
        print(f"F({i:2d}) = {num:,}")
    
    print("\n" + "=" * 40)
    print(f"Sum of first 20 Fibonacci numbers: {sum(fib_numbers):,}")


if __name__ == "__main__":
    main()
