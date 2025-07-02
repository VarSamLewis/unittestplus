    
import core
import manipulate

if __name__ == "__main__":

    # Example test functions for demonstration
    def sum2int(int1: int, int2: int) -> int:
        if int1 is None or int2 is None:
            raise ValueError("Both inputs must be provided")
        return int1 + int2
    core.bettertest(sum2int, inputs=[35, 20], output=55, display=False)
    #print(core._gen_test_identity(sum2int))

    """

    try:
        
    except Exception as e:
        print("Call failed")
    """
