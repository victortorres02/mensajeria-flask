import api_call from "./api_call.js";

export async function get_self_user_data() {
	return api_call("/api/web/get_profile_data", new Object());
}

export async function get_self_user_id() {
	return get_self_user_data()
	.then(profile_data => profile_data.user_id);
}
