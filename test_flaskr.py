from flask_sqlalchemy import SQLAlchemy
from random import randint
import unittest

from models import Category, Item

from flaskr import create_app


class RESTTestCase(unittest.TestCase):
    """This class represents the rest test case"""

    def assert404(self, res):
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json["msg"], "resource not found, aborting...")
        self.assertEqual(res.json["data"], None)
        self.assertFalse(res.json["success"])

    def createCateg(self, categ):
        categ = Category(
            type=categ,
        )
        with self.app.app_context():
            self.db.session.add(categ)
            self.db.session.commit()
            self.db.session.close()

    def createCategs(self):
        for i in range(5):
            self.createCateg("test categ " + str(i))

    def createItem(self, item, categToInsert=None):
        categories = self.getCategs()
        with self.app.app_context():
            if categToInsert is None:
                categToInsert = categories[randint(0, 4)].id
            item = Item(
                item=item,
                category=categToInsert
            )
            self.db.session.add(item)
            self.db.session.commit()
            self.db.session.close()  

    def createItems(self, nbOfItems=5):
        for i in range(nbOfItems):
            self.createItem(
                "test item " + str(i)
            )

    def deleteData(self):
        with self.app.app_context():
            self.db.session.query(Category).delete()
            self.db.session.query(Item).delete()
            self.db.session.commit()
            self.db.session.close()

    def getCategs(self):
        categories = Category.query.order_by(Category.id).all()
        return categories

    def initDb(self):
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app("test")
        self.app.config["ITEMS_BATCH_SIZE"] = 10
        self.client = self.app.test_client
        self.initDb()
        self.deleteData()

    def tearDown(self):
        """Hook executed after each test"""
        pass

    def test_get_categories_returns_expected_categories(self):
        """Given a web client, when it hits /api/categories with a GET request,
           then it should get the expected response payload"""
        self.createCategs()
        res = self.client().get('/api/categories')
        self.assertTrue(res.json["success"])
        self.assertEqual(res.json["msg"], "fetched categories")
        self.assertEqual(res.json["data"]["totalCategs"], 5)
        for j in range(5):
            self.assertEqual(
                res.json["data"]["categories"][j]["type"],
                "test categ "+str(j)
            )

    def test_get_categories_with_no_categories_returns_404(self):
        """Given a web client, when it hits /api/categories with a GET request
           and there are no categories in the DB, then it should get the
           expected 404 response"""
        # setup empties db at each test iteration,
        # so there should not be any categories in there
        res = self.client().get('/api/categories')
        self.assert404(res)

    def test_get_items_returns_all_the_items(self):
        """Given a web client, when it hits /api/items with a GET request
           and there are 5 items in DB, then it should get all the
           items in the response payload"""
        self.createCategs()
        self.createItems()
        res = self.client().get('/api/items')
        self.assertTrue(res.json["success"])
        self.assertEqual(res.json["msg"], "fetched items")
        self.assertEqual(res.json["data"]["totalItems"], 5)

    def test_get_items_with_no_page_returns_the_first_10_items(self):
        """Given a web client, when it hits /api/items with a GET request
           and there are 11 items in DB, then the response payload should
           contain the ten first items"""
        self.createCategs()
        self.createItems(11)
        res = self.client().get('/api/items')
        eleventhItem = list(
            filter(
                lambda item: item['item'] == "test item 10",
                res.json["data"]["items"]
            )
        )
        self.assertTrue(res.json["success"])
        self.assertEqual(res.json["msg"], "fetched items")
        self.assertEqual(res.json["data"]["totalItems"], 11)
        self.assertEqual(len(eleventhItem), 0)
        self.assertEqual(len(res.json["data"]["items"]), 10)
        self.assertEqual(
            res.json["data"]["items"][0]["item"],
            "test item 0"
        )
        self.assertEqual(
            res.json["data"]["items"][9]["item"],
            "test item 9"
        )

    def test_11_items_in_DB_and_page_2_returns_the_11th_item(self):
        """Given a web client, when it hits /api/items with a GET request
           and there are 11 items in DB and page 2 is specified, then the
           response payload should only contain the 11th item"""
        self.createCategs()
        self.createItems(11)
        res = self.client().get('/api/items?page=2')
        self.assertEqual(res.json["data"]["totalItems"], 11)
        self.assertEqual(len(res.json["data"]["items"]), 1)
        self.assertEqual(
            res.json["data"]["items"][0]["item"],
            "test item 10"
        )

    def test_11_items_in_DB_and_page_3_specified_returns_404(self):
        """Given a web client, when it hits /api/items with a GET request
           and there are 11 items in DB and page 3 is specified,
           then the response should be a 404 response"""
        self.createCategs()
        self.createItems(11)
        res = self.client().get('/api/items?page=3')
        self.assert404(res)

    def test_get_items_includes_categories_list_in_response(self):
        """Given a web client, when it hits /api/items with a GET request
           and there are items in DB,
           then the response payload should contain the list categs"""
        self.createCategs()
        self.createItems()
        res = self.client().get('/api/items')
        self.assertEqual(len(res.json["data"]["categories"]), 5)
        self.assertEqual(
            res.json["data"]["categories"][4]["type"],
            "test categ 4"
        )

    def test_none_as_current_categ_when_no_categ_specified(self):
        """Given a web client,
           when it hits /api/items with a GET request
           without specifying the category,
           then the response payload should contain `None` for current categ"""
        self.createCategs()
        self.createItems()
        res = self.client().get('/api/items')
        self.assertEqual(res.json["data"]["currentCategory"], '')

    def test_get_items_returns_relevant_categs_when_categ_specified(self):
        """Given a web client, when it hits /api/items with a GET request
           and there is relevant data in db
           and categ is specified as a query param,
           then the response payload should only contain
           the items linked to that category"""
        # arrange
        filteringCateg = "filtering_test_categ"
        self.createCategs()
        self.createItems()
        # create a specific categ for the test
        self.createCateg(filteringCateg)
        # get the id of the newly created categ
        newlyInsertedCateg = Category.query.filter_by(
            type=filteringCateg
        ).first()
        # create a item with that specific categ
        self.createItem(
            "filtering_test_item",
            newlyInsertedCateg.id
        )
        # act
        res = self.client().get('/api/items?categ='+filteringCateg)
        # assert
        self.assertEqual(len(res.json["data"]["items"]), 1)
        self.assertEqual(
            res.json["data"]["items"][0]["item"],
            "filtering_test_item"
        )
        self.assertEqual(
            res.json["data"]["currentCategory"],
            "filtering_test_categ"
        )

    def test_get_items_returns_with_non_existing_categ_returns_404(self):
        """Given a web client, when it hits /api/items with a GET request
           with a non existing categ as a query param,
           then it should get a 404 response"""
        self.createCategs()
        self.createItems()
        res = self.client().get("/api/items?categ=non_existing")
        self.assert404(res)

    def test_deleting_an_existing_item_results_in_item_deleted(self):
        """Given a web client, when it hits /api/items
           with a DELETE request with an existing item as a query param,
           then it should get a 204 response"""
        # arrange
        deletingCateg = "deleting_test_categ"
        self.createCategs()
        self.createItems()
        # create a specific categ for the test
        self.createCateg(deletingCateg)
        # get the id of the newly created categ
        newlyInsertedCateg = Category.query.filter_by(
            type=deletingCateg
        ).first()
        # create a item with that specific categ
        self.createItem(
            "deleting_test_item",
            newlyInsertedCateg.id
        )
        newlyInsertedItem = Item.query.filter_by(
            item="deleting_test_item"
        ).first()
        # act
        res = self.client().delete("/api/items/"+str(
            newlyInsertedItem.id
        ))
        # assert
        self.assertEqual(res.status_code, 204)

    def test_deleting_a_non_existing_item_results_in_item_deleted(
        self
    ):
        """Given a web client,
           when it hits /api/items with a DELETE request
           with a non existing item as a query param,
           then it should get a 422 response"""
        # act
        res = self.client().delete("/api/items/9999")
        # assert
        self.assertEqual(res.status_code, 422)
        self.assertEqual(
            res.json["msg"],
            "could not process your request, aborting..."
        )
        self.assertEqual(res.json["data"], None)
        self.assertFalse(res.json["success"])

    def test_creating_a_item_results_in_new_item_persisted(self):
        """Given a web client,
           when it hits /api/items with a POST request
           with a valid item payload,
           then the new item should be persisted in DB"""
        # arrange
        postingCateg = "posting_test_categ"
        self.createCategs()
        self.createItems()
        # create a specific categ for the test
        self.createCateg(postingCateg)
        # get the id of the newly created categ
        newlyInsertedCateg = Category.query.filter_by(
            type=postingCateg
        ).first()
        # act
        res = self.client().post("/api/items", json={
            "item": "posting_test_item",
            "category": newlyInsertedCateg.id
        })
        newlyInsertedItem = Item.query.filter(
            Item.item == "posting_test_item"
        ).one_or_none()
        # assert
        self.assertIsNotNone(newlyInsertedItem)

    def test_creating_items_returns_a_201(self):
        """Given a web client,
           when it hits /api/items with a POST request
           with a valid item payload,
           then it should get a 201 response"""
        # arrange
        postingCateg = "posting_test_categ"
        self.createCategs()
        self.createItems()
        # create a specific categ for the test
        self.createCateg(postingCateg)
        # get the id of the newly created categ
        newlyInsertedCateg = Category.query.filter_by(
            type=postingCateg
        ).first()
        # act
        res = self.client().post("/api/items", json={
            "item": "posting_test_item",
            "category": newlyInsertedCateg.id
        })
        self.assertEqual(res.status_code, 201)

    def test_create_item_with_invalid_payload_fails(self):
        """Given a web client,
           when it hits /api/items with a POST request
           with a invalid item payload,
           then it should get a 400 response"""        
        # arrange
        postingCateg = "posting_test_categ"
        self.createCategs()
        self.createItems()
        # create a specific categ for the test
        self.createCateg(postingCateg)
        # get the id of the newly created categ
        newlyInsertedCateg = Category.query.filter_by(
            type=postingCateg
        ).first()
        # act
        res = self.client().post("/api/items", json={
            "answer": "posting_test_answer",
            "category": newlyInsertedCateg.id
        })
        self.assertEqual(res.status_code, 400)

    def test_creating_same_item_twice_fails(self):
        """Given a web client,
           when it hits /api/items with a POST request
           with a valid item payload,
           and it re posts the same request,
           then it should get a 422 response"""
        # arrange
        postingCateg = "posting_test_categ"
        self.createCategs()
        self.createItems()
        # create a specific categ for the test
        self.createCateg(postingCateg)
        # get the id of the newly created categ
        newlyInsertedCateg = Category.query.filter_by(
            type=postingCateg
        ).first()
        # act
        # sending the first item
        self.client().post("/api/items", json={
            "item": "posting_test_item",
            "category": newlyInsertedCateg.id
        })
        # sending the same item again
        res = self.client().post("/api/items", json={
            "item": "posting_test_item",
            "category": newlyInsertedCateg.id
        })
        self.assertEqual(res.status_code, 422)

    def test_returns_relevant_item_when_search_term_specified(self):
        """Given a web client, when it hits
           /api/items?searchTerm=search_test_item
           with a GET request,
           then the response payload should only contain
           the items with that search term in their title"""
        # arrange
        searchCateg = "search_test_categ"
        self.createCategs()
        self.createItems()
        # create a specific categ for the test
        self.createCateg(searchCateg)
        # get the id of the newly created categ
        newlyInsertedCateg = Category.query.filter_by(
            type=searchCateg
        ).first()
        # create a item with a given title
        self.createItem(
            "search_test_item",
            newlyInsertedCateg.id
        )
        # create a second item with a resemblant title
        self.createItem(
            "search_test_item2",
            newlyInsertedCateg.id
        )
        # create a 3rd item with something else entirely as a title
        self.createItem(
            "something_else_entirely",
            newlyInsertedCateg.id
        )
        # act
        res = self.client().get(
            "/api/items?searchTerm=search_test_item"
        )
        # assert
        self.assertEqual(len(res.json["data"]["items"]), 2)
        self.assertEqual(
            res.json["data"]["items"][0]["item"],
            "search_test_item"
        )
        self.assertEqual(
            res.json["data"]["items"][1]["item"],
            "search_test_item2"
        )

    def test_item_when_nonexisting_search_term_specified(self):
        """Given a web client, when it hits
           /api/items?searchTerm=nonexisting
           with a GET request,
           then the response should be a 404"""
        # arrange
        self.createCategs()
        self.createItems()
        # act
        res = self.client().get(
            "/api/items?searchTerm=nonexisting"
        )
        # assert
        self.assertEqual(res.status_code, 404)

    def test_app_categ_filtering(self):
        """Given a web client,
        when it hits /api/stuff with a POST request
        and a input payload containing the categ
        then the response body should contain one item
        and it must have the same category"""
        # arrange
        appCateg = "app_test_categ"
        self.createCategs()
        self.createItems()
        # create a specific categ for the test
        self.createCateg(appCateg)
        # get the id of the newly created categ
        newlyInsertedCateg = Category.query.filter_by(
            type=appCateg
        ).first()
        # create a item with a given title
        self.createItem(
            "app_test_item",
            newlyInsertedCateg.id
        )
        # act
        res = self.client().post("/api/stuff", json={
            "category": "app_test_categ",
            "prevItems": []
        })
        # assert
        self.assertEqual(res.json["data"]["item"], "app_test_item")
        self.assertEqual(
            res.json["data"]["category"],
            "app_test_categ"
        )

    def test_app_categ_404(self):
        """Given a web client,
        when it hits /api/stuff with a POST request
        and a input payload containing a non existing categ
        then the response should be a 404"""
        res = self.client().post("/api/stuff", json={
            "category": "non_existing_categ",
            "prevItems": []
        })
        self.assertEqual(res.status_code, 404)

    def test_app_prev_items(self):
        """Given a web client, when it hits /api/stuff
        with a POST request and a input payload
        containing the previous items
        then the response body should contain a item
        and it must not be in the previous items array"""
        # arrange
        appPrevCateg = "app_prev_test_categ"
        self.createCategs()
        self.createItems()
        # create a specific categ for the test
        self.createCateg(appPrevCateg)
        # get the id of the newly created categ
        newlyInsertedCateg = Category.query.filter_by(
            type=appPrevCateg
        ).first()
        # create a item with a given title
        self.createItem(
            "app_prev_test_item",
            newlyInsertedCateg.id
        )
        firstItem = Item.query.filter_by(
            item="app_prev_test_item"
        ).first()
        # create another item
        self.createItem(
            "app_prev_test_item2",
            newlyInsertedCateg.id
        )
        secondItem = Item.query.filter_by(
            item="app_prev_test_item2"
        ).first()
        # act
        res = self.client().post("/api/stuff", json={
            "category": "app_prev_test_categ",
            "prevItems": [secondItem.id]
        })
        res2 = self.client().post("/api/stuff", json={
            "category": "app_prev_test_categ",
            "prevItems": [firstItem.id]
        })
        # assert
        self.assertEqual(
            res.json["data"]["item"],
            "app_prev_test_item"
        )
        self.assertEqual(
            res2.json["data"]["item"],
            "app_prev_test_item2"
        )

    def test_wrong_app_prev_items(self):
        """Given a web client, when it hits /api/items
        with a POST request and a input payload
        containing invalid previous items
        then the response should be a 404"""
        # arrange
        self.createCateg("placeholder_categ")
        res = self.client().post("/api/stuff", json={
            "category": "placeholder_categ",
            "prevItems": [9999, 9998]
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            res.json["msg"],
            "bad request, please check your input params..."
        )
        self.assertEqual(res.json["data"], None)
        self.assertFalse(res.json["success"])

    def test_app__no_prev_items(self):
        """Given a web client, when it hits /api/items
        with a POST request and a input payload
        containing no previous
        then the response body should contain a item"""
        # arrange
        appPrevCateg = "no_prev_test_categ"
        self.createCategs()
        self.createItems()
        # create a specific categ for the test
        self.createCateg(appPrevCateg)
        # get the id of the newly created categ
        newlyInsertedCateg = Category.query.filter_by(
            type=appPrevCateg
        ).first()
        # create a item with a given title
        self.createItem(
            "no_prev_test_item",
            newlyInsertedCateg.id
        )
        # act
        res = self.client().post("/api/stuff", json={
            "category": "no_prev_test_categ",
            "prevItems": []
        })
        # assert
        self.assertEqual(
            res.json["data"]["item"],
            "no_prev_test_item"
        )

    def test_app_all_categs(self):
        """Given a web client,
        when it hits /api/stuff with a POST request
        and a input payload containing `all` as a categ
        then the response body should contain one item
        and the next item can be of another category"""
        # arrange
        appAllCategs = "app_test_all_categs"
        appAllCategs2 = "app_test_all_categs2"
        # create a specific categ for the test
        self.createCateg(appAllCategs)
        # create a second specific categ for the test
        self.createCateg(appAllCategs2)
        # get the id of the newly created categ
        newlyInsertedCateg = Category.query.filter_by(
            type=appAllCategs
        ).first()
        # get the id of the second newly created categ
        newlyInsertedCateg2 = Category.query.filter_by(
            type=appAllCategs2
        ).first()
        # create a item with a given title
        firstItemStr = "app_test_item"
        self.createItem(
            firstItemStr,
            newlyInsertedCateg.id
        )
        # get the id of the second newly created first item
        firstItem = Item.query.filter_by(
            item=firstItemStr
        ).first()
        # create another item
        self.createItem(
            "app_test_item2",
            newlyInsertedCateg2.id
        )
        # act
        res = self.client().post("/api/stuff", json={
            "category": "all",
            "prevItems": [firstItem.id]
        })
        # assert
        self.assertEqual(res.json["data"]["item"], "app_test_item2")
        self.assertEqual(
            res.json["data"]["category"],
            "app_test_all_categs2"
        )

    def test_get_base_url_200(self):
        """Given a web user,
        when he hits /api with a get request,
        then the response should have a status code of 200
        and it should show that the API is up"""
        res = self.client().get('/api')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json["success"])
        self.assertIsNone(res.json["data"])
        self.assertEqual(res.json["msg"], "REST API is up")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
