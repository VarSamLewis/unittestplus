    
import core
import manipulate

if __name__ == "__main__":
    def sum2int(int1: int, int2: int) -> int:
        if int1 is None or int2 is None:
            raise ValueError("Both inputs must be provided")
        return int1 + int2

    try:
        core.bettertest(sum2int, inputs=[35, 20], output=55)
    except Exception as e:
        print("Call failed")
