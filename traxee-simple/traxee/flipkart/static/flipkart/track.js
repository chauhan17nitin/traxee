console.log('connected file track.js and improved')
function getCookieValue(a) {
    var b = document.cookie.match('(^|;)\\s*' + a + '\\s*=\\s*([^;]+)');
    return b ? b.pop() : '';
}

const trackForm = document.querySelector('.slider_form');

trackForm.addEventListener('submit', (e) => {
	e.preventDefault();
	const product_id = trackForm['product_id'].value;
	const price_input = trackForm['price_input'].value;
  
	console.log(product_id);
  console.log(price_input);

	const request = new XMLHttpRequest();
	request.open('POST', '/add_trackapi/');

	const header =  "X-CSRFToken";
	const token = getCookieValue('csrftoken');
	request.setRequestHeader(header, token);

	const data = new FormData();
	data.append('product_id', product_id);
	data.append('price_input', price_input);
	request.send(data);


	request.onload = () => {
		if (request.status == 403){
			alert('Aleardy on track');

    } else if (request.status == 200) {

		}
		else if (request.status) {
			alert('Login to your account first');
			window.location.replace('/login');}
}
});
