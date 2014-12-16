__author__ = 'siy'

import numpy as np
import scipy.stats as stat
## dimensions are called axes, the number of axes is rank


# array creation
a = np.array([1,2,3])
print(a)
print(a.dtype)
a = np.zeros( (3,4) )
print(a)
a = np.ones( [2,3,4], dtype=complex)
print(a)
a = np.empty( (2,3))
print(a)


# range creation
b = np.arange(10)
print(b)
b = np.arange(0.0, 10.0, 0.5)
print(b)
b = np.linspace(0, 2, 9)
print(b)


# basic operations
a = np.array( [20, 30, 40, 50])
print(a)
b = np.arange(4)
print(b)
c = a - b
print(c)
c = b**2
print(c)
c = a < 35
print(c)

a = np.array( [[1,1],
               [0,1]])
b = np.array( [[2,0],
               [3,4]])
c = a * b
print(c)
c = np.dot(a,b)
print(c)

a = np.random.random((2,3))
print(a)
print(a.sum())
print(a.min())
print(a.max())

a = np.arange(12).reshape(3,4)
print(a)
print(a.sum(axis=0))    # sum of each column
print(a.sum(axis=1))    # sum of each row
print(a.cumsum(axis=1)) # cumulative sum along each row


# Indexing, Slicing and Iterating
a = np.arange(10)**3
print(a)
print(a[2])
print(a[2:5])
a[:6:2] = -1000     # a[0:6:2] = -1000; from start to index 6, exclusive, set every 2nd element to -1000
print(a)
a = a[::-1]             # reverse a
print(a)
for i in a: print(i**(1/3.))

def f(x,y): return 10*x+y
b = np.fromfunction(f, (5,4), dtype=int)
print(b)
print(b[2,3])
print(b[0:5,1])     # second item in each index
print(b[:,1])       # same as above
print(b[1:3,:])     # second to third row
print(b[-1])        # the last row, = b[-1,:]

for row in b: print(row)
for item in b.flat: print(item)

# Anonymous function
make_inc = lambda num: lambda arg: num + arg
inc = make_inc(1)
print(inc(1))


# percentile
print(np.percentile(np.arange(0,1000, 10), [20,50]))

# mean
print()
print("mean")
a = np.array([[1, np.nan, 2], [3, 4, 5]])
print(a)
print(np.nanmean(a))    # nan mean
print(np.mean(a))
print(np.nanmean(a, axis=0))
print(np.nanmean(a, axis=1))


print("a">"b")

print(stat.norm.stats([1, 2, 3, 4]))

np.random.normal(0, 0.1, 1000)