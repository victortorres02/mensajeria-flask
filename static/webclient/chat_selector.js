import Chat from "./chat.js";

export default class ChatSelector {
	constructor(renderer, contacts_area, users_area) {
		this.renderer = renderer;
		this.contacts_area = contacts_area;
		this.users_area = users_area;
		this.rendered_chats = new Map();
		this.selected_chat = undefined;
	}
	check_new_chats(async_obj) {
		let watcher = async_obj.obj;
		let new_chats = watcher.listed_chats.filter(
			chat => Array.from(this.rendered_chats.keys()).filter(ch => ch.id == chat.id).length == 0);
		if (new_chats.length == 0)
			return;
		console.log("Nuevos chats a mostrar", new_chats);

		let sync_manager = async_obj.sync_manager;
		new_chats.forEach(ch => {
			let chat = new Chat(ch.id);
			this.render_chat(chat, sync_manager);

			let async_obj = sync_manager.add_chat(chat);
			async_obj.sync_period = 1000;
		});
	}
	render_chat(chat, sync_manager) {
		let elem = document.createElement("div");
		elem.classList.add("my_contact_cont");

		let img_div = document.createElement("div");
		img_div.classList.add("my_contact_img");

		let contact_img = document.createElement("img");
		contact_img.src = "/static/penguin.png";

		let contact_name = document.createElement("h6");
		contact_name.classList.add("contact_name");
		contact_name.appendChild(document.createTextNode("contacto"));

		img_div.appendChild(contact_img);
		elem.appendChild(img_div);
		elem.appendChild(contact_name);

		elem.onclick = this.chat_click_callback.bind(this, elem, chat, sync_manager);
		this.contacts_area.appendChild(elem);
		this.rendered_chats.set(chat, elem);
	}
	chat_click_callback(elem, chat, sync_manager) {
		this.set_selected_chat(chat, sync_manager);
	}
	set_selected_chat(chat, sync_manager) {
		this.renderer.clear();

		let selected_async_obj = sync_manager.get_async_obj(this.selected_chat);

		if (selected_async_obj !== undefined) {
			let render_callbacks = selected_async_obj.after_hooks.filter(hook => {console.log("T:", hook.name, hook); return hook.name == "bound check_chat_update";});
			if (render_callbacks.length != 0) {
				console.log("CB", render_callbacks);
				let index = selected_async_obj.after_hooks.indexOf(render_callbacks[0]);
				selected_async_obj.after_hooks.splice(index, 1);
			}
		}

		console.log("Chat seleccionado:", chat);
		this.selected_chat = chat;

		let chat_async_obj = sync_manager.get_async_obj(chat);
		chat_async_obj.after_hooks.push(this.renderer.check_chat_update.bind(this.renderer));
		chat_async_obj.force_now();
	}
}

