import api_call from "./api_call.js";

export default class ContactWatcher {
	constructor() {
		this.contacts = [];
	}
	async do_sync() {
		let api_args = Object();
        api_args.chat_type

		return api_call('/api/web/list_contacts', api_args)
		.then(json_res => {
			this.add_contacts(json_res.contacts);
		});
	}
	add_contacts(contacts) {
		let new_contacts = contacts.filter(contact => this.contacts.filter(cont => cont.id == contact.id).length == 0);
		new_contacts.forEach(chat => console.log("Nuevo chat: ", chat));
		new_contacts.forEach(chat => this.contacts.push(chat));
	}
}
