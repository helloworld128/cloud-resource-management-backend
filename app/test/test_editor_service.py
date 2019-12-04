import unittest
import os, shutil
from app.test.base import BaseTestCase
from app.main.service.editor_service import get_tree


class TestEditorService(BaseTestCase):

    def test_get_tree(self):
        try:
            shutil.rmtree('root')
        except:
            pass
        os.mkdir('root')
        os.chdir('root')
        os.mkdir('level1')
        fp = open('lvl1.txt', 'w')
        fp.write('test')
        fp.close()
        os.chdir('level1')
        os.mkdir('level2')
        os.chdir('../../')
        res = get_tree('root')
        expected = [{'label': 'level1', 'children': [{'label': 'level2', 'children': []}]},
                    {'label': 'lvl1.txt'}]
        self.assertTrue(res == expected)
        shutil.rmtree('root')


if __name__ == '__main__':
    unittest.main()

