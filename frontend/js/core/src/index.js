import {createRoot} from 'react-dom/client';
import i18next from 'i18next'
import {initReactI18next} from 'react-i18next';
import CoreApp from './view/CoreApp.jsx';


let backendLang = window.SETTINGS.lang;
let root = createRoot(document.getElementById("root"));
let app = <CoreApp/>;


fetch(`/static/core/translation.${backendLang}.json`)
	.then(response => response.json())
	.then(result => {
		i18next
			.use(initReactI18next)
			.init({
				resources: {
					[backendLang]: {
						translation: result,
					}
				},
				lng: backendLang,
				fallbackLng: 'en',
		});
	})
	.catch(error => {
		console.error(error);
		console.error("Failed to fetch language file. The language module will be switched off");
	})
	.finally(() => {
		root.render(app);
	});
