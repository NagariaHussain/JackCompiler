import typing

class DemoNTClass(typing.NamedTuple):

    a: int
    b: float = 1.1
    c = 'spam'

print('annotations:', DemoNTClass.__annotations__)


print('a:', DemoNTClass.a)
print('b:', DemoNTClass.b)
print('c:', DemoNTClass.c)

nt = DemoNTClass(10, 78)

print('nt.a:', nt.a)
print('nt.b:', nt.b)
print('nt.c:', nt.c)


from dataclasses import dataclass

@dataclass
class DemoDataClass:
    a: int
    b: float = 1.1
    c = 'spam'

print('annotations:', DemoDataClass.__annotations__)


print('a:', DemoDataClass.a)
# print('b:', DemoDataClass.b)
# print('c:', DemoDataClass.c)

