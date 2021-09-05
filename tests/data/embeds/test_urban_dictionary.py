from data.embeds.urban_dictionary import Definition
import unittest


class TestUD(unittest.TestCase):
    def test_clean_string(self):
        self.assertEqual(
            Definition.clean_string("A definition [with links] to other [definitions]"),
            "A definition with links to other definitions"
        )

        no_processing = "A string that needs no processing."
        self.assertEqual(Definition.clean_string(no_processing), no_processing)

        long_string = "A very long string that hopefully exceeds the 1024 character limit for embed field values, " \
                      "in order to test if the truncation part of this specific function works as expected. " \
                      "The issue is that coming up with a string that exceeds the 1024 embed field value character " \
                      "limit is quite tedious, so I have no idea how I plan on ever finishing this." \
                      "As of the writing of this sentence, I'm only a third of the way there." \
                      "Crazy. I could probably just toss some lorem ipsum in there, but that would be no fun." \
                      "Or would it? Hey GitHub, Didier here." \
                      "Instead I would like to take this opportunity to out my frustrations on the abomination of a " \
                      "\"language\" that is Haskell. You see, Haskell is just terrible and useless. " \
                      "It truly does pose the bane of my existence, and I deeply hope that I will never have to use it " \
                      "ever again in my life. Good thing I somehow managed to pass that class, otherwise I would've " \
                      "probably collapsed mentally on the spot. As it turns out, though, this sentence is already in the " \
                      "900 character range, so I don't have much of a reason to continue writing about the worst " \
                      "invention humanity has ever come up with."

        self.assertGreater(len(long_string), 1024)
        self.assertEqual(len(Definition.clean_string(long_string)), 1024)
        self.assertEqual(Definition.clean_string(long_string)[-3:], "...")

    def test_ratio(self):
        dic = {
            "thumbs_up": 5,
            "thumbs_down": 0
        }
        self.assertEqual(Definition.ratio(dic), 100.0)

        dic["thumbs_down"] = 5
        self.assertEqual(Definition.ratio(dic), 50.0)

        dic["thumbs_up"] = 0
        self.assertEqual(Definition.ratio(dic), 0)
