console.log('file connected search.js');

function getCookieValue(a) {
    var b = document.cookie.match('(^|;)\\s*' + a + '\\s*=\\s*([^;]+)');
    return b ? b.pop() : '';
}

function reply_click(clicked_id){
  const button = document.getElementById(clicked_id);
  button.innerHTML = "Adding... ";
  const request = new XMLHttpRequest();
  request.open('POST', '/add_trackapi/');

  const header =  "X-CSRFToken";
  const token = getCookieValue('csrftoken');
  request.setRequestHeader(header, token);

  const data = new FormData();
  data.append('product_id', clicked_id);
  request.send(data);
  console.log('request sent');

  request.onload = () => {
    if (request.status == 403){
      alert('Aleardy on track');
      button.innerHTML = "On Track";
    } else if (request.status == 200) {
      button.innerHTML = "On Track";
    } else if (request.status) {
      alert('Login to your account first');
      window.location.replace('/login');
    }
  }

}
