"""
User-level application (stub).
"""

import argparse
from store import Storage


def main(arguments):
    storage = allocate_application(arguments)

    # Adding a key-value pair to the storage.
    key = "info8002"
    value = "fun"
    callback = storage.put(key, value, block=False)

    # Depending on how fast your blockchain is,
    # this will return a proper result.
    print(storage.retrieve(key))

    # Using the callback object,
    # you can also wait for the operation to be completed.
    callback.wait()

    # Now the key should be available,
    # unless a different node `put` a new value.
    print(storage.retrieve(key))

    # Show all values of the key.
    print(storage.retrieve_all(key))


def allocate_application(arguments):
    application = Storage(
        bootstrap=arguments.bootstrap,
        miner=arguments.miner,
        )

    return application


def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--miner", type=bool, default=False, nargs='?',
                        const=True, help="Starts the mining procedure.")
    parser.add_argument("--bootstrap", type=str, default=None,
                        help="Sets the address of the bootstrap node.")
    arguments, _ = parser.parse_known_args()

    return arguments


if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
