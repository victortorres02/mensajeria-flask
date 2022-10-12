import api_call from "./api_call.js";

export async function get_self_user_id() {
	return api_call("/api/web/get_profile_data", new Object())
	.then(json_res => json_res.user_id);
}

