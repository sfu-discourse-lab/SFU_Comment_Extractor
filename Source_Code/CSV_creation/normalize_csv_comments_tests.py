import unittest
import normalize_csv_comments
from normalize_csv_comments import word_segmentation
from normalize_csv_comments import read_dictionary

class TestSegmenter(unittest.TestCase):

    def setUp(self):
        self.dictionary = read_dictionary()

    #def test_punctuation(self):
    #    input_text = r"Give your husband a big big kiss for me.But don't comehere."
    #    expected = r"Give your husband a big big kiss for me. But don't come here."
    #    self.assertEqual( word_segmentation(input_text), expected)

    def test_simple_period(self):
        '''
        :return:
         This is a simple test case where space is missing after the sentence ending period.'
        '''
        print('Simple test case where space is missing after the sentence ending period.')
        input_text = r"Rich,Funny you should mention the Roman Empire.That reminds me - Jesus Hippy was crucified for your skins."
        expected = r"Rich,Funny you should mention the Roman Empire. That reminds me - Jesus Hippy was crucified for your skins."
        self.assertEqual(word_segmentation(input_text, self.dictionary), expected)

if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStringMethods)
    unittest.TextTestRunner(verbosity=4).run(suite)


