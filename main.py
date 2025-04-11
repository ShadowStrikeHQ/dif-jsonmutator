import argparse
import json
import logging
import random
import sys
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class JSONMutator:
    """
    A class for mutating JSON payloads based on a schema.
    """

    def __init__(self, schema: Dict[str, Any], sample: Dict[str, Any]):
        """
        Initializes the JSONMutator with a schema and a sample JSON payload.

        Args:
            schema: A dictionary representing the JSON schema.
            sample: A dictionary representing a sample JSON payload.
        """
        self.schema = schema
        self.sample = sample

    def mutate(self, iterations: int = 1) -> List[Dict[str, Any]]:
        """
        Generates a list of mutated JSON payloads based on the schema and sample.

        Args:
            iterations: The number of mutated payloads to generate.

        Returns:
            A list of dictionaries, where each dictionary is a mutated JSON payload.
        """
        mutated_payloads = []
        for _ in range(iterations):
            mutated_payloads.append(self._mutate_recursive(self.schema, self.sample))
        return mutated_payloads

    def _mutate_recursive(self, schema: Dict[str, Any], data: Any) -> Any:
        """
        Recursively mutates the JSON data based on the schema.

        Args:
            schema: The schema for the current level of the data.
            data: The data to mutate.

        Returns:
            The mutated data.
        """
        if isinstance(schema, dict):
            if "type" in schema:
                data_type = schema["type"]
                if data_type == "string":
                    return self._mutate_string(data)
                elif data_type == "integer":
                    return self._mutate_integer(data)
                elif data_type == "number":
                    return self._mutate_number(data)
                elif data_type == "boolean":
                    return self._mutate_boolean()
                elif data_type == "null":
                    return None
                elif data_type == "array":
                    if "items" in schema:
                        if isinstance(data, list):
                            mutated_array = []
                            for item in data:
                                mutated_array.append(self._mutate_recursive(schema["items"], item))
                            return mutated_array
                        else:
                            # Data is not a list when it should be. Return an empty list
                            return []
                    else:
                         return [] #No item schema defined, can't mutate
                elif data_type == "object":
                     if isinstance(data, dict):
                        mutated_object = {}
                        if "properties" in schema:
                            for key, value in data.items():
                                if key in schema["properties"]:
                                    mutated_object[key] = self._mutate_recursive(schema["properties"][key], value)
                                else:
                                    #Keep values as they are for properties not in schema. Could also remove them, depends on the use case.
                                    mutated_object[key] = value
                            return mutated_object
                     else:
                         # Data is not a dict when it should be.  Return an empty dict
                         return {}
                else:
                    logging.warning(f"Unsupported type: {data_type}")
                    return data  # Return the original data if the type is not supported
            else:
                # No type specified in schema. Attempt to process as an object
                 if isinstance(data, dict):
                        mutated_object = {}
                        for key, value in data.items():
                            mutated_object[key] = self._mutate_recursive({}, value) #Empty schema, but still recurse
                        return mutated_object
                 else:
                     return data # Not a dict and no schema type defined.  Return as is.

        elif isinstance(data, dict):
            # Schema might be empty ( {} ). Treat this as a pass through, applying mutation to all values.
            mutated_object = {}
            for key, value in data.items():
               mutated_object[key] = self._mutate_recursive({}, value)  # Recurse with an empty schema.
            return mutated_object
        else:
            # Not a dict or the type could not be found. No mutation, return the original
            return data

    def _mutate_string(self, data: str) -> str:
        """
        Mutates a string value.

        Args:
            data: The string value to mutate.

        Returns:
            The mutated string value.
        """
        mutation_strategies = [
            lambda s: s + "!" * random.randint(1, 5),  # Add exclamation marks
            lambda s: s.upper(),  # Convert to uppercase
            lambda s: s.lower(),  # Convert to lowercase
            lambda s: s[::-1],  # Reverse the string
            lambda s: s + "<script>alert('XSS')</script>",  # Inject XSS payload
            lambda s: s + "' OR '1'='1",  # Inject SQL injection payload
            lambda s: s + "\0", # Add null byte
            lambda s: ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(random.randint(5, 15))), #Random string
        ]
        strategy = random.choice(mutation_strategies)
        return strategy(data)

    def _mutate_integer(self, data: int) -> int:
        """
        Mutates an integer value.

        Args:
            data: The integer value to mutate.

        Returns:
            The mutated integer value.
        """
        mutation_strategies = [
            lambda i: i + random.randint(1, 10),  # Add a small random number
            lambda i: i - random.randint(1, 10),  # Subtract a small random number
            lambda i: i * random.randint(1, 3),  # Multiply by a small random number
            lambda i: i // random.randint(1, 3) if random.randint(1, 3) != 0 else i,  # Integer divide by small random number
            lambda i: 2**31 - 1,  # Integer overflow
            lambda i: -2**31,  # Integer underflow
            lambda i: 0  # Set to zero
        ]
        strategy = random.choice(mutation_strategies)
        try:
           return strategy(data)
        except OverflowError:
            return data #If the mutation causes an overflow error, just revert to the original value.

    def _mutate_number(self, data: float) -> float:
        """
        Mutates a number (float) value.

        Args:
            data: The number value to mutate.

        Returns:
            The mutated number value.
        """
        mutation_strategies = [
            lambda f: f + random.uniform(0.1, 1.0),  # Add a small random number
            lambda f: f - random.uniform(0.1, 1.0),  # Subtract a small random number
            lambda f: f * random.uniform(1.1, 2.0),  # Multiply by a small random number
            lambda f: f / random.uniform(1.1, 2.0) if random.uniform(1.1, 2.0) != 0 else f,  # Divide by a small random number
            lambda f: float('inf'),  # Set to infinity
            lambda f: float('-inf'),  # Set to negative infinity
            lambda f: float('nan')  # Set to NaN
        ]
        strategy = random.choice(mutation_strategies)
        try:
            return strategy(data)
        except ZeroDivisionError:
            return data #If the mutation causes a division by zero error, just revert to the original value.

    def _mutate_boolean(self) -> bool:
        """
        Mutates a boolean value.

        Returns:
            The mutated boolean value (always the opposite of the current value).
        """
        return not random.choice([True, False]) # Always return a random boolean, not based on the input.


