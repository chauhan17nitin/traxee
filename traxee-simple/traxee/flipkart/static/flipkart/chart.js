console.log('file connected');

function getCookieValue(a) {
    var b = document.cookie.match('(^|;)\\s*' + a + '\\s*=\\s*([^;]+)');
    return b ? b.pop() : '';
}

function get_chart(clicked_id){
	const button = document.getElementById(clicked_id);
	
	const request = new XMLHttpRequest();
	request.open('POST', '/brief_history/');

	const header =  "X-CSRFToken";
	const token = getCookieValue('csrftoken');
	request.setRequestHeader(header, token);
	
	const id = new FormData();
	id.append('product_id', clicked_id);
	request.send(id);
  	console.log('request sent');
	
	request.onload = () => {
		
		const res = JSON.parse(request.response);
		console.log(typeof res);
		//graph
		const history = JSON.parse(res.history_json);
		console.log(typeof history);
		var labels = [], data = [];
		Object.keys(history).forEach((key, index) => {
			console.log(history[key])
			var time = new Date(key*1000).toLocaleDateString();
			labels.push(time);
			console.log(history[key].current_price.amount);
			data.push(history[key].current_price.amount);
		} )
		console.log(labels);
		console.log(data);
		var ctx = document.getElementById('myChart');
		var myChart = new Chart(ctx, {
			type: 'line',
			data: {
				labels: labels,
				datasets: [{
					label: 'cost price',
					data: data,
					backgroundColor: [
						'rgba(255, 206, 86, 0.2)',
					],
					borderColor: [
						'rgba(209, 10, 10, 1)',
					],
					borderWidth: 1
				}]
			},
			options: {
				scales: {
					yAxes: [{
						ticks: {
							beginAtZero: true
						}
					}]
				}
			}
		});

		//slider
		var max_price = data[data.length-1];
		$("#slider").slider({
			range: "min",
			value: 1,
			step: 10,
			min: 0,
			max: max_price,
			slide: function( event, ui ) {
				$( "#price_input" ).val(ui.value );
			}
		});


		$("#price_input").change(function () {
			var value = this.value;
			value = Math.min(value, max_price)
			console.log(value);
			$("#price_input").val(value)
			$("#slider").slider("value", parseInt(value));
		});



		$("#slider_form input").not("#slider_button").keydown(function(event) {
			if (event.keyCode == 13) {
			  event.preventDefault();
			  return false;
			}
		});


	}
}
