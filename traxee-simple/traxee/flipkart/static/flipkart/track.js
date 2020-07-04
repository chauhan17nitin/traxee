
function getCookieValue(a) {
    var b = document.cookie.match('(^|;)\\s*' + a + '\\s*=\\s*([^;]+)');
    return b ? b.pop() : '';
}



var trackForm = document.getElementById('slider_form');

trackForm.addEventListener('submit', function(){
	e.preventDefault();
	const product_id = trackForm['product_id'].value;
	const price_input = trackForm['price_input'].value;
	console.log(product_id);

	const request = new XMLHttpRequest();
	request.open('POST', '/add_trackapi/');

	const header =  "X-CSRFToken";
	const token = getCookieValue('csrftoken');
	request.setRequestHeader(header, token);

	const data = new FormData();
	data.append('product_id', product_id);
	data.append('price_input', price_input);
	request.send(data);
	button.innerHTML = "Adding... ";

	request.onload = () => {
		if (request.status == 403){
			alert('Aleardy on track');
			button.innerHTML = "On Track";}
		else if (request.status == 200) {
			button.innerHTML = "On Track";
		}
		else if (request.status) {
			alert('Login to your account first');
			window.location.replace('/login');}
}
});

