import SyncManager from "./webclient/sync_manager.js";
import ChatRenderer from "./webclient/chat_renderer.js";
import ChatWatcher from "./webclient/chat_watcher.js";
import ChatSelector from "./webclient/chat_selector.js";
import Chat from "./webclient/chat.js";
import User from "./webclient/chat.js";
import api_call from "./webclient/api_call.js";
import { get_self_user_id } from "./webclient/profile.js";


var sync_manager;
var chat_renderer;
var chat_selector;
var user_id;

function setup()
{
	text_input.addEventListener("keyup", event => {
		if (event.key !== "Enter")
			return;
		enviar();
	});

	sync_manager = new SyncManager();
	chat_renderer = new ChatRenderer(message_area);
	chat_renderer.set_self_user_id(get_self_user_id());

	let chat_watcher = new ChatWatcher();
	chat_selector = new ChatSelector(chat_renderer, contacts_area, users_area);

	let chat_watcher_async_obj = sync_manager.add_async_obj(chat_watcher, 3000);
	chat_watcher_async_obj.after_hooks.push(chat_selector.check_new_chats.bind(chat_selector));
	chat_watcher_async_obj.force_now();
}

function enviar()
{
	let texto = text_input.value;
	// No enviar texto en blanco
	if (!texto || !texto.trim())
		return;
	text_input.value = "";

	var chat_id;
	if (chat_selector.selected_chat === undefined) {
		console.error("current_chat sin especificar");
		return;
	}
	else
		chat_id = chat_selector.selected_chat.id;

	let datos = Object();
	datos.chat_id = chat_id;
	datos.message_type = 1;
	datos.message_data = texto;

	api_call("/api/web/send_message", datos)
	.catch(error => {
		console.error("Error al enviar el mensaje", error);
	});
}

window.onload = setup;

