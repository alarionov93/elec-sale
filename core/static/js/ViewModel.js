/**
 * Created by sanya on 17.03.16.
 */


function ViewModel() {
    var self = this;
    self.added = ko.observable(false);
    self.removed = ko.observable(false);
    self.msg = ko.observable("");
    self.products = ko.observableArray();
    self.cart = ko.observableArray();
    self.products.expanded = ko.observable(false);
    self.order = ko.observable();
    self.orderCreated = ko.observable(false);
    self.orderPopupShown = ko.observable(false);
    self.customerPhone = ko.observable('');
    self.customerEmail = ko.observable('');
    self.firstShow = ko.observable(true);
    self.fedbackText = ko.observable('');

    self.customerPhone.isValid = ko.computed(function() {
        var p = self.customerPhone();
        return !!p && typeof p !== "undefined"
        && p.length !== 0 && p.length > 6 && p.match(/\D/i) == null;
    });
    self.customerEmail.isValid = ko.computed(function() {
        var e = self.customerEmail();
        return !!e && typeof e !== "undefined"
        && e.length !== 0 && e.includes("@");
    });
    self.fedbackText.isValid = ko.computed(function() {
        var e = self.customerEmail();
        return !!e && typeof e !== "undefined"
        && e.length !== 0;
    });

    // self.emailError = ko.computed(function() {
    //     return !!self.customerEmail.isValid();
    // });
    // self.phoneError = ko.computed(function() {
    //     return !!self.customerPhone.isValid();
    // });

    self.cart.total = ko.computed(function() {
        var total = 0;
        if (self.cart() !== undefined && self.cart().length > 0) {
            var products = self.cart();
            for (var i = 0; i < products.length; i++) {
                total += parseInt(products[i].cost);
            }
        }
        return total;
    });
    self.init = function () {
        self.getInitProducts();
        self.updateCart();
    }

    self.cart.removeDouble = function() {
        for (var i = 0; i < self.cart().length; i++) {
            if (self.cart()[i].inCart() > 1) {
                // self.cart.remove(self.cart()[i]);
            }
        }
    };
    self.hasDuplicates = function(array) {
        var valuesSoFar = [];
        for (var i = 0; i < array.length; ++i) {
            var value = array[i];
            if (valuesSoFar.indexOf(value) !== -1) {
                return true;
            }
            valuesSoFar.push(value);
        }
        return false;
    }

    // for (var i in fields) {console.log(fields[i]);} // think how to implement it
    self.getInitProducts = function () {
        $.get("/products/").then(function (resp) {
            products = JSON.parse(resp.products);
            console.log(products);
            images_dir = resp.images_dir;
            if(resp.length == 0) {
                // TODO: handle it?
            } else {
                self.products.removeAll();
                for (var i = 0; i < products.length; i++) {
                    product = new Product(products[i].fields.id, products[i].fields.name, 
                                        products[i].fields.cost, products[i].fields.in_stock, 
                                        products[i].fields.thumbs, products[i].fields.images);
                    self.products.push(product);
                }
                console.log(self.products());
            }
        }).always();
        self.products.expanded(false);
    }

    self.getAllProducts = function() {
        return function() {
            $.get("/products/all/").then(function (resp) {
                products = JSON.parse(resp.products);
                console.log(products);
                images_dir = resp.images_dir;
                if(resp.length == 0) {
                    // TODO: handle it?
                } else {
                    self.products.removeAll();
                    for (var i = 0; i < products.length; i++) {
                        product = new Product(products[i].fields.id, products[i].fields.name, 
                                        products[i].fields.cost, products[i].fields.in_stock, 
                                        products[i].fields.thumbs, products[i].fields.images);
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
            var products = resp;
            if(resp.length == 0) { // TODO: change error handling logic here!
                // TODO: handle it?
            } else {
                self.cart.removeAll();
                for (var i = 0; i < products.length; i++) {
                        product = new Product(products[i].fields.id, products[i].fields.name, 
                                        products[i].fields.cost, products[i].fields.in_stock, 
                                        products[i].fields.thumbs, products[i].fields.images,
                                        true);
                        self.cart.push(product);
                    }
                console.log(self.cart());
            }
        }).always();
    };

    self.addToCart = function(productId) {
        return function() {
            productId = parseInt(productId);
            $.get("/cart/add/"+encodeURIComponent(productId)).then(function (resp) {
                console.log(resp.status);
                if (resp.status == 0) {
                    for (var i = 0; i < self.products().length; i++) {
                        if (self.products()[i].id == productId) {
                            productToPush = self.products()[i];
                            self.cart.push(productToPush);
                            self.products()[i].isInCart(true);
                        }
                    }
                } else {
                    console.log("Error:" + resp.status);                    
                }
            }).always();
        }
    };

    self.deleteFromCart = function(itemId) {
        return function() {
            $.get("/cart/delete/"+encodeURIComponent(itemId)).then(function (resp) {
                // delete from productsInCart, if server deletes from session
                console.log(resp.status);
                if (resp.status == 0) {
                    console.log(self.cart());
                    var deleted = self.cart.splice(itemId, 1);
                    console.log(deleted);
                }
            }).always();
        }
    };

    self.removeAllFromCart = function() {
        $.get("/cart/remove_all/").then(function (resp) {
            console.log(resp.status);
            if (resp.status == 0) {
                self.cart.removeAll();
            }
        }).always();
    };

    self.showMsg = function(msg, blockId) {
        $(blockId).text(msg);
        $(blockId).show();
    };

    self.hideMsg = function() {
        $(blockId).hide();
    }

    self.showOrderPopup = function() {
        return function() {
            self.orderPopupShown(true);
        }
    }

    self.hideOrderPopup = function() {
        return function() {
            self.orderPopupShown(false);
        }
    }

    self.makeOrder = function() {
        return function() {
            self.firstShow(false);
            if (self.customerPhone.isValid() && self.customerEmail.isValid()) {
                var token = $('input[name*=csrf]').val();
                $.post("/orders/create/", {
                    phone: self.customerPhone(),
                    email: self.customerEmail(),
                    total: self.cart.total(),
                    csrfmiddlewaretoken: token}).then(function (resp) {
                    console.log(resp.status);
                    if (resp.status == 0) {
                        console.log(resp);
                        self.cart.removeAll();
                        var order = resp.order;
                        self.order(new Order(order.date, order.number, order.phone, order.email, order.products, order.total, resp.success));
                        self.orderCreated(true);
                        self.hideOrderPopup();
                    }
                }).always();
            }
        }
    };

    self.sendFeedback = function() {
        return function() {
            self.firstShow(false);
            if (self.feedbackText.isValid() && self.customerEmail.isValid()) {
                var token = $('input[name*=csrf]').val();
                $.post("/feedback/", {
                    text: self.fedbackText(),
                    email: self.customerEmail(),
                    csrfmiddlewaretoken: token}).then(function (resp) {
                    console.log(resp.status);
                    if (resp.status == 0) {
                        console.log(resp);
                        self.hideFeedbackPopup();
                    }
                }).always();
            }
        }
    };
}