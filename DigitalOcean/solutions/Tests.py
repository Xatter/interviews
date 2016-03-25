import unittest
import Server

OK = "OK\n"
FAIL = "FAIL\n"
ERROR = "ERROR\n"

class Test_CommandParsing(unittest.TestCase):
    # Proper Parse of all command types
    # Unexepected Input

    def setUp(self):
        self.indexer = Server.Indexer()

    def testSunnyDay(self):
        command, package, dependnecies = self.indexer.decode("INDEX|foo|bar")
        self.assertEqual(command, 'INDEX')
        self.assertEqual(package, 'foo')
        self.assertCountEqual(dependnecies, ['bar'])

    def test_DependenciesOptional(self):
        command, package, dependnecies = self.indexer.decode("INDEX|foo|")
        self.assertEqual(dependnecies, None)

    def test_MustHaveTwoPipes(self):
        command, package, dependnecies = self.indexer.decode("INDEX|foo")
        self.assertEqual('ERROR', command)

    def test_PackageCantBeList(self):
        command, package, dependnecies = self.indexer.decode("INDEX|foo,bar,baz|")
        self.assertEqual('ERROR', command)


class Test_Indexing(unittest.TestCase):
# * For `INDEX` commands, the server returns `OK\n` if the package could be indexed or if it was already present. It returns `FAIL\n` if the package cannot be indexed because some of its dependencies aren't indexed yet and need to be installed first.
    def setUp(self):
        self.indexer = Server.Indexer()

    def test_ShouldIndexSinglePackage(self):
        self.assertEqual(OK, self.indexer.index('foo', None))

    def test_ShouldReturnOKIfAlreadyExists(self):
        self.indexer.index('foo', None)
        self.assertEqual(OK, self.indexer.index('foo', None))

    def test_ShouldIndexTwoPackages(self):
        self.assertEqual(OK, self.indexer.index('foo', None))
        self.assertEqual(OK, self.indexer.index('bar', None))

    def test_ShouldNotIndexIfDependencyNotIndexed(self):
        self.assertEqual(FAIL, self.indexer.index('bar', ['foo']))

    def test_ShouldIndexWithDependency(self):
        self.indexer.index('foo', None)
        self.assertEqual(OK, self.indexer.index('bar', ['foo']))

class Test_Querying(unittest.TestCase):
    def setUp(self):
        self.indexer = Server.Indexer()

    def test_QueryFails(self):
        self.assertEqual(FAIL, self.indexer.query('foo'))

    def test_QueryReturnsOk(self):
        self.indexer.index('foo',None)
        self.assertEqual(OK, self.indexer.query('foo'))


# * For `QUERY` commands, the server returns `OK\n` if the package is indexed. It returns `FAIL\n` if the package isn't indexed.
class Test_Removing(unittest.TestCase):
# The response code returned should be as follows:
# * For `REMOVE` commands, the server returns `OK\n` if the package could be removed from the index. 
#   It returns `FAIL\n` if the package could not be removed from the index because some other indexed package depends on it. 
#   It returns `OK\n` if the package wasn't indexed.

    def setUp(self):
        self.indexer = Server.Indexer()

    def test_RemoveShouldReturnOkForNonIndexedPackage(self):
        self.assertEqual(OK, self.indexer.remove('foo'))

    def test_ShouldRemoveSoloPackage(self):
        self.indexer.index('foo', None)
        self.assertEqual(OK, self.indexer.remove('foo'))

    def test_ShouldNotRemoveIfDependencyOfAnotherPackage(self):
        self.indexer.index('foo', None)
        self.indexer.index('bar', ['foo'])
        self.assertEqual(FAIL, self.indexer.remove('foo'))

    def test_ShouldNotRemoveIfDependencyOfDependencyOfAnotherPackage(self):
        # Note to self, we may not need this test case I need some more clarity on the requirements
        self.indexer.index('foo', None)
        self.indexer.index('bar', ['foo'])
        self.indexer.index('baz', ['bar'])
        self.assertEqual(FAIL, self.indexer.remove('bar'))

    def test_ShouldRemoveInCorrectOrder(self):
        self.indexer.index('foo', None)
        self.indexer.index('bar', ['foo'])
        self.indexer.index('baz', ['bar'])

        self.assertEqual(OK, self.indexer.remove('baz'))
        self.assertEqual(OK, self.indexer.remove('bar'))
        self.assertEqual(OK, self.indexer.remove('foo'))

class Test_Server(unittest.TestCase):
    # * If the server doesn't recognise the command or if there's any problem with the message sent by the client it should return `ERROR\n`.
    pass
