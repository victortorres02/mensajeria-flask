import SyncManager from "./webclient/sync_manager.js";
import ChatRenderer from "./webclient/chat_renderer.js";
import Chat from "./webclient/chat.js";


var sync_manager;
var chat_renderer;

function setup()
{
	text_input = document.getElementById("text_input");
	message_area = document.getElementById("message_area");

	text_input.addEventListener("keyup", event => {
		if (event.key !== "Enter")
			return;
		enviar();
	});

	sync_manager = new SyncManager();
	chat_renderer = new ChatRenderer(message_area);

	let chat_watcher = new ChatWatcher();
	let chat_selector = new ChatSelector(chat_watcher, chat_renderer, );
	sync_manager.add_async_obj(chat_watcher);
}

function enviar()
{
	let texto = text_input.value;
	// No enviar texto en blanco
	if (!texto || !texto.trim())
		return;
	text_input.value = "";

	var chat_id;
	if (chat_renderer.current_chat === undefined) {
		console.error("current_chat sin especificar");
		return;
	}
	else
		chat_id = chat_renderer.current_chat.id;

	let datos = Object();
	datos.chat_id = chat_id;
	datos.message_type = 1;
	datos.message_data = texto;

	fetch("/api/web/send_message", {
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

window.onload = setup;

