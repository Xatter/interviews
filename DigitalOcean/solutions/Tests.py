import unittest
import Server

OK = "OK\n"
FAIL = "FAIL\n"
ERROR = "ERROR\n"

class Test_CommandParsing(unittest.TestCase):
    # Proper Parse of all command types
    # Unexepected Input

    def setUp(self):
        self.server = Server.Server()

    def testSunnyDay(self):
        command, package, dependnecies = self.server.decode("INDEX|foo|bar\n")
        self.assertEqual(command, 'INDEX')
        self.assertEqual(package, 'foo')
        self.assertCountEqual(dependnecies, ['bar'])

    def test_DependenciesOptional(self):
        command, package, dependnecies = self.server.decode("INDEX|foo|\n")
        self.assertEqual(dependnecies, None)

class Test_Indexing(unittest.TestCase):
# * For `INDEX` commands, the server returns `OK\n` if the package could be indexed or if it was already present. It returns `FAIL\n` if the package cannot be indexed because some of its dependencies aren't indexed yet and need to be installed first.
    def setUp(self):
        self.server = Server.Server()

    def test_ShouldIndexSinglePackage(self):
        self.assertEqual(OK, self.server.index('foo', None))

    def test_ShouldReturnOKIfAlreadyExists(self):
        self.server.index('foo', None)
        self.assertEqual(OK, self.server.index('foo', None))

    def test_ShouldIndexTwoPackages(self):
        self.assertEqual(OK, self.server.index('foo', None))
        self.assertEqual(OK, self.server.index('bar', None))

    def test_ShouldNotIndexIfDependencyNotIndexed(self):
        self.assertEqual(FAIL, self.server.index('bar', ['foo']))

    def test_ShouldIndexWithDependency(self):
        self.server.index('foo', None)
        self.assertEqual(OK, self.server.index('bar', ['foo']))

class Test_Querying(unittest.TestCase):
    def setUp(self):
        self.server = Server.Server()

    def test_QueryFails(self):
        self.assertEqual(FAIL, self.server.query('foo'))

    def test_QueryReturnsOk(self):
        self.server.index('foo',None)
        self.assertEqual(OK, self.server.query('foo'))


# * For `QUERY` commands, the server returns `OK\n` if the package is indexed. It returns `FAIL\n` if the package isn't indexed.
class Test_Removing(unittest.TestCase):
# The response code returned should be as follows:
# * For `REMOVE` commands, the server returns `OK\n` if the package could be removed from the index. 
#   It returns `FAIL\n` if the package could not be removed from the index because some other indexed package depends on it. 
#   It returns `OK\n` if the package wasn't indexed.

    def setUp(self):
        self.server = Server.Server()

    def test_RemoveShouldReturnOkForNonIndexedPackage(self):
        self.assertEqual(OK, self.server.remove('foo'))

    def test_ShouldRemoveSoloPackage(self):
        self.server.index('foo', None)
        self.assertEqual(OK, self.server.remove('foo'))

    def test_ShouldNotRemoveIfDependencyOfAnotherPackage(self):
        self.server.index('foo', None)
        self.server.index('bar', ['foo'])
        self.assertEqual(FAIL, self.server.remove('foo'))

    def test_ShouldNotRemoveIfDependencyOfDependencyOfAnotherPackage(self):
        # Note to self, we may not need this test case I need some more clarity on the requirements
        self.server.index('foo', None)
        self.server.index('bar', ['foo'])
        self.server.index('baz', ['bar'])
        self.assertEqual(FAIL, self.server.remove('bar'))

    def test_ShouldRemoveInCorrectOrder(self):
        self.server.index('foo', None)
        self.server.index('bar', ['foo'])
        self.server.index('baz', ['bar'])

        self.assertEqual(OK, self.server.remove('baz'))
        self.assertEqual(OK, self.server.remove('bar'))
        self.assertEqual(OK, self.server.remove('foo'))

class Test_Server(unittest.TestCase):
    # * If the server doesn't recognise the command or if there's any problem with the message sent by the client it should return `ERROR\n`.
    pass
