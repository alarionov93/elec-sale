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
    self.feedbackText = ko.observable('');
    self.feedbackFormShown = ko.observable(false);
    self.customerVoted = ko.observable(false);

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
    self.feedbackText.isValid = ko.computed(function() {
        var e = self.feedbackText();
        return !!e && typeof e !== "undefined"
        && e.length !== 0 && e.length < 500 && e.length > 2;
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

    self.equals = function(obj, secObj) {
        var stat;
        for(var key in obj) {
            // if(obj.hasOwnProperty(key) && secObj.hasOwnProperty(key)) {
            //     if (typeof obj[key] == "object" && typeof secObj[key] == "object") {
            //         stat = self.equals(obj[key], secObj[key]);
            //     } else if (typeof obj[key] == "function" && typeof secObj[key] == "function") {
            //         stat = (obj[key]() == secObj[key]());
            //     } else if(secObj[key] != obj[key]) {
            //         return false;
            //     } else if(key == "count") {
            //         continue;
            //     }
            // }
            if (key == "id") {
                if(obj.hasOwnProperty(key) && secObj.hasOwnProperty(key)) {
                    if(secObj[key] != obj[key]) {
                        return false;
                    }
                }
            } else {
                continue;
            }
        }
        // if(stat == false) {
        //     return false;
        // }

        return true;
    }
    self.duplicates = ko.observableArray();
    self.findDuplicates = function(array) {
        var rem = [];
        for(var i = 0; i < array.length-1; i++) {
            for(var j = i; j < array.length; j++) {
                if(i != j) {
                    if(self.equals(array[i], array[j])) {
                        array[i].count(array[i].count() + 1);
                        // rem.push(j);
                        self.cart.remove(array[j]);
                    }
                }
            }
        }
        return rem;
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

    self.showFeedbackForm = function() {
        return function () {
            self.feedbackFormShown(true);
        }
    };

    self.hideFeedbackForm = function() {
        return function() {
            self.feedbackFormShown(false);
        }
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
                    feedback: self.feedbackText(),
                    email: self.customerEmail(),
                    csrfmiddlewaretoken: token}).then(function (resp) {
                    console.log(resp.status);
                    if (resp.status == 0) {
                        console.log(resp);
                        $("#msg").text(resp.success);
                        // self.hideFeedbackForm();
                        self.customerEmail('');
                        self.feedbackText('');
                        self.customerVoted(true);
                    } else if (resp.status == 3) {
                        $("#msg").text(resp.success);
                        self.customerEmail('');
                        self.feedbackText('');
                        self.customerVoted(true);
                    } else {
                        $("p#err").append("Ошибка сервера, повторите попытку позже.")
                    }
                }).always();
            }
        }
    };
}