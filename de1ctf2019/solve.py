#!/usr/bin/env python2

"""
In this challenge we are given a binary that checks an input given from stdin.
If it is correct, it will call get_flag in a separate library and print(it.)
However, we don't have the library so need to find the correct input and input
it over netcat. If it is incorrect, only 'Goodbye' is printed.

Reversing shows that the program verifies the input character by character.]
Because of the program's linear nature and reliance on verbose constraints,
angr is perfect for solving this challenge quickly. On a virtual machine
with one core and 4 GB of RAM, it took ~26 seconds to solve.

Author: scienceman (@docileninja)
Team: PPP (CMU)
"""

import angr
import claripy
import subprocess
import logging
#logging.getLogger('angr').setLevel('INFO')
START = 0x400536 # start of main
FIND = 0x400AB5 # part of program that prints the flag
#AVOID = [0x4005F8, 0x400A4A] # all addresses after a failed check occur on a fixed interval
AVOID=[]
BUF_LEN = 70

def char(state, c):
    '''returns constraints s.t. c is printable'''
    return state.solver.And(c <= '~', c >= ' ')

def main():
    p = angr.Project('test')

    print('creating state')
    flag = claripy.BVS('flag', BUF_LEN*8)
    state = p.factory.blank_state(addr=START, stdin=flag)

    print('adding constaints to stdin')
    for c in flag.chop(8):
        state.solver.add(char(state, c))

    print('creating state and simgr')
    ex = p.factory.simulation_manager(state)
    ex.use_technique(angr.exploration_techniques.Explorer(find=FIND, avoid=AVOID))

    print('running explorer')
    ex.run()

    print('found solution')
    correct_input = ex.one_found.posix.dumps(0) # ex._f is equiv. to ex.found[0]
    print (correct_input)

    return correct_input

def test():
    team = main()
    p = subprocess.Popen(["./test"], env={"LD_LIBRARY_PATH": "."}, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate(input=team + b"\n")
    assert b"GOOD" in out

if __name__ == '__main__':
    team = main()
    print('found correct input: {}'.format(repr(team)))

