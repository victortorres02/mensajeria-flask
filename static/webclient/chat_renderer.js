
export default class ChatRenderer {
	constructor(message_area) {
		this.message_area = message_area;
		this.rendered_messages = new Map();
	}
	set_self_user_id(user_id) {
		if (user_id.then === undefined)
			this.user_id = user_id;
		else
			user_id.then(id => {this.user_id = id;});
	}
	check_chat_update(async_obj) {
		let chat = async_obj.obj;
		let new_messages = chat.retrieved_messages.filter(message => !this.rendered_messages.has(message));
		if (new_messages.length == 0)
			return;
		console.log("Mensajes a mostrar", new_messages);
		new_messages.forEach(this.render_message.bind(this));
	}
	render_message(message) {
		let elem = document.createElement("div");
		elem.classList.add("message-container");

		let message_elem = document.createElement("p");
		message_elem.appendChild(document.createTextNode(message.message_data));
		message_elem.classList.add("text-message");
		message_elem.classList.add("px-2");
		if (message.sender_id == this.user_id)
			message_elem.classList.add("self-message");

		elem.appendChild(message_elem);
		this.message_area.appendChild(elem);
		this.rendered_messages.set(message, elem);
	}
	clear() {
		for (let child of Array.from(this.message_area.children))
			this.message_area.removeChild(child);
		this.rendered_messages = new Map();
	}
}

