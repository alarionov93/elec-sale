;

    VM.getProduct = function(productId) {
        $.get("/products/"+encodeURIComponent(productId)).then(function (resp) {
            console.log(resp.status);
            if (resp.status == 0) {
                product = new Product(product.fields.id, product.fields.name, 
                                product.fields.cost, product.fields.in_stock, 
                                product.fields.thumbs, product.fields.images);
                console.log(product);
            }
        }).always();
    }