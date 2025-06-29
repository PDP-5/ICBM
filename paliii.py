#!/usr/bin/env python3

import re
import sys

#undefined = None
#image = []

symtab = {
    "AND": 0o0000,
    "TAD": 0o1000,
    "ISZ": 0o2000,
    "DCA": 0o3000,
    "JMS": 0o4000,
    "JMP": 0o5000,
    "IOT": 0o6000,
    "OPR": 0o7000,
    "I":   0o0400,
    "CLA": 0o7200,
    "CLL": 0o7100,
    "CMA": 0o7040,
    "CML": 0o7020,
    "RAR": 0o7010,
    "RAL": 0o7004,
    "RTR": 0o7012,
    "RTL": 0o7006,
    "IAC": 0o7001,
    "CIA": 0o7041,
    "KCF": 0o6030,
    "KSF": 0o6031,
    "KCC": 0o6032,
    "KRS": 0o6034,
    "KIE": 0o6035,
    "KRB": 0o6036,
    "TSF": 0o6041,
    "TLS": 0o6046,
    "DXL": 0o6053,
    "DYS": 0o6067,
    "SMA": 0o7500,
    "SZA": 0o7440,
    "SPA": 0o7510,
    "SNA": 0o7450,
    "SNL": 0o7420,
    "SZL": 0o7430,
    "SKP": 0o7410,
    "OSR": 0o7404
}

def dot():
    global labels
    return labels["."]

def zero(symbol):
    return 0

def error(symbol):
    raise Exception(f"Undefined symbol: {symbol}")

def core(value):
    global image, labels
    if value is None:
        raise Exception(f"No value for {dot():04o}")
    if image:
        print(f"Store {value:04o} at {dot():04o}")
        image[dot()] = value & 0o7777
    labels["."] = dot() + 1
    return None

def foo(value):
    return value

def page(value):
    if value & 0o7600:
        value = (value & 0o177) | 0o200
    return value

def parse(line, store=foo):
    global undefined, pagify
    line = re.sub(r'/.*$', '', line)

    m = re.compile(r'^([^;]*);(.*)').match(line)
    if m:
        parse(m.group(1), store)
        parse(m.group(2), store)
        return None

    line = line.strip()
    if line == "":
        return None

    m = re.compile(r'TITLE(.*)').match(line)
    if m:
        title = m.group(1)
        print(f"title {title}")
        return None
    m = re.compile(r'^\*([0-7]+)').match(line)
    if m:
        labels["."] = int(m.group(1), 8)
        print(f"address {dot():04o}")
        return None
    m = re.compile(r'^([A-Z0-9]+),(.*)').match(line)
    if m:
        label = m.group(1)
        print(f"label {label} = {dot():04o}")
        labels[label] = dot()
        parse(m.group(2), core)
        return None
    m = re.compile(r'^([A-Z0-9]+)=(.*)').match(line)
    if m:
        symbol = m.group(1)
        print(f"symbol {symbol} = {m.group(2)}")
        value = parse(m.group(2))
        symtab[symbol] = value
        return None
    m = re.compile(r'^([^ ]+)[ \t]+(.*)').match(line)
    if m:
        value = parse(m.group(1))
        print(f"composition {m.group(1)}={value:04o} with {m.group(2)}")
        pagify = True
        return store(value | parse(m.group(2)))

    m = re.compile(r'^-(.*)').match(line)
    if m:
        print(f"negate {m.group(1)}")
        value = -parse(m.group(1))
        print(f"negate {value}")
        return store(value)
    m = re.compile(r'^([^+]*)\+(.*)').match(line)
    if m:
        print(f"addition {m.group(1)} {m.group(2)}")
        value = parse(m.group(1)) + parse(m.group(2))
        return store(value)
    m = re.compile(r'^([^+]*)-(.*)').match(line)
    if m:
        print(f"subtraction {m.group(1)} {m.group(2)}")
        value = parse(m.group(1)) - parse(m.group(2))
        return store(value)
    m = re.compile(r'^([0-7]+)').match(line)
    if m:
        number = int(m.group(1), 8)
        print(f"number {number}")
        return store(number)
    m = re.compile(r'^([A-Z0-9.]+)').match(line)
    if m:
        symbol = m.group(1)
        if symbol in symtab:
            value = symtab[symbol]
            print(f"symbol {symbol} is {value:04o}")
            return store(value)
        elif symbol in labels:
            value = labels[symbol]
            print(f"label {symbol} is {value:04o}")
            if pagify:
                value = page(value)
                print(f"pagified {value:04o}")
            return store(value)
        else:
            return undefined(symbol)
    raise Exception(f"Syntax error: {line}")

if __name__ == "__main__":
    global undefined, image, labels, pagify
    print("PASS 1")
    labels = {}
    labels["."] = 0
    undefined = zero
    image = None
    labels = {}
    with open(sys.argv[1]) as f:
        for line in f:
            pagify = False
            parse(line, core)
    print("PASS 2")
    labels["."] = 0
    undefined = error
    image = [None] * 4096
    with open(sys.argv[1]) as f:
        for line in f:
            pagify = False
            parse(line, core)
    for i in range(4096):
        if image[i] is not None:
            print(f"{i:04o} {image[i]:04o}")
