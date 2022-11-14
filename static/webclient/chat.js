import api_call from "./api_call.js";

const ChatType = {
	personal: 1,
	group: 2,
};

class Chat {
	//TODO: Jalar la información directamente desde el JSON
	constructor(chat_id, name, type, members) {
		this.id = chat_id;
		this.name = name;
		this.type = type;
		this.members = members;
		this.listed_messages = [];
		this.retrieved_messages = [];
	}
	set_self_user_id(user_id) {
		if (user_id.then === undefined)
			this.self_user_id = user_id;
		else
			user_id.then(id => {this.self_user_id = id;});
	}
	get_name() {
		if (this.name === undefined || this.name === null)
		{
			return this.members.filter(user => user.id != this.self_user_id).map(user => user.username).join(", ");
		}
		else
		{
			return this.name;
		}
	}
	async do_sync() {
		let api_args = Object();
		api_args.chat_id = this.id;

		return api_call("/api/web/list_messages", api_args)
		.then(json_res => {
			this.add_listed_messages(json_res.messages);
			let pending_messages = this.get_pending_retrieve_messages();

			if (pending_messages.length == 0)
				return;
			console.log("Nuevos mensajes: ", pending_messages);

			let api_args = Object();
			api_args.chat_id = this.id;
			api_args.message_ids = pending_messages.map(message => message.id);

			return api_call("/api/web/retrieve_messages", api_args)
			.then(json_res => {
				console.log("Mensajes recibidos: ", json_res.messages);
				this.add_retrieved_messages(json_res.messages);
			})
			.catch (err => console.error("Error al obtener los mensajes de ", this.id, err));
		})
		.catch (err => console.error("Error al listar los mensajes de ", this.id, err));
	}
	add_listed_messages(listed_messages) {
		let messages = listed_messages.filter(message => this.retrieved_messages.filter(msg => msg.id == message.id).length == 0);
		messages.forEach(message => console.log("Mensaje recibido: ", message));
		messages.forEach(message => this.listed_messages.push(message));
	}
	get_pending_retrieve_messages() {
		return this.listed_messages;
	}
	add_retrieved_messages(messages) {
		messages.filter(message => {
			if (message.status == "error") {
				console.error("Error al obtener el mensaje", message.id, message.reason);
				return false;
			}
			else
				return true;
		});
		messages.forEach(message => {
			let eq_id_list = this.listed_messages.filter(msg => msg.id == message.id);
			if (eq_id_list.length != 0) {
				let index = this.listed_messages.indexOf(eq_id_list[0]);
				this.listed_messages.splice(index, 1);
			}
			console.log("Mensaje recibido: ", message);
			this.retrieved_messages.push(message);
		});
	}
}

export {Chat as default, ChatType};
