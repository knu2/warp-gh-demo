def divide(a, b):
    """Divide two numbers with zero division handling.
    
    Args:
        a: The numerator
        b: The denominator
    
    Returns:
        The result of a / b, or None if b is zero
    """
    if b == 0:
        print("Error: Cannot divide by zero")
        return None
    return a / b


def main():
    print("Hello, Warp!")
    
    # Test division function
    result1 = divide(10, 2)
    print(f"divide(10, 2) = {result1}")
    
    result2 = divide(10, 0)
    print(f"divide(10, 0) = {result2}")
    
    result3 = divide(15, 3)
    print(f"divide(15, 3) = {result3}")

if __name__ == "__main__":
    main()
