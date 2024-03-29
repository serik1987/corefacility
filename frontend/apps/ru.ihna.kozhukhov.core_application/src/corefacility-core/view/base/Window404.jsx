import {translate as t} from 'corefacility-base/utils';

import CoreWindow from './CoreWindow';
import CoreWindowHeader from './CoreWindowHeader';


export default class Window404 extends CoreWindow{

	/** Returns false because window 404 is not reloadable.
	 */
	get reloadable(){
		return false;
	}

	get browserTitle(){
		return t("Not Found");
	}

	renderControls(){
		return null;
	}

	renderContent(){
		return  (<CoreWindowHeader header={t('The requested resource was not found')}>
			<p><i>{t('May be, the resource has been deleted, moved permanently or never existed.')}</i></p>
		</CoreWindowHeader>);
	}

}