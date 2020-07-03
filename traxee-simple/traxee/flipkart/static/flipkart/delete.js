console.log('file attached');

function getCookieValue(a) {
    var b = document.cookie.match('(^|;)\\s*' + a + '\\s*=\\s*([^;]+)');
    return b ? b.pop() : '';
}

function reply_click(clicked_id){
  const button = document.getElementById(clicked_id);
  button.innerHTML = "Deleting...";
  const request = new XMLHttpRequest();
  request.open('POST', '/remove_trackapi/');

  const header =  "X-CSRFToken";
  const token = getCookieValue('csrftoken');
  request.setRequestHeader(header, token);

  const data = new FormData();
  data.append('product_id', clicked_id);
  request.send(data);
  console.log('request sent');

  request.onload = () => {
    console.log(request.status);
    if (request.status == 200){
      window.location.replace('/flipkart/track');
    } else {
      alert('may encountered a server error');
    }
  }
}
