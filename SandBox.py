

word = "hello"

alphabet = 'abcdefghijklmnopqrstuvwxyz'

splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
print("splits ", splits)

deletes = [a + b[1:] for a, b in splits if b]
print("deletes ", deletes)

transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
print("tranpose ", transposes)

replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
print("replaces ", replaces)

inserts    = [a + c + b     for a, b in splits for c in alphabet]
print("inserts ", inserts)


def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

print(edits1(word))
print(len(edits1(word)))

def edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1))

print([(x, y) for x in [1,2,3] for y in [2,1,4] if x!=y])

print([x**2 for x in range(5)])

print(99 & 1)