





function addToCart(productId,quantity) {
  console.log("este es el id del producto: ", productId)

  console.log("la cantidad es : ", quantity)

  fetch(`/carro/agregar/${productId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ product_id: productId, quantity: quantity })
  })
  .then(response => {
    if (response.ok) {
      return response.json();
    } else {
      throw new Error('Error al agregar el producto al carrito');
    }
  })


}

function getCookie(name) {
  // Función auxiliar para obtener el valor de la cookie CSRF
  const cookieValue = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return cookieValue ? cookieValue.pop() : '';
}


