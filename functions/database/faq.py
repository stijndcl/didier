from functions.database import utils


def getCategories():
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute(
        """SELECT name FROM faq_categories"""
    )
    return cursor.fetchall()


def addCategory(name):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute(
        """INSERT INTO faq_categories(name) VALUES (%s)""", (name.lower(),)
    )
    connection.commit()


def addQuestion(category: str, question: str, answer: str, answer_markdown: str = None):
    connection = utils.connect()
    cursor = connection.cursor()

    # Find the Id of this category
    cursor.execute(
        """SELECT id FROM faq_categories WHERE name = %s""", (category.lower(),)
    )
    categoryId = cursor.fetchall()[0]

    if not categoryId:
        return

    categoryId = categoryId[0]

    # Check if a markdown string has to be added
    if answer_markdown is None:
        cursor.execute(
            """INSERT INTO faq_entries(category_id, question, answer) VALUES (%s, %s, E%s)""",
            (categoryId, question, answer,)
        )
    else:
        cursor.execute(
            """INSERT INTO faq_entries(category_id, question, answer, answer_markdown) VALUES (%s, %s, E%s, E%s)""", (categoryId, question, answer, answer_markdown)
        )

    connection.commit()


def getCategory(category):
    connection = utils.connect()
    cursor = connection.cursor()
    cursor.execute(
        """SELECT *
        FROM faq_entries INNER JOIN faq_categories fc on faq_entries.category_id = fc.id 
        WHERE %s = fc.name""",
        (category.lower(),)
    )
    return cursor.fetchall()
