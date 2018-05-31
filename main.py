import xxhash
import threading
import random
import time


def random_plaintext(n):
    max_range = 16 ** n - 1
    return ('0' * 3 + hex(random.randint(0, max_range))[2:])[-4:]


def generate_chain(rainbow_file, file_lock, steps, chains):
    for _ in xrange(chains):
        plaintext = random_plaintext(4)
        for _ in xrange(steps - 1):
            plaintext = xxhash.xxh64(plaintext).hexdigest()[:4]
        hex_hash = xxhash.xxh64(plaintext).hexdigest()

        file_lock.acquire()
        rainbow_file.write(plaintext + ":" + hex_hash + "\n")
        file_lock.release()


def main():
    n_threads = 16
    file_lock = threading.Lock()
    steps = 256
    chains = 32
    rainbow_file = open("rt.txt", "a")
    start = time.time()

    threads = []
    for thread_id in xrange(n_threads):
        threads.append(threading.Thread(target=generate_chain, args=(rainbow_file, file_lock, steps, chains)))
        threads[thread_id].start()

    stop = time.time()
    print stop - start


if __name__ == "__main__":
    main()
