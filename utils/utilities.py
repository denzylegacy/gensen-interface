import random
import time


class UniqueIdGenerator:
    @staticmethod
    def generate_unique_custom_id():
        timestamp = time.time()
        rand_num = random.randint(0, 100000)

        # Convert both values ​​to hexadecimal and then combine them
        custom_id = hex(int(timestamp))[2:] + hex(rand_num)[2:]

        return custom_id[:100]
