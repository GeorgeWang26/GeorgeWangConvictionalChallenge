import requests
import json
from flask import Flask, Response, jsonify

app = Flask(__name__)

URL = "https://my-json-server.typicode.com/convictional/engineering-interview-api/products"


# get_product(id, raw_products) consumes a product id and a json object of raw_products. If the product
# with matching id exists in raw_products, it returns that product in json format as requried in schema, 
# if the id does not exist, it returns False.
def get_product(id, raw_products):
    for raw_product in raw_products:
        if id == raw_product["id"]:
            product = {}
            product["code"] = raw_product["id"]
            product["title"] = raw_product["title"]
            product["vendor"] = raw_product["vendor"]
            product["bodyHtml"] = raw_product["body_html"]
            product["variants"] = []
            product["images"] = []
            for raw_variant in raw_product["variants"]:
                variant = {}
                variant["id"] = raw_variant["id"]
                variant["title"] = raw_variant["title"]
                variant["sku"] = raw_variant["sku"]
                quantity = 0
                if "inventory_quantity" in raw_variant:
                    # negative inventory_quantity in raw data should be adjusted to 0
                    quantity = max(0, raw_variant["inventory_quantity"])
                variant["available"] = quantity > 0
                variant["inventory_quantity"] = quantity
                variant["weight"] = {"value": raw_variant["weight"], "unit": raw_variant["weight_unit"]}
                product["variants"].append(variant)
                for raw_image in raw_variant["images"]:
                    image = {"source": raw_image["src"], "variantId": raw_variant["id"]}
                    product["images"].append(image)
            return product
    return False


# get_products(raw_products) consumes a json object of raw_products. It returns all products in json
# format as requried in schema.
def get_products(raw_products):
    products = []
    for product in raw_products:
        id = product["id"]
        products.append(get_product(id, [product]))
    return products


# get_inventory(raw_products) consumes a json object of raw_products. It returns the product inventory 
# in json format as requreid in schema.
def get_inventory(raw_products):
    inventory = []
    for raw_product in raw_products:
        product_id = raw_product["id"]
        for raw_variant in raw_product["variants"]:
            variant_id = raw_variant["id"]
            quantity = 0
            if "inventory_quantity" in raw_variant:
                # negative inventory_quantity in raw data should be adjusted to 0
                quantity = max(0, raw_variant["inventory_quantity"])
            variant_inventory = {"productId": product_id, "variantId": variant_id, "stock": quantity}
            inventory.append(variant_inventory)
    return inventory


# handles error 404
@app.errorhandler(404)
def page_not_found(e):
    return Response(response = json.dumps({"message": "Product not found"}, indent = 4),
                    status = 404,
                    mimetype = "application/json")


# returns all products in json format as requried in schema.
@app.route("/products", methods = ["GET"])
def get_all_products():
    response = requests.get(URL)
    products_data = json.loads(response.text)
    products = get_products(products_data)
    return jsonify(products)


# returns product with specified id in json format as requried in schema. If product with given id is 
# not present, returns error 400.
@app.route("/product/<int:product_id>", methods = ["GET"])
def get_peoduct_by_id(product_id):
    response = requests.get(URL)
    products_data = json.loads(response.text)
    product = get_product(product_id, products_data)
    if product:
        return jsonify(product)
    else:
        return Response(response = json.dumps({"message": "Invalid ID supplied"}, indent = 4), 
                        status = 400, 
                        mimetype = "application/json")


# returns the product inventory in json format as requreid in schema.
@app.route("/store/inventory", methods = ["GET"])
def get_store_inventory():
    response = requests.get(URL)
    products_data = json.loads(response.text)
    inventory = get_inventory(products_data)
    return jsonify(inventory)


app.run(host = "0.0.0.0", port = 5000, debug = True)