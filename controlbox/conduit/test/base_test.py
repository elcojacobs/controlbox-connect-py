import unittest
from unittest.mock import Mock, PropertyMock

from hamcrest import is_, assert_that, raises, calling
from io import IOBase

from controlbox.conduit.base import ConduitDecorator, ConduitStreamDecorator, DefaultConduit, Conduit, ConduitFactory


class ConduitTest(unittest.TestCase):

    def test_abstract_methods(self):
        sut = Conduit()
        assert_that(calling(sut.close), raises(NotImplementedError))
        assert_that(calling(sut.__getattribute__).with_args('input'), raises(NotImplementedError))
        assert_that(calling(sut.__getattribute__).with_args('output'), raises(NotImplementedError))
        assert_that(calling(sut.__getattribute__).with_args('open'), raises(NotImplementedError))
        assert_that(calling(sut.__getattribute__).with_args('target'), raises(NotImplementedError))


class ConduitDecoratorTest(unittest.TestCase):
    def test_target(self):
        mock = Mock()
        prop = PropertyMock(return_value="123")
        type(mock).target = prop
        sut = ConduitDecorator(mock)
        assert_that(sut.target, is_("123"))
        prop.assert_called_once()

    def test_close(self):
        mock = Mock()
        mock.close = Mock(return_value="123")
        sut = ConduitDecorator(mock)
        assert_that(sut.close(), is_(None))
        mock.close.assert_called_once()

    def test_open(self):
        mock = Mock()
        prop = PropertyMock(return_value=True)
        type(mock).open = prop
        sut = ConduitDecorator(mock)
        assert_that(sut.open, is_(True))
        prop.assert_called_once()

    def test_input(self):
        mock = Mock()
        io = IOBase()
        prop = PropertyMock(return_value=io)
        type(mock).input = prop
        sut = ConduitDecorator(mock)
        assert_that(sut.input, is_(io))
        prop.assert_called_once()

    def test_outut(self):
        mock = Mock()
        io = IOBase()
        prop = PropertyMock(return_value=io)
        type(mock).output = prop
        sut = ConduitDecorator(mock)
        assert_that(sut.output, is_(io))
        prop.assert_called_once()


class ConduitStreamDecoratorTest(unittest.TestCase):

    def test_constructor(self):
        mock = Mock()
        sut = ConduitStreamDecorator(mock)
        assert_that(sut._input, is_(None))
        assert_that(sut._output, is_(None))
        assert_that(sut.decorate, is_(mock))

    def test_input_calls_wrap_on_decorated_input(self):
        mock = Mock()
        io = IOBase()
        io2 = IOBase()
        type(mock).input = PropertyMock(return_value=io)
        sut = ConduitStreamDecorator(mock)
        sut._wrap_input = Mock(return_value=io2)
        assert_that(sut.input, is_(io2))
        sut._wrap_input.assert_called_once_with(io)

    def test_output_calls_wrap_on_decorated_output(self):
        mock = Mock()
        io = IOBase()
        io2 = IOBase()
        type(mock).output = PropertyMock(return_value=io)
        sut = ConduitStreamDecorator(mock)
        sut._wrap_output = Mock(return_value=io2)
        assert_that(sut.output, is_(io2))
        sut._wrap_output.assert_called_once_with(io)

    def test_immediate_close(self):
        mock = Mock()
        mock.close = Mock()
        sut = ConduitStreamDecorator(mock)
        sut.close()
        mock.close.assert_called_once()

    def test_stream_close(self):
        mock = Mock()
        mock.close = Mock()
        output = Mock()
        output.close = Mock()
        type(mock).output = PropertyMock(return_value=output)
        sut = ConduitStreamDecorator(mock)
        assert_that(sut.output, is_(output))
        sut.close()
        output.close.assert_called_once()
        mock.close.assert_called_once()

    def test_wrap_output(self):
        mock = Mock()
        sut = ConduitStreamDecorator(mock)
        assert_that(sut._wrap_output(123), is_(123))

    def test_wrap_input(self):
        mock = Mock()
        sut = ConduitStreamDecorator(mock)
        assert_that(sut._wrap_input(123), is_(123))


class DefaultConduitTest(unittest.TestCase):

    def test_constructor_read_write(self):
        read = IOBase()
        write = IOBase()
        sut = DefaultConduit(read, write)
        assert_that(sut.output, is_(write))
        assert_that(sut.input, is_(read))

    def test_set_streams(self):
        read = IOBase()
        write = IOBase()
        sut = DefaultConduit(None)
        sut.set_streams(read, write)
        assert_that(sut.output, is_(write))
        assert_that(sut.input, is_(read))

    def test_open(self):
        assert_that(DefaultConduit(None).open, is_(True))

    def test_constructor_read(self):
        read = IOBase()
        sut = DefaultConduit(read)
        assert_that(sut.output, is_(read))
        assert_that(sut.input, is_(read))

    def test_close_closes_both_streams(self):
        read = IOBase()
        write = IOBase()
        sut = DefaultConduit(read, write)
        read.close = Mock()
        write.close = Mock()
        sut.close()
        read.close.assert_called_once()
        write.close.assert_called_one()


class ConduitFactoryTest(unittest.TestCase):

    def test_call(self):
        f = ConduitFactory()
        assert_that(f, raises(NotImplementedError))
