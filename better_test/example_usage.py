    
import core
import manipulate

if __name__ == "__main__":

    # Example test functions for demonstration
    def sum2int(int1: int, int2: int) -> int:
        if int1 is None or int2 is None:
            raise ValueError("Both inputs must be provided")
        return int1 + int2
    
    try:
        core.bettertest(sum2int, inputs=[35, 20], output=55)
        #manipulate.clear_tests(sum2int)
        #manipulate._assign_alias(sum2int, alias="Test assign alias", test_id=1)
        #code = manipulate.get_previous_test_definition(sum2int, test_id=1)
    except Exception as e:
        print(f"Call failed: {e}")
