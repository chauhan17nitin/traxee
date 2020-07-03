function reply_click(){
	var x = document.getElementById("slider_form").submit();
	const button = document.getElementById("slider_button");
	const request = new XMLHttpRequest();
	request.open('POST', '/add_trackapi/');
	
	button.innerHTML = "Adding... ";
	console.log(x)
	
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


}


function r_click(product_id){

	const button = document.getElementById("slider_button");
	button.innerHTML = "Adding... ";
	const request = new XMLHttpRequest();
	request.open('POST', '/add_trackapi/');

	const header =  "X-CSRFToken";
	const token = getCookieValue('csrftoken');
	request.setRequestHeader(header, token);

	const data = new FormData();
	data.append('product_id', product_id);
	request.send(data);
	console.log(product_id);

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

}
