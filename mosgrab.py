#!/local/python-2.7.1/bin/python  
import sys
import re
import numpy as np

def is_ev_line(line):
    return 'eigenvalue' in line and 'nsaos' in line

def parse_ev_line(line):
    i = int(line[:6])
    index_ev = line.index('eigenvalue=') + 11
    index_n = line.index('nsaos=') + 6
    ev = float(re.sub('[dD]', 'E', line[index_ev:index_ev+20]))
    n = int(line[index_n:index_n+4])
    return (i, ev, n)

def format_ev_line(i, ev, n):
    s = "{0:6d}  a      eigenvalue={1:20.13E}   nsaos={2:<4d}\n"
    return s.format(i, ev, n)

def is_coefficients_line(line):
    try:
        float(re.sub('[dD]', 'E', line[:20]))
        return True
    except:
        return False

def format_coefficients_line(c):
    if c.size == 4:
        s = "{0:20.13E}{1:20.13E}{2:20.13E}{3:20.13E}\n"
        return re.sub('E', 'D', s.format(c[0], c[1], c[2], c[3]))
    elif c.size == 3:
        s = "{0:20.13E}{1:20.13E}{2:20.13E}\n"
        return re.sub('E', 'D', s.format(c[0], c[1], c[2]))
    elif c.size == 2:
        s = "{0:20.13E}{1:20.13E}\n"
        return re.sub('E', 'D', s.format(c[0], c[1]))
    elif c.size == 1:
        s = "{0:20.13E}\n"
        return re.sub('E', 'D', s.format(c[0]))

def read_coefficients_vector(ls, n):
    s = ''.join([ll[:-1] for ll in ls])
    C_col = np.zeros(n)
    for i in range(n):
        ss = s[i*20:(i+1)*20]
        C_col[i] = float(re.sub('[dD]', 'E', ss))
    return C_col

def read_mos_file(file):
    line = file.next()
    while line.startswith('$') or line.startswith('#'):
        line = file.next()
    if not is_ev_line(line):
        s = "Cannot interpret line as ev line\n"
        raise ValueError(''.join([s, line]))
    (i, ev, n) = parse_ev_line(line)
    C = np.zeros((n, n))
    E = np.zeros(n)
    E[0] = ev
    line = file.next()
    ls = []
    for j in range((n + 3) / 4):
        ls.append(line)
        line = file.next()
    C[:,0] = read_coefficients_vector(ls, n)
    for j in range(1, n):
        (i, ev, n) = parse_ev_line(line)
        E[j] = ev
        line = file.next()
        ls = []
        for jj in range((n + 3 ) / 4):
            ls.append(line)
            line = file.next()
        C[:,j] = read_coefficients_vector(ls, n)
    if not line.startswith("$end"):
        raise ValueError(''.join(["expected '$end', got: ", line]))
    return C, E

def write_mos_file(file, C, E):
    pre = \
'''$scfmo    scfconv=6   format(4d20.14)
# SCF total energy is      -00.0000000000 a.u.
#
'''
    post = "$end\n"
    if not (C.shape[0] == C.shape[1] == E.shape[0]):
        raise ValueError('C needs to be NxN, E Nx1')
    N = C.shape[0]
    file.write(pre)
    for i in range(N):
        file.write(format_ev_line(i+1, E[i], N))
        for ii in range(0, N, 4):
            file.write(format_coefficients_line(C[ii:ii+4,i]))
    file.write(post)

def main(infile, outfile):
    C, E = read_mos_file(infile)
    write_mos_file(outfile, C, E)

if __name__ == '__main__':
    main(sys.stdin, sys.stdout)
