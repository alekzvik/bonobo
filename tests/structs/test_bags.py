import pickle
from unittest.mock import Mock

from bonobo import Bag
from bonobo.constants import INHERIT_INPUT
from bonobo.structs import Token

args = ('foo', 'bar', )
kwargs = dict(acme='corp')


def test_basic():
    my_callable1 = Mock()
    my_callable2 = Mock()
    bag = Bag(*args, **kwargs)

    assert not my_callable1.called
    result1 = bag.apply(my_callable1)
    assert my_callable1.called and result1 is my_callable1.return_value

    assert not my_callable2.called
    result2 = bag.apply(my_callable2)
    assert my_callable2.called and result2 is my_callable2.return_value

    assert result1 is not result2

    my_callable1.assert_called_once_with(*args, **kwargs)
    my_callable2.assert_called_once_with(*args, **kwargs)


def test_inherit():
    bag = Bag('a', a=1)
    bag2 = Bag.inherit('b', b=2, _parent=bag)
    bag3 = bag.extend('c', c=3)
    bag4 = Bag('d', d=4)

    assert bag.args == ('a', )
    assert bag.kwargs == {'a': 1}
    assert bag.flags is ()

    assert bag2.args == ('a', 'b', )
    assert bag2.kwargs == {'a': 1, 'b': 2}
    assert INHERIT_INPUT in bag2.flags

    assert bag3.args == ('a', 'c', )
    assert bag3.kwargs == {'a': 1, 'c': 3}
    assert bag3.flags is ()

    assert bag4.args == ('d', )
    assert bag4.kwargs == {'d': 4}
    assert bag4.flags is ()

    bag4.set_parent(bag)
    assert bag4.args == ('a', 'd', )
    assert bag4.kwargs == {'a': 1, 'd': 4}
    assert bag4.flags is ()

    bag4.set_parent(bag3)
    assert bag4.args == ('a', 'c', 'd', )
    assert bag4.kwargs == {'a': 1, 'c': 3, 'd': 4}
    assert bag4.flags is ()


def test_pickle():
    bag1 = Bag('a', a=1)
    bag2 = Bag.inherit('b', b=2, _parent=bag1)
    bag3 = bag1.extend('c', c=3)
    bag4 = Bag('d', d=4)

    # XXX todo this probably won't work with inheriting bags if parent is not there anymore? maybe that's not true
    # because the parent may be in the serialization output but we need to verify this assertion.

    for bag in bag1, bag2, bag3, bag4:
        pickled = pickle.dumps(bag)
        unpickled = pickle.loads(pickled)
        assert unpickled == bag


def test_eq_operator():
    assert Bag('foo') == Bag('foo')
    assert Bag('foo') != Bag('bar')
    assert Bag('foo') is not Bag('foo')
    assert Bag('foo') != Token('foo')
    assert Token('foo') != Bag('foo')


def test_repr():
    bag = Bag('a', a=1)
    assert repr(bag) == "<Bag ('a', a=1)>"


def test_iterator():
    bag = Bag()
    assert list(bag.apply([1, 2, 3])) == [1, 2, 3]
    assert list(bag.apply((1, 2, 3))) == [1, 2, 3]
    assert list(bag.apply(range(5))) == [0, 1, 2, 3, 4]
    assert list(bag.apply('azerty')) == ['a', 'z', 'e', 'r', 't', 'y']
