#!/usr/bin/env python
# coding=utf-8
import math

import xxhash
from mpi4py import MPI
import random
import argparse

CHAR_BITS = 16
GLOBAL_TAG = 1337


def generate_chain(chains, steps, n):
    results = ''
    plaintext = ''

    for c in chains:
        for _ in xrange(steps - 1):
            plaintext = xxhash.xxh64(c).hexdigest()[:n]
        hex_hash = xxhash.xxh64(plaintext).hexdigest()
        results += plaintext + ":" + hex_hash + "\n"
    return results


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    piece = None

    parser = argparse.ArgumentParser(description='A simple rainbow table generator supporting xxHash')
    parser.add_argument('-steps', action="store", help='Number of steps in chain', dest='steps', type=int, default=None)
    parser.add_argument('-length', action="store", help='Password length', dest='length', type=int, default=4)

    length = parser.parse_args().length
    steps = [parser.parse_args().steps, 2 ** (2 * length)][parser.parse_args().steps is None]

    if rank == 0:
        parser.add_argument('-chains', action="store", help='Number of chains', dest='chains', type=int, default=None)
        chains = [parser.parse_args().chains, (16 ** length) / (steps * size)][parser.parse_args().chains is None]

        ceil_no = chains % size
        floor_no = size - ceil_no
        ceil = int(math.ceil(float(chains) / float(size)))
        floor = int(math.floor(float(chains) / float(size)))

        plain_array = list(set(map(lambda _: ('0' * 3 + hex(random.randint(0, CHAR_BITS ** length - 1))[2:])[-length:],
                                   xrange(2 * chains))))[:chains]

        index = 0
        for i in xrange(size):
            add = [floor, ceil][i < ceil_no]
            data = plain_array[index:index + add]
            if index != 0:
                comm.send(data, dest=i, tag=GLOBAL_TAG)
            else:
                piece = data
            index += add
    else:
        piece = comm.recv(source=0, tag=GLOBAL_TAG)

    if rank == 0:
        result = generate_chain(piece, steps, length)

        for i in xrange(1, size):
            result += comm.recv(source=i, tag=GLOBAL_TAG)

        parser.add_argument('-file', action="store", help='Output filename', dest='file', default='rt.txt')
        rainbow_file = open(parser.parse_args().file, "w")
        rainbow_file.write(result)

    else:
        comm.send(generate_chain(piece, steps, length), dest=0, tag=GLOBAL_TAG)


if __name__ == "__main__":
    main()
