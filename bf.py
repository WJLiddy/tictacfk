#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python Brainfuck interpreter.

Jitted using http://morepypy.blogspot.fr/2011/04/tutorial-part-2-adding-jit.html
"""

import sys
import os

try:
    from rpython.rlib.jit import JitDriver, purefunction
except ImportError:

    class JitDriver(object):
        def __init__(self, **kw):
            pass

        def jit_merge_point(self, **kw):
            pass

        def can_enter_jit(self, **kw):
            pass

    def purefunction(f):
        return f


jitdriver = JitDriver(greens=['position', 'chars', 'jump_table'],
                      reds=['ptr'])


@purefunction
def get_jump(jump_table, pos):
    return jump_table[pos]


def create_jump_table(chars):
    jump_table = {}
    left_positions = []

    position = 0
    for char in chars:
        if char == '[':
            left_positions.append(position)

        elif char == ']':
            left = left_positions.pop()
            right = position
            jump_table[left] = right
            jump_table[right] = left
        position += 1

    return jump_table


class Array(object):
    def __init__(self):
        self._cells = [0] * 256  # preallocation
        self._index = 0

    def get(self):
        return self._cells[self._index]

    def set(self, n):
        self._cells[self._index] = n

    def increment(self):
        self._cells[self._index] += 1

    def decrement(self):
        if self._cells[self._index] > 0:
            self._cells[self._index] -= 1

    def right(self):
        self._index += 1
        if self._index >= len(self._cells):
            self._cells.append(0)

    def left(self):
        if self._index > 0:
            self._index -= 1


def run(chars, input, maxinstr):

    result = []
    iptr = 0
    instrcnt = 0

    """Actual BrainFuck Interpreter."""
    jump_table = create_jump_table(chars)
    ptr = Array()

    position = 0
    while position < len(chars):
        instrcnt += 1
        if(instrcnt > maxinstr):
            return [[-1], instrcnt]
        jitdriver.jit_merge_point(position=position,
                                  ptr=ptr,
                                  chars=chars,
                                  jump_table=jump_table)

        char = chars[position]

        if char == '>':
            ptr.right()

        elif char == '<':
            ptr.left()

        elif char == '+':
            ptr.increment()

        elif char == '-':
            ptr.decrement()

        elif char == '.':
            result.append(ptr.get() % 256)

        elif char == ',':
            if(iptr == len(input)):
                ptr.set(0)
            else:
                ptr.set(input[iptr])
                iptr+=1

        elif char == '[' and ptr.get() % 256 == 0:
            position = get_jump(jump_table, position)

        elif char == ']' and ptr.get() % 256 != 0:
            position = get_jump(jump_table, position)

        position += 1
    return [result, instrcnt]


def remove_comments(chars):
    codes = '<>[]-+,.'
    tmp = ""
    for c in chars:
        if c in codes:
            tmp += c
    return tmp




def target(*args):
    return entry_point, None


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


