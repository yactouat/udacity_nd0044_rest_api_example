from unicodedata import category
from flask import abort, jsonify, request
from helpers import paginate_items
import sys

from models import Category, Item, db


def init_routes(app):

    def abort400IfNoField(fields):
        for field in fields:
            try:
                request.get_json()[field]
                pass
            except KeyError as k:
                abort(400)

    @app.route("/api/items", methods=["POST"])
    def create_item():
        error = False
        abort400IfNoField(["item", "category"])
        try:
            item = Item(
                item=request.get_json()["item"],
                category=request.get_json()["category"]
            )
            if not item.checkItemUniqueness():
                error = True
            else:
                db.session.add(item)
                db.session.commit()
                formattedItem = item.format()
        except Exception as e:
            error = True
            print(sys.exc_info())
            db.session.rollback()
        finally:
            db.session.close()
            if error:
                abort(422)
            else:
                return jsonify({
                    "msg": "item created",
                    "success": True,
                    "data": formattedItem
                }), 201

    @app.route('/api/items/<item_id>', methods=['DELETE'])
    def delete_item(item_id):
        error = False
        try:
            item = Item.query.filter_by(id=item_id).first()
            if item is None:
                error = True
            else:
                Item.query.filter_by(id=item_id).delete()
                db.session.commit()
        except Exception as e:
            error = True
            db.session.rollback()
            print(str(e))
        finally:
            db.session.close()
            if error:
                abort(422)
            else:
                # a no content response is not supposed to have a body
                return '', 204

    @app.route("/api", methods=["GET"])
    def get_base_url():
        return jsonify({
            "msg": "REST API is up",
            "success": True,
            "data": None
        }), 200

    @app.route("/api/categories", methods=["GET"])
    def get_categories():
        categories = []
        categories = Category.query.order_by(Category.id).all()
        formattedCategs = [category.format() for category in categories]
        if (len(formattedCategs) == 0):
            abort(404)
        else:
            return jsonify({
                "msg": "fetched categories",
                "success": True,
                "data": {
                    "categories": formattedCategs,
                    "totalCategs": len(formattedCategs)
                }
            }), 200

    @app.route("/api/items", methods=["GET"])
    def get_items():
        items = None
        requestedCategStr = request.args.get("categ", '', type=str)
        requestedSearchTermStr = request.args.get("searchTerm", '', type=str)
        if requestedCategStr == '':
            items = Item.query.order_by(
                Item.id
            ).filter(Item.item.ilike(
                '%'+requestedSearchTermStr+'%'
            )).all()
        else:
            requestedCateg = Category.query.filter_by(
                type=requestedCategStr
            ).first()
            if requestedCateg is None:
                abort(404)
            items = Item.query.filter_by(
                category=requestedCateg.id
            ).order_by(
                Item.id
            ).filter(Item.item.ilike(
                '%'+requestedSearchTermStr+'%'
            )).all()
        formattedItems = [item.format() for item in items]
        categories = Category.query.order_by(Category.id).all()
        paginatedItems = paginate_items(
            app.config["ITEMS_BATCH_SIZE"],
            request.args.get("page", 1, type=int),
            formattedItems
        )
        formattedCategs = [category.format() for category in categories]
        if (len(paginatedItems) == 0):
            abort(404)
        else:
            return jsonify({
                "msg": "fetched items",
                "success": True,
                "data": {
                    "categories": formattedCategs,
                    "currentCategory": requestedCategStr,
                    "items": paginatedItems,
                    "totalItems": len(formattedItems)
                }
            }), 200

    @app.route("/api/stuff", methods=["POST"])
    def get_app_item():
        abort400IfNoField(["prevItems", "category"])
        requestCateg = request.get_json()["category"]
        item = None
        if requestCateg == "all":
            item = db.session.query(Item).filter(
                Item.id.not_in(request.get_json()["prevItems"])
            ).first()
        else:
            categ = Category.query.filter_by(
                type=requestCateg
            ).first()
            if categ is None:
                abort(404)
            item = db.session.query(Item).filter(
                Item.category == categ.id,
                Item.id.not_in(request.get_json()["prevItems"])
            ).first()
        if item is None:
            abort(400)
        return jsonify({
            "msg": "app item fetched",
            "success": True,
            "data": item.format()
        }), 200
