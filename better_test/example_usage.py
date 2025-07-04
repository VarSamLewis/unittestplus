    
from encodings import mac_turkish
import core
import manipulate

if __name__ == "__main__":

    # Example test functions for demonstration

    def sum2int(int1: int, int2: int) -> int:
        if int1 is None or int2 is None:
            raise ValueError("Both inputs must be provided")
        return int1 + int2

    try:
        #core.bettertest(sum2int, inputs=[5,5], expected_output=10, alias="Test_message")
        #test_id = manipulate.get_testid(sum2int, "Test_message")
        #manipulate.update_message(sum2int, "Updated message", test_id)
        test = manipulate.get_test(sum2int, 1, display = False)
        test
    except Exception as e:
        print(f"Call failed: {e}")
