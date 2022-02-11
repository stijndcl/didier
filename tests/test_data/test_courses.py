import unittest

from data.courses import load_courses, find_course_from_name


class TestCourses(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.courses = load_courses()

    def test_find_course(self):
        self.assertIsNone(find_course_from_name("garbage", self.courses))
        self.assertIsNone(find_course_from_name("garbage"))

        # Find by name
        webdev = find_course_from_name("Webdevelopment", self.courses)
        self.assertIsNotNone(webdev)
        self.assertEqual(webdev.code, "C003779")

        # Find by abbreviation
        infosec = find_course_from_name("infosec", self.courses)
        self.assertIsNotNone(infosec)
        self.assertEqual(infosec.code, "E019400")

        # Case sensitive
        not_found = find_course_from_name("ad3", self.courses, case_insensitive=False)
        self.assertIsNone(not_found)

        # Find by alt name
        pcs = find_course_from_name("parallel computer systems", self.courses)
        self.assertIsNotNone(pcs)
        self.assertEqual(pcs.code, "E034140")
