window.onload = function() {

	elm = document.getElementById("title");
	title = elm.innerHTML;
	len = title.trim().length;
	
	if (len > 9) elm.style.fontSize = 17;
	if (len > 10) elm.style.fontSize = 16;
	if (len > 12) elm.style.fontSize = 15;

}

