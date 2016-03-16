/**
 * Created by sanya on 17.03.16.
 */


function ViewModel() {
    var self = this;
    self.added = ko.observable(false);
    self.removed = ko.observable(false);
    self.msg = ko.observable("");
    self.productsInCart = ko.observableArray();
    self.products = ko.observableArray();
    self.products.expanded = ko.observable(false);
    self.init = function () {
        self.getInitProducts();
        // self.updateCart();
    }

    // for (var i in fields) {console.log(fields[i]);} // think how to implement it
    self.getInitProducts = function () {
        $.get("products/").then(function (resp) {
            products = JSON.parse(resp.products);
            console.log(products);
            images_dir = resp.images_dir;
            if(resp.length == 0) {
                // TODO: handle it?
            } else {
                self.products.removeAll();
                for (var i = 0; i < products.length; i++) {
                    product = new Product(products[i].fields.id, products[i].fields.name, products[i].fields.cost, products[i].fields.in_stock, products[i].fields.thumbs, products[i].fields.images);
                    self.products.push(product);
                }
                console.log(self.products());
            }
        }).always();
        self.products.expanded(false);
    }

    self.getAllProducts = function() {
        return function() {
            $.get("products/all/").then(function (resp) {
                products = JSON.parse(resp.products);
                console.log(products);
                images_dir = resp.images_dir;
                if(resp.length == 0) {
                    // TODO: handle it?
                } else {
                    self.products.removeAll();
                    for (var i = 0; i < products.length; i++) {
                        product = new Product(products[i].fields.id, products[i].fields.name, products[i].fields.cost, products[i].fields.in_stock, products[i].fields.thumbs, products[i].fields.images);
                        self.products.push(product);
                    }
                    console.log(self.products());
                }
            }).always();
            self.products.expanded(true);
        }
    }

    self.updateCart = function() {
        $.get("/cart/update/").then(function (resp) {
            console.log(resp);
            if(resp.length == 0) {
                // TODO: handle it?
            } else {
                self.productsInCart.removeAll();
                self.productsInCart(resp);
                var products = self.productsInCart();
                console.log(products);
            }
        }).always();
    };

    self.deleteFromCart = function(item_id) {
        return function() {
            $.get("/cart/delete/"+encodeURIComponent(item_id)).then(function (resp) {
                // delete from productsInCart, if server deletes from session
                console.log(resp.status);
                if (resp.status == 0) {
                    self.productsInCart.pop(item_id);
                }
            }).always();
        }
    };

    self.addToCart = function(product_id) {
        return function() {
            $.get("/cart/add/"+encodeURIComponent(product_id)).then(function (resp) {
                console.log(resp.status);
                self.updateCart();
            }).always();
        }
    };

    self.removeAllFromCart = function() {
        $.get("/cart/remove_all/").then(function (resp) {
            console.log(resp.status);
            if (resp.status == 0) {
                self.productsInCart.removeAll();
            }
        }).always();
    };
}