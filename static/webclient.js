
chat_id = 1;
chat_position = 0;

function setup()
{
	text_input = document.getElementById("text_input");
	message_area = document.getElementById("message_area");

	text_input.addEventListener("keyup", event => {
		if (event.key !== "Enter")
			return;
		enviar();
	});

	init_sync();
}

function enviar()
{
	texto = text_input.value;
	text_input.value = "";

	datos = Object();
	datos.chat_id = chat_id;
	datos.payload = texto;

	fetch("/api/web/post_msg", {
		method: 'POST',
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(datos)
	})
	.catch(error => {
		console.error("Error al enviar el mensaje", error);
	});
}


function get_messages()
{
	return fetch(
		"/api/web/get_msgs?chat_id=" + chat_id +
		"&position=" + chat_position +
		"&max_messages=40")
	.then(response => {
		if (!response.ok)
			throw new Error("Servidor regresó un error");
		return response;
	})
	.then(response => response.json());
}


function init_sync()
{
	return get_messages().then(
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
			console.error("Error al sincronizar:", error);
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
	elem.classList.add("text-message");
	elem.classList.add("px-2");
	elem.appendChild(document.createTextNode(message.payload));
	message_area.appendChild(elem);
}


window.onload = setup;


