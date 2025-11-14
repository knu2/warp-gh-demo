def main():
    print("Hello, Warp!")
    x = int("42")  # Fine
    y = int("abc")  # ValueError!
    print(f"Result: {x + y}")

if __name__ == "__main__":
    main()
