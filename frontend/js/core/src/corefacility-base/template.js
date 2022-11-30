import {translate as t} from './utils';

function tpl_base_document(html_code){
	let win = window.open();
	win.document.body.innerHTML = html_code;
	win.document.head.innerHTML = `
	<title>Corefacility</title>
	<meta charset="utf-8"/>
	<link rel="icon" href="/static/favicon.ico" />
`;
	win.print();
}

export function tpl_password(login, password){
	tpl_base_document(`
		<p>${t("To get access to the corefacility use the following credentials:")}</p>
		<p>URL: ${window.origin}</p>
		<p>${t("Login")}: ${login}</p>
		<p>${t("Password")}: ${password}</p>
	`);
}