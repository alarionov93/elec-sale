/**
 * Created by sanya on 17.03.16.
 */
;

function Product(id, name, cost, inStock, thumbs, images, isInCart, inCart) {
	var self = this;
	this.id = id;
    this.name = name;
    this.cost = cost;
    this.inStock = inStock;
    this.thumbs = thumbs;
    this.images = images;

    if(isInCart) {
    	this.isInCart = ko.observable(true);
    } else {
    	this.isInCart = ko.observable(false);
    }

    this.count = ko.observable(inCart);
    this.pureCount = inCart;
    this.count.subscribe(function(value) {
	    this.pureCount = value;
	});
	this.price = ko.computed(function() {
    	if(self.count() > 1) {
    		return self.cost * self.count();
    	}
    	
    	return self.cost;
    });
}

function Order(date, number, phone, email, products, total, msg) {
    this.date = date;
    this.number = number;
    this.phone = phone;
    this.email = email;
    this.items = products;
    this.total = total;
    this.success = msg;
}