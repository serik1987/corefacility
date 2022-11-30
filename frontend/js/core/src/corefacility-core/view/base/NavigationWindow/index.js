import {NotImplementedError} from 'corefacility-base/exceptions/model';
import {ReactComponent as NavigationArrow} from 'corefacility-base/shared-view/icons/chevron.svg';

import CoreWindow from '../CoreWindow';
import styles from './style.module.css';


export default class NavigationWindow extends CoreWindow{

	/**	Renders navigation bar
	 * 	@return {React.Component} the rendered component
	 */
	renderControls(){
		const navigationItems = this.renderNavigationItems();
		let navigationItemIndex = 0;

		return (
			<ul className={styles.navigation_panel}>
				{navigationItems.map(navigationItem => {
					return (
						<li key={navigationItemIndex++} className={styles.navigation_item_wrapper}>
							{navigationItem}
							{navigationItemIndex !== navigationItems.length - 1 && (
								<div className={styles.navigation_item_transition}>
									<NavigationArrow/>
								</div>
							)}
						</li>
					);
				})}
			</ul>
		);
	}

	/** Renders natvigation items
	 * 	@return {array of React.Component} array Hyperlink, p and any
	 * 		other React components: one component means one navigation item
	 */
	renderNavigationItems(){
		throw new NotImplementedError("renderNavigationItems");
	}

}