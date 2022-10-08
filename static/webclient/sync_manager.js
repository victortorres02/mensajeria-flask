
class AsyncObj {
	constructor(sync_manager, obj, sync_period) {
		this.sync_manager = sync_manager;
		this.obj = obj;
		this.sync_period = sync_period;
		
		this.before_hooks = [];
		this.after_hooks = [];

		console.log("New async obj: ", obj, sync_period);
		this.timeout = setTimeout(this.async_loop.bind(this), sync_period);
	}
	async async_loop() {
		if (this.sync_manager.async_objs.includes(this)) {
			this.before_hooks.forEach(hook => hook(this));
			await this.obj.do_sync();
			this.after_hooks.forEach(hook => hook(this));
			this.timeout = setTimeout(this.async_loop.bind(this), this.sync_period);
		}
	}
}

export default class SyncManager {
	constructor() {
		this.chats = [];
		this.async_objs = [];
	}
	add_chat(chat) {
		this.chats.push(chat);
		return this.add_async_obj(chat, 250);
	}
	add_async_obj(obj, sync_period) {
		let async_obj = new AsyncObj(this, obj, sync_period);
		this.async_objs.push(async_obj);
		return async_obj;
	}
	get_async_obj(obj) {
		let vals = this.async_obj.filter(async_obj => async_obj.obj == obj);
		if (vals.length == 0)
			return undefined;
		else
			return vals[0];
	}
}

