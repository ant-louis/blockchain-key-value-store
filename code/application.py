"""
User-level application (stub).
"""

import argparse

from store import Storage


def main(arguments):
    storage = allocate_application(arguments)

    # Adding a key-value pair to the storage.
    callback = storage.put("info8002", "fun", block=False)

    # Using the callback object,
    # you can also wait for the operation to be completed.
    callback.wait()

    # Depending on how fast your blockchain is,
    # this will return a proper result.
    print(storage.retrieve("info8002"))

    #However, our blokchain is always one block behind, so you'll have
    #to submit another transaction
    callback2 = storage.put("info8002", "interesting", block=False)
    callback2.wait()

    # Now the key should be available,
    print(storage.retrieve("info8002"))

    callback3 = storage.put("Party", "fun", block=False)
    callback3.wait()

    # Show all values of the key.
    print(storage.retrieve_all("info8002"))


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
