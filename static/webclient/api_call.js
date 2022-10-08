
export default function api_call(url, api_args) {
	return fetch(url, {
		method: 'POST',
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(api_args)
	})
	.then(response => {
		if (!response.ok)
			throw new Error("Servidor regresó un error HTTP");
		return response;
	})
	.then(response => response.json())
	.then(json_res => {
		if (json_res.status == "error")
			throw new Error((json_res.reason !== undefined)?json_res.reason:"Servidor regresó un error");
		return json_res;
	});
}

