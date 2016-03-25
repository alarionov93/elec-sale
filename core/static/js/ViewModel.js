/**
 * Created by sanya on 17.03.16.
 */
;

function ViewModel() {
    var self = this;
    self.waiter = new Waiter();
    self.waiter.show();
    self.added = ko.observable(false);
    self.removed = ko.observable(false);
    self.msg = ko.observable("");
    self.products = ko.observableArray();
    self.products.loaded = ko.observable(false);
    self.shuffledProducts = ko.observableArray();
    self.productsToShow = ko.observableArray();
    self.cart = ko.observableArray();
    self.products.expanded = ko.observable(false);
    self.productToView = ko.observable(null);
    self.isViewing = ko.observable(false);
    self.order = ko.observable();
    self.orderCreated = ko.observable(false);
    self.orderPopupShown = ko.observable(false);
    self.customerPhone = ko.observable('');
    self.customerEmail = ko.observable('');
    self.firstShow = ko.observable(true);
    self.feedbackText = ko.observable('');
    self.feedbackFormShown = ko.observable(false);
    self.customerVoted = ko.observable(false);
    self.purchaseFormShown = ko.observable(false);
    self.positionNeeded = ko.observable('');
    self.showResponse = ko.observable(false);

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
    self.positionNeeded.isValid = ko.computed(function() {
        var e = self.positionNeeded();
        return !!e && typeof e !== "undefined"
        && e.length !== 0 && e.length < 500 && e.length > 2;
    });

    self.cart.total = ko.computed(function() {
        var total = 0;
        if (self.cart() !== undefined && self.cart().length > 0) {
            var products = self.cart();
            for (var i = 0; i < products.length; i++) {
                total += parseInt(products[i].price());
            }
        }
        return total;
    });

    $.get("/products/all/").then(function (resp) {
        products = JSON.parse(resp.products);
        console.log(products);
        images_dir = resp.images_dir;
        if(resp.length == 0) {
            // TODO: handle it?
        } else {
            self.products.removeAll();
            for (var i = 0; i < products.length; i++) {
                product = new Product(products[i].fields.id,
                                products[i].fields.name,
                                products[i].fields.desc,
                                products[i].fields.cost,
                                products[i].fields.in_stock, 
                                products[i].fields.left_in_stock,
                                products[i].fields.thumbs,
                                products[i].fields.images);
                self.products.push(product);
            }
            console.log(self.products());
            self.products.loaded(true);
            self.showInitProducts();
            self.updateCart();
        }
    }).always(self.waiter.hide);

    self.equals = function(obj, secObj) {
        var stat;
        for(var key in obj) {
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

        return true;
    }

    // self.duplicates = ko.observableArray();
    // self.findDuplicates = function(array) {
    //     var rem = [];
    //     for(var i = 0; i < array.length-1; i++) {
    //         for(var j = i; j < array.length; j++) {
    //             if(i != j) {
    //                 if(self.equals(array[i], array[j])) {
    //                     array[i].count(array[i].count() + 1);
    //                     self.cart.remove(array[j]);
    //                 }
    //             }
    //         }
    //     }
    //     return rem;
    // }

    self.shuffle = function(arr) {
        var newLength = 2;
        // for (var i = 0; i < newLength; i++) {
        //     var j = Math.floor(Math.random() * (i + 1));
        //     var temp = array[i];
        //     array[i] = array[j];
        //     array[j] = temp;
        // }
        for(var j, x, i = arr.length; i; j = parseInt(Math.random() * i), x = arr[--i], arr[i] = arr[j], arr[j] = x);
        self.shuffledProducts(arr.slice(0,3));
    }

    // for (var i in fields) {console.log(fields[i]);} // think how to implement it
    self.showInitProducts = function () {
        self.shuffle(self.products());
        self.productsToShow(self.shuffledProducts());
        self.products.expanded(false);
    };

    self.showAllProducts = function() {
        self.productsToShow(self.products());
        self.products.expanded(true);
    };

    self.products.find = function (id) {
        for (var i = 0; i < self.products().length; i++) {
            if (parseInt(id) == self.products()[i].id) {
                product = self.products()[i];
            }
        }

        return product;
    };

    self.cart.find = function (id) {
        for (var i = 0; i < self.cart().length; i++) {
            if (parseInt(id) == self.cart()[i].id) {
                product = self.cart()[i];
            }
        }

        return product;
    };

    self.updateCart = function() {
        if(self.products.loaded() == true && self.products().length > 0) {
            self.waiter.show();
            $.get("/cart/update/").then(function (resp) {
                console.log(resp.status);
                if (resp.status == 0) {
                    self.cart.removeAll();
                    for (var i = 0; i < resp.cart.length; i++) {
                        p = self.products.find(resp.cart[i].id); //find element in products
                        p.isInCart(true);
                        p.count(resp.cart[i].count); //++ its count
                        self.cart.push(p);
                        // if(resp.cart[i].count > 1) {
                        //     p = self.cart.find(resp.cart[i].id); //find element in cart
                        //     p.isInCart(true);
                        //     p.count(resp.cart[i].count); //++ its count
                        // } else {
                        //     p = self.products.find(resp.cart[i].id); //find element in products
                        //     p.isInCart(true);
                        //     p.count(resp.cart[i].count);
                        //     self.cart.push(p);
                        // }
                    }
                } else {
                    console.log("Error:" + resp.status);                    
                }
            }).always(self.waiter.hide);
        }
    };
    // addToCart should be invoked with .bind() !!
    self.addToCart = function(vm, evt, product) {
        self.waiter.show();
        var product = this;
        evt.stopPropagation();
        productId = parseInt(product.id);
        $.get("/cart/add/"+encodeURIComponent(productId)).then(function (resp) {
            console.log(resp.status);
            if (resp.status == 0) {
                self.cart.removeAll();
                for (var i = 0; i < resp.cart.length; i++) {
                    p = self.products.find(resp.cart[i].id); //find element in products
                    p.isInCart(true);
                    p.count(resp.cart[i].count); //++ its count
                    self.cart.push(p);
                    // p.leftInStock--;
                }
            } else {
                console.log("Error:" + resp.status);                    
            }
        }).always(self.waiter.hide);
    };

    self.deleteFromCart = function(productId) {
        return function() {
            self.waiter.show();
            $.get("/cart/delete/"+encodeURIComponent(productId)).then(function (resp) {
                // delete from productsInCart, if server deletes from session
                console.log(resp.status);
                if (resp.status == 0) {
                    var productToDelete = self.cart.find(productId);
                    var deleted = self.cart.remove(productToDelete);
                    // productToDelete.leftInStock++;
                    console.log(deleted);
                }
            }).always(self.waiter.hide);
        }
    };

    self.removeAllFromCart = function() {
        self.waiter.show();
        $.get("/cart/remove_all/").then(function (resp) {
            console.log(resp.status);
            if (resp.status == 0) {
                self.cart.removeAll();
            }
        }).always(self.waiter.hide);
    };

    self.showFeedbackForm = function() {
        return function () {
            self.firstShow(true);
            self.feedbackFormShown(true);
        }
    };

    self.hideFeedbackForm = function() {
        return function() {
            self.feedbackFormShown(false);
            self.showResponse(false);
        }
    };

    self.showPurchaseForm = function() {
        return function () {
            self.firstShow(true);
            self.purchaseFormShown(true);
        }
    };

    self.hidePurchaseForm = function() {
        return function() {
            self.purchaseFormShown(false);
            self.showResponse(false);
        }
    };

    self.showOrderPopup = function() {
        return function() {
            self.firstShow(true);
            self.orderPopupShown(true);
        }
    };

    self.hideOrderPopup = function() {
        return function() {
            self.orderPopupShown(false);
        }
    };

    // TODO: make waited after make order click!!
    self.makeOrder = function() {
        return function() {
            self.firstShow(false);
            if (self.customerPhone.isValid() && self.customerEmail.isValid()) {
                self.waiter.show();
                var token = $('input[name*=csrf]').val();
                $.post("/orders/create/", {
                    phone: self.customerPhone(),
                    email: self.customerEmail(),
                    total: self.cart.total(),
                    csrfmiddlewaretoken: token}).then(function (resp) {
                    // self.showResponse(true); // for form to be invisible, to show only msg or err!!
                    console.log(resp.status);
                    if (resp.status == 0) {
                        console.log(resp);
                        self.cart.removeAll();
                        var order = resp.order;
                        self.order(new Order(order.date, order.number, order.phone, order.email, order.items, order.total, resp.success));
                        self.orderCreated(true);
                        self.hideOrderPopup();
                    }
                }).always(self.waiter.hide);
            }
        }
    };

    self.sendFeedback = function() {
        return function() {
            self.firstShow(false);
            if (self.feedbackText.isValid() && self.customerEmail.isValid()) {
                self.waiter.show();
                var token = $('input[name*=csrf]').val();
                $.post("/feedback/", {
                    feedback: self.feedbackText(),
                    email: self.customerEmail(),
                    csrfmiddlewaretoken: token}).then(function (resp) {
                    self.showResponse(true); // for form to be invisible, to show only msg or err!!
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
                }).always(self.waiter.hide);
            }
        }
    };

    self.sendPurchase = function() {
        return function() {
            self.firstShow(false);
            if (self.positionNeeded.isValid() && self.customerEmail.isValid()) {
                self.waiter.show();
                var token = $('input[name*=csrf]').val();
                $.post("/purchase/", {
                    purchase: self.positionNeeded(),
                    email: self.customerEmail(),
                    csrfmiddlewaretoken: token}).then(function (resp) {
                    self.showResponse(true); // for form to be invisible, to show only msg or err!!
                    console.log(resp.status);
                    if (resp.status == 0) {
                        console.log(resp);
                        $("#msg").text(resp.success);
                        // self.hideFeedbackForm();
                        self.customerEmail('');
                        self.positionNeeded('');
                    } else {
                        $("p#err").append("Ошибка сервера, повторите попытку позже.")
                    }
                }).always(self.waiter.hide);
            }
        }
    };

    self.getProduct = function(productId, evt, vm) {
        return function () {
            var product = self.products.find(productId);
            self.productToView(product);
        }
    };

    self.viewingOff = function() {
        return function () {
            self.productToView(null);
        }
    };
}