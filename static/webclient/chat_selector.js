import Chat, { ChatType } from "./chat.js";
import User from "./user.js";
import api_call from "./api_call.js";

export default class ChatSelector {
	constructor(renderer, contacts_area, users_area) {
		this.renderer = renderer;
		this.contacts_area = contacts_area;
		this.users_area = users_area;
		this.rendered_chats = new Map();
		this.rendered_contacts = new Map();
		this.selected_chat = undefined;
	}
	set_self_user_id(user_id) {
		if (user_id.then === undefined)
			this.user_id = user_id;
		else
			user_id.then(id => {this.user_id = id;});
	}
	check_new_contacts(async_obj) {
		let watcher = async_obj.obj;
		let chats_personales = Array.from(this.rendered_chats.keys()).filter(
			chat => chat.type == ChatType.personal);
		let new_contacts = watcher.contacts.filter(
			contact => Array.from(this.rendered_contacts.keys()).filter(cont => cont.id == contact.id).length == 0)
			.filter(
				contact => chats_personales.filter(chat => chat.members.filter(member => member.id == contact.id).length != 0).length == 0);
		if (new_contacts.length == 0)
			return;
		console.log("Nuevos contactos a mostrar", new_contacts);

		let sync_manager = async_obj.sync_manager;
		new_contacts.forEach(cont => {
			let user = new User(cont.id, cont.username);
			this.render_contact(user, sync_manager);
		});
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
			let chat = new Chat(ch.id, ch.name, ch.type, ch.members);
			if (this.user_id !== undefined)
				chat.set_self_user_id(this.user_id);
			this.render_chat(chat, sync_manager);

			// Eliminacion del div del contacto
			if (chat.type == ChatType.personal && this.user_id !== undefined)
			{
				let contacto = chat.members.filter(member => member.id != this.user_id)[0];
				let contacto_personal = Array.from(this.rendered_contacts.keys()).filter(
					cont => cont.id == contacto.id);
				if (contacto_personal.length > 0)
				{
					if (contacto_personal > 1)
						console.warn("Mas de un div para el contacto", contacto, contacto_personal);
					contacto_personal.forEach(cont => {
						console.log("Eliminando div de contacto", cont.username);
						let elem = this.rendered_contacts.get(cont);
						this.users_area.removeChild(elem);
						this.rendered_contacts.delete(cont);
					});
				}
			}

			let async_obj = sync_manager.add_chat(chat);
			async_obj.sync_period = 1000;

			if (chat.id == this.target_chat_id)
			{
				this.set_selected_chat(chat, sync_manager);
				this.target_chat_id = undefined;
			}
		});
	}
	render_contact(user, sync_manager) {
		let elem = document.createElement("div");
		elem.classList.add("my_contact_cont");

		let img_div = document.createElement("div");
		img_div.classList.add("my_contact_img");

		let contact_img = document.createElement("img");
		contact_img.src = "/static/penguin.png";

		let contact_name = document.createElement("h6");
		contact_name.classList.add("contact_name");
		contact_name.appendChild(document.createTextNode(user.username));

		img_div.appendChild(contact_img);
		elem.appendChild(img_div);
		elem.appendChild(contact_name);

		elem.onclick = this.contact_click_callback.bind(this, elem, user, sync_manager);
		this.users_area.appendChild(elem);
		this.rendered_contacts.set(user, elem);
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
		contact_name.appendChild(document.createTextNode(chat.get_name()));

		img_div.appendChild(contact_img);
		elem.appendChild(img_div);
		elem.appendChild(contact_name);

		elem.onclick = this.chat_click_callback.bind(this, elem, chat, sync_manager);
		this.contacts_area.appendChild(elem);
		this.rendered_chats.set(chat, elem);
	}
	contact_click_callback(elem, contact, sync_manager) {
		let api_args = Object();
		api_args.user_id = contact.id;
		api_args.chat_type = ChatType.personal;

		return api_call("/api/web/create_chat", api_args)
		.then(json_res => {
			let chat_id = json_res.id;

			// Checar si el chat ya fue sincronizado
			let chat_personal = Array.from(this.rendered_chats.keys()).filter(
				chat => chat.id == chat_id);
			if (chat_personal.length > 0)
			{
				this.set_selected_chat(chat_personal[0], sync_manager);
			}
			else
			{
				this.target_chat_id = chat_id;
			}
			// contact => chats_personales.filter(chat => chat.members.filter(member => member.id == contact.id).length != 0).length == 0);
		});
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

