    
import core
import manipulate
import pandas as pd
import random

if __name__ == "__main__":

    # Example test functions for demonstration

    def sum2int(int1: int, int2: int) -> int:
        if int1 is None or int2 is None:
            raise ValueError("Both inputs must be provided")
        return int1 + int2

    def multiply_and_add(x: int, y: int, add: int = 0) -> int:
        """
        Multiplies x and y, then adds the 'add' value.
        """
        return x * y + add

    def profile_GPU_usage(func, args, kwargs):
    # Custom profiling logic here
        return random.random()  # Example random value

    custom_metrics = {
    "sum_of_args": "sum(args)",  # Using eval to sum the positional arguments
    "output_plus_10": lambda func, args, kwargs: func(*args, **kwargs) + 10,  # Callable
    "GPU_usage": lambda func, args, kwargs: profile_GPU_usage(func, args, kwargs)
    }

    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [4, 5, 6],
        "C": [7, 8, 9]
    })

    def get_df_shape(df):
        return df

    try:
        core.bettertest(get_df_shape, inputs=df,expected_output=df ,alias="Check DF")
        #test_id = manipulate.get_testid(sum2int, "Test_message")
        #manipulate.update_message(sum2int, "Updated message", test_id)
        #test = manipulate.get_test(sum2int, 1, display = True)
        """
        test_result = core.bettertest(
            func=multiply_and_add,
            inputs=[3, 4],
            kwargs={"add": 2},
            expected_output=14,
            custom_metrics=custom_metrics,
            alias="basic multiplication test",
            message="Ensure multiply_and_add behaves correctly"
        )
        """
        #manipulate.clear_tests(multiply_and_add)
    except Exception as e:
        print(f"Call failed: {e}")
