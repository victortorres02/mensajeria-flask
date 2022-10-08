
export default class ChatRenderer {
	constructor(message_area) {
		this.message_area = message_area;
		this.rendered_messages = new Map();
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
		let elem = document.createElement("p");
		elem.classList.add("text-message");
		elem.classList.add("px-2");
		elem.appendChild(document.createTextNode(message.message_data));
		message_area.appendChild(elem);
		this.render_message.set(message, elem);
	}
}

