import unittest
import normalize_csv_comments
from normalize_csv_comments import word_segmentation
from normalize_csv_comments import normalize

class TestSegmenter(unittest.TestCase):

    def setUp(self):
        pass


    def test_normalization(self):
        '''
        :return:
         This is a simple test case where space is missing after the sentence ending period.'
        '''
        print('Running simple test cases where space is missing after the sentence ending period.')
        input_text = r'tired of having their paychequaes plundered is another'
        expected = r'tired of having their paychequaes plundered is another'
        self.assertEqual(normalize(input_text), expected)

        input_text = r"Rich,Funny you should mention the Roman Empire.That reminds me - Jesus Hippy was crucified for your skins."
        expected = r"Rich, Funny you should mention the Roman Empire. That reminds me - Jesus Hippy was crucified for your skins."
        self.assertEqual(normalize(input_text), expected)

        input_text = r"They gone from the Nazi youth to a participant in the Dirty War.Lord help us."
        expected = r"They gone from the Nazi youth to a participant in the Dirty War. Lord help us."
        self.assertEqual(normalize(input_text), expected)

        input_text = r'''Why should temporary workers get paid more??How about Tim Horton's and all the rest of the companies rushing to hire all of these temporary foreign workers hire CANADIANS and PAY THEM A LIVING WAGE?HOW ABOUT THAT, HUH?This whole temp worker incentive is a drive the labour force to the bottom, nothing more.The government should be much tougher on hiring practices with these companies and instead build incentives for young Canadians, and especially in apprenticeship programs.'''
        expected = r'''Why should temporary workers get paid more?? How about Tim Horton's and all the rest of the companies rushing to hire all of these temporary foreign workers hire CANADIANS and PAY THEM A LIVING WAGE? HOW ABOUT THAT, HUH? This whole temp worker incentive is a drive the labour force to the bottom, nothing more. The government should be much tougher on hiring practices with these companies and instead build incentives for young Canadians, and especially in apprenticeship programs.'''
        self.assertEqual(normalize(input_text), expected)

        # Make sure that the code is retaining newly created or mispelled words (e.g., Fibulously)
        input_text = r'Fibulously good...'
        expected = r'Fibulously good...'
        self.assertEqual(normalize(input_text), expected)

        input_text = r'Plagiarists are barnacles on the state of journalism.'
        expected = r'Plagiarists are barnacles on the state of journalism.'
        self.assertEqual(normalize(input_text), expected)
        r'Is it your view that we should just sack these lay about s --'
        r'Is it your view that we should just sack these layabouts -- '

if __name__ == '__main__':
    unittest.main()
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestStringMethods)
    #unittest.TextTestRunner(verbosity=4).run(suite)