def setup_argparse() -> argparse.ArgumentParser:
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        An argparse.ArgumentParser object.
    """
    parser = argparse.ArgumentParser(
        description="A command-line tool that takes a JSON schema and a JSON sample as input, "
                    "and generates a stream of mutated JSON payloads based on the schema."
    )
    parser.add_argument(
        "--schema",
        type=str,
        required=True,
        help="Path to the JSON schema file."
    )
    parser.add_argument(
        "--sample",
        type=str,
        required=True,
        help="Path to the JSON sample file."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of mutated payloads to generate (default: 1)."
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Path to the output file to write the mutated payloads. If not specified, outputs to stdout."
    )
    return parser


def main() -> None:
    """
    The main function of the dif-JSONMutator tool.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        with open(args.schema, "r") as f:
            schema = json.load(f)
    except FileNotFoundError:
        logging.error(f"Schema file not found: {args.schema}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in schema file: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading schema file: {e}")
        sys.exit(1)

    try:
        with open(args.sample, "r") as f:
            sample = json.load(f)
    except FileNotFoundError:
        logging.error(f"Sample file not found: {args.sample}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in sample file: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading sample file: {e}")
        sys.exit(1)

    try:
        mutator = JSONMutator(schema, sample)
        mutated_payloads = mutator.mutate(args.iterations)

        if args.output:
            try:
                with open(args.output, "w") as f:
                    json.dump(mutated_payloads, f, indent=4)
                logging.info(f"Mutated payloads written to: {args.output}")

            except Exception as e:
                 logging.error(f"Error writing to output file: {e}")
                 sys.exit(1)


        else:
            for payload in mutated_payloads:
                print(json.dumps(payload, indent=4))

    except Exception as e:
        logging.error(f"An error occurred during mutation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()