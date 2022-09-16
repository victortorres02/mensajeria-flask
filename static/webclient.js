
chat_id = 1;
chat_position = 0;

function setup()
{
	textinput = document.getElementById("textinput");
	message_area = document.getElementById("message_area");
	textinput.addEventListener("keyup", event => {
		if (event.key !== "Enter")
			return;
		enviar();
	});
	init_sync();
}

function enviar()
{
	texto = textinput.value;
	textinput.value = "";
	datos = Object();
	datos.chat_id = chat_id;
	datos.payload = texto;
	const xhttp = new XMLHttpRequest();
	//xhttp.onload = function(){console.log(this)};
	xhttp.open("POST", "/api/web/post_msg");
	xhttp.setRequestHeader("Content-Type", "application/json");
	xhttp.send(JSON.stringify(datos));
}


function sync(resolve, reject)
{
	const xhttp = new XMLHttpRequest();
	xhttp.onload = http => {
		request = http.target;
		//console.log(request);
		if (request.status == 200)
		{
			console.log(request.responseText);
			response = JSON.parse(request.responseText);
			console.log("syncing", response.messages.length, "messages");
			//console.log(resolve);
			resolve(response);
			return;
		}
		reject();
	};
	xhttp.ontimeout = () => {
		console.log("sync request timed out");
		reject();
	}
	xhttp.timeout = 7000;
	xhttp.open("GET",
		"/api/web/get_msgs?chat_id=" + chat_id +
		"&position=" + chat_position +
		"&max_messages=40");
	xhttp.send();
}


function init_sync()
{
	let sync_promise = new Promise(sync);
	return sync_promise.then(
		value => {
			if (value.messages.length == 0)
			{
				setTimeout(init_sync, 250);
			}
			else
			{
				add_chat_messages(value);
				return init_sync();
			}
		}, error => {
			console.log("Error syncing:", error);
			setTimeout(init_sync, 2000);
		});
}

function add_chat_messages(messages)
{
	msgs = messages.messages;
	for (var i = 0; i < msgs.length; i++)
	{
		add_chat_msg(msgs[i]);
	}
}

function add_chat_msg(message)
{
	chat_position = message.position;
	let elem = document.createElement("p");
	elem.appendChild(document.createTextNode(message.payload));
	message_area.appendChild(elem);
}


window.onload = setup;


