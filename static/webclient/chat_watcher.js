import api_call from "./api_call.js";

export default class ChatWatcher {
	constructor() {
		this.listed_chats = [];
	}
	async do_sync() {
		let api_args = Object();

		return api_call('/api/web/list_chats', api_args)
		.then(json_res => {
			this.add_listed_chats(json_res.chats);
		});
	}
	add_listed_chats(listed_chats) {
		let new_chats = listed_chats.filter(chat => this.listed_chats.filter(ch => ch.id == chat.id).length == 0);
		new_chats.forEach(chat => console.log("Nuevo chat: ", chat));
		new_chats.forEach(chat => this.listed_chats.push(chat));
	}
}

