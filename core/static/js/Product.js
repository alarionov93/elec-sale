/**
 * Created by sanya on 17.03.16.
 */

function Product(id, name, cost, inStock, thumbs, images) {
	this.id = id;
    this.name = name;
    this.cost = cost;
    this.inStock = inStock;
    this.thumbs = thumbs;
    this.images = images;
}

function Order(date, number, phone, email, products, total, msg) {
    this.date = date;
    this.number = number;
    this.phone = phone;
    this.email = email;
    this.products = products;
    this.total = total;
    this.success = msg;
}